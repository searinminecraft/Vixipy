from quart import (
    Quart,
    g,
    make_response,
    render_template,
    request,
    redirect,
    flash,
    abort,
    send_from_directory,
)
from aiohttp import ClientSession, DummyCookieJar
from urllib.parse import urlparse
from asyncio import gather
import traceback
import logging
import os

from quart_babel import Babel, _
from quart_rate_limiter import RateLimiter

import pyxivision

from . import api
from . import cfg

from .core.landing import getLandingPage, getLandingRanked
from .core.user import getUser

from .classes import User, MemcacheStore

from .routes import (
    settings,
    proxy,
    devtest,
    artworks,
    discover,
    userAction,
    users,
    tag,
    newest,
    pixivision,
    ranking,
)

log = logging.getLogger()


def create_app():
    app = Quart(__name__, static_folder=None)
    store = MemcacheStore()
    limiter = RateLimiter(app, store=store)

    if int(os.environ.get("PYXIV_DEBUG", 0)) == 1:
        logLevel = logging.DEBUG
    else:
        logLevel = logging.INFO

    logging.basicConfig(
        level=logLevel,
        format=("[%(asctime)s]: %(name)s %(levelname)s: %(message)s"),
        style="%",
    )

    logging.getLogger("urllib3.connectionpool").setLevel(logging.ERROR)
    # logging.getLogger("werkzeug").setLevel(logging.ERROR)

    app.secret_key = cfg.PyXivSecret
    app.config["QUART_RATE_LIMITER_ENABLED"] = cfg.RateLimitsEnabled
    app.config["authless"] = cfg.AuthlessMode
    app.config["nor18"] = cfg.NoR18
    app.config["languages"] = ["en", "fil", "zh_Hans", "ru"]
    app.config["proxy-servers"] = (
        "https://i.pixiv.re",
        "https://pixiv.darkness.services",
        "https://pximg.cocomi.eu.org/",
        "https://i.suimoe.com/",
        "https://i.yuki.sh/",
        "https://pximg.obfs.dev/",
        "https://pi.169889.xyz/",
        "https://pixiv.tatakai.top/",
        "https://pixiv.ducks.party/",
    )

    def getLocale():
        if g.get("lang") and g.lang != "":
            log.debug("current g.lang %s", g.lang)
            return g.lang

        l = request.accept_languages.best_match(app.config["languages"])
        log.debug("matched lang %s", l)
        return l

    babel = Babel(app, locale_selector=getLocale)

    # https://www.pixiv.net/ajax/settings/self
    app.config["stamps"] = {
        "hakuzau": {
            "name": "ハクゾウ",
            "ids": (301, 302, 303, 304, 305, 306, 307, 308, 309, 310),
        },
        "kitsune": {
            "name": "キツネ",
            "ids": (401, 402, 403, 404, 405, 406, 407, 408, 409, 410),
        },
        "moemusume": {
            "name": "萌え娘",
            "ids": (201, 202, 203, 204, 205, 206, 207, 208, 209, 210),
        },
        "dokurochan": {
            "name": "どくろちゃん",
            "ids": (101, 102, 103, 104, 105, 106, 107, 108, 109, 110),
        },
        "None": {
            "name": "None",
            "ids": (701, 702, 703, 704, 705, 706, 707, 708, 709, 710),
        },
    }

    app.config["emojis"] = {
        "normal": 101,
        "surprise": 102,
        "serious": 103,
        "heaven": 104,
        "happy": 105,
        "excited": 106,
        "sing": 107,
        "cry": 108,
        "normal2": 201,
        "shame2": 202,
        "love2": 203,
        "interesting2": 204,
        "blush2": 205,
        "fire2": 206,
        "angry2": 207,
        "shine2": 208,
        "panic2": 209,
        "normal3": 301,
        "satisfaction3": 302,
        "surprise3": 303,
        "smile3": 304,
        "shock3": 305,
        "gaze3": 306,
        "wink3": 307,
        "happy3": 308,
        "excited3": 309,
        "love3": 310,
        "normal4": 401,
        "surprise4": 402,
        "serious4": 403,
        "love4": 404,
        "shine4": 405,
        "sweat4": 406,
        "shame4": 407,
        "sleep4": 408,
        # does pixiv really have to have their own emojis
        # even though theyre in the official unicode spec?
        "heart": 501,
        "teardrop": 502,
        "star": 503,
    }

    app.register_blueprint(proxy.proxy)
    app.register_blueprint(settings.settings)
    app.register_blueprint(artworks.artworks)
    app.register_blueprint(devtest.devtest)
    app.register_blueprint(discover.discover)
    app.register_blueprint(userAction.userAction)
    app.register_blueprint(users.users)
    app.register_blueprint(tag.tag)
    app.register_blueprint(newest.newest)
    app.register_blueprint(pixivision.pixivision)
    app.register_blueprint(ranking.rankings)

    @app.before_serving
    async def startup():

        user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0"
        )

        app.proxySession = ClientSession(connector_owner=False)
        app.pixivApi = ClientSession(
            "https://www.pixiv.net",
            headers={"User-Agent": user_agent, "Referer": "https://www.pixiv.net"},
            connector_owner=False,
            cookie_jar=DummyCookieJar(),
        )

        app.pyxivision = pyxivision.Client()

    @app.after_serving
    async def shutdown():
        await app.pixivApi.close()
        await app.proxySession.close()
        await app.pyxivision.close()
        try:  # just so it doesn't scream if it fails
            os.remove("pyxiv.running")
        except:
            return
        log.info("Shutting down. Goodbye!")  # only log once

    @app.errorhandler(429)
    async def tooManyRequests(e):
        log.warn(
            "Remote %s (%s) has been rate limited.",
            request.user_agent,
            request.remote_addr,
        )
        return "Too many requests\n", 429

    @app.errorhandler(api.PixivError)
    async def handlePxError(e):
        resp = await make_response(
            await render_template(
                "error.html",
                errortitle=_("pixiv Error!"),
                errordesc=_(
                    "pixiv returned an error trying to request data: <code>%(error)s</code>",
                    error=e if str(e) != "" else _("Unspecified error"),
                ),
            ),
        )
        return resp, 500

    @app.errorhandler(404)
    async def notFound(e):
        return (
            await render_template(
                "error.html",
                errortitle=_("Not found"),
                errordesc=_("The requested resource could not be found."),
            ),
            404,
        )

    @app.errorhandler(400)
    async def badRequest(e):
        return (
            await render_template(
                "error.html",
                errortitle=_("Bad request"),
                errordesc=_("The server could not satisfy the request."),
            ),
            400,
        )

    @app.errorhandler(403)
    async def handleForbidden(e):
        return (
            await render_template(
                "error.html",
                errortitle=_("Forbidden"),
                errordesc=_("You do not have permission to access this page."),
            ),
            403,
        )

    @app.errorhandler(401)
    async def handleUnauthorized(e):
        return (
            await render_template(
                "error.html",
                errortitle=_("Unauthorized"),
                errordesc=_(
                    _(
                        "Provide your pixiv PHPSESSID in settings to perform this action."
                    )
                ),
            ),
            401,
        )

    @app.errorhandler(405)
    async def handleMethodNotAllowed(e):
        return (
            await render_template(
                "error.html",
                errortitle=_("Method Not Allowed"),
                errordesc=_("This method is not allowed for this endpoint"),
            ),
            405,
        )

    @app.errorhandler(Exception)
    async def handleInternalError(e):
        log.exception("Error", exc_info=e)
        resp = await make_response(
            await render_template("500.html", error=e, info=traceback.format_exc())
        )
        return resp, 500

    @app.before_request
    async def beforeReq():

        route = request.full_path.split("/")[1]

        if route in ("static", "proxy", "robots.txt", "favicon.ico"):
            return

        if request.path.split("/")[1] == "en":
            p = request.path.replace("/en", "")
            if p == "":
                p = "/"
            return redirect(p, code=308)

        g.rev = cfg.GitRev
        g.repo = cfg.GitRepo
        g.version = cfg.Version + "+" + g.rev
        g.instanceName = cfg.PxInstanceName
        g.lang = request.cookies.get("lang")

        g.userPxSession = request.cookies.get("PyXivSession")
        g.userPxCSRF = request.cookies.get("PyXivCSRF")
        g.userProxyServer = request.cookies.get("PyXivProxy", "")

        if (not g.userPxSession and not g.userPxCSRF) or g.userPxSession == "":
            g.isAuthorized = False

            if route in ("self",):
                abort(401)

        else:
            g.isAuthorized = True

            try:
                notifications, userdata = await gather(
                    api.pixivReq(
                        "get",
                        "/rpc/notify_count.php?op=count_unread",
                        {"Referer": "https://www.pixiv.net/en"},
                    ),
                    getUser(g.userPxSession.split("_")[0], False),
                )

                g.notificationCount = notifications["popboard"]
                g.userdata = userdata
                g.hasNotifications = g.notificationCount > 0
                g.isPremium = g.userdata.premium
            except api.PixivError:
                flash(
                    "Token is not valid anymore (logged out?), so you were signed out.",
                    "error",
                )
                g.userdata = None
                g.isAuthorized = False
                del g.userPxSession
                del g.userPxCSRF

                g.invalidSession = True

    @app.after_request
    def afterReq(r):
        p = urlparse(g.get("userProxyServer")).hostname or ""
        # from https://codeberg.org/PixivFE/PixivFE/src/commit/665503fcc92034384e8b0346cd2fb8e4b419db7b/server/middleware/csp.go#L44
        # vixipy is still not a pixivfe competitor as always
        r.headers["Content-Security-Policy"] = (
            "base-uri 'self'; default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: %s; media-src 'self' %s; font-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none';"
            % (p, p)
        )
        r.headers["X-Frame-Options"] = "DENY"
        if g.get("invalidSession", False):

            r.delete_cookie("PyXivCSRF")
            r.delete_cookie("PyXivSession")

        return r

    @app.route("/")
    async def home():

        if g.isAuthorized:
            mode = request.args.get("mode", "all")
            data, rdata = await gather(getLandingPage(mode), getLandingRanked())
            return await render_template("index.html", data=data, rankingData=rdata)

        data = await getLandingRanked()
        return await render_template("index.html", data=data)

    @app.route("/robots.txt")
    def robotsTxt():
        log.warning(
            "Possible crawler: %s (%s) accessed the robots.txt",
            request.user_agent,
            request.remote_addr,
        )
        return (
            "\nCrawl-delay: 15\nUser-Agent: *\nDisallow: /\nDisallow: /proxy\nAllow: /artworks/*\nDisallow: /artworks/*/comments\nAllow: /users/*",
            {"Content-Type": "text/plain"},
        )

    @app.route("/about")
    async def about():

        return await render_template("settings/about.html")

    @app.route("/jump.php")
    async def pixivRedir():
        if request.args.get("url"):
            # /jump.php?url=https://kita.codeberg.page
            dest = request.args["url"]
        else:
            # /jump.php?https://kita.codeberg.page
            dest = list(request.args.keys())[0]

        return await render_template("leave.html", dest=dest)

    @app.route("/static/<path:filename>")
    async def static(filename):
        if os.path.isfile(os.path.join("pyxiv/instance/", filename)):
            return await send_from_directory("pyxiv/instance", filename)

        return await send_from_directory("pyxiv/static", filename)

    return app
