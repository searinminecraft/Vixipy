from flask import Flask, Response, g, make_response, render_template, request, flash
from flask_babel import Babel
import traceback

from requests import ConnectionError

from . import api
from . import cfg

from .core.landing import getLandingPage, getLandingRanked
from .core.user import getUser

from .classes import User

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


def create_app():
    app = Flask(__name__)
    app.secret_key = cfg.PyXivSecret
    app.config["authless"] = cfg.AuthlessMode
    app.config["languages"] = ["en", "fil", "zh_Hans"]
    app.config["proxy-servers"] = (
            "https://i.pixiv.re",
            "https://pixiv.darkness.services",
            "https://pximg.exozy.me",
            "https://pximg.cocomi.eu.org/",
            "https://i.suimoe.com/",
            "https://i.yuki.sh/",
            "https://pximg.obfs.dev/",
            "https://pi.169889.xyz/",
            "https://pixiv.tatakai.top/",
            "https://pixiv.ducks.party/"
    )

    def getLocale():
        if g.get("lang") and g.lang != "" :
            return g.lang

        return request.accept_languages.best_match(app.config['languages']) 

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
            "ids": (701, 702, 703, 704, 705, 706, 707, 708, 709, 710)
        }
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

    @app.errorhandler(api.PixivError)
    def handlePxError(e):
        resp = make_response(render_template("error.html", error=e, pixivError=True))
        return resp, 500

    @app.errorhandler(404)
    def notFound(e):
        return "404 not found", 404

    @app.errorhandler(Exception)
    def handleInternalError(e):
        traceback.print_exc()
        resp = make_response(
            render_template(
                "500.html", error=e, info=traceback.format_exc(), isDebug=app.debug
            )
        )
        return resp, 500

    @app.errorhandler(ConnectionError)
    def handleConnectionError(e):
        return handleInternalError(e)

    @app.before_request
    def beforeReq():

        route = request.full_path.split("/")[1]

        if route in ("static", "proxy", "robots.txt", "favicon.ico"):
            return

        g.version = "1.9"
        g.instanceName = cfg.PxInstanceName
        g.lang = request.cookies.get("lang", "en")

        g.userPxSession = request.cookies.get("PyXivSession")
        g.userPxCSRF = request.cookies.get("PyXivCSRF")
        g.userProxyServer = request.cookies.get("PyXivProxy", "")

        if not g.userPxSession and not g.userPxCSRF:
            g.isAuthorized = False

            if route in ("self",):
                return render_template("unauthorized.html"), 401

        else:
            g.isAuthorized = True

            try:
                g.userdata: User = getUser(g.userPxSession.split("_")[0])
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

            g.notificationCount = api.pixivReq(
                "/rpc/notify_count.php?op=count_unread",
                {"Referer": "https://www.pixiv.net/en"},
            )["popboard"]
            g.hasNotifications = g.notificationCount > 0

    @app.after_request
    def afterReq(r):
        if g.get("invalidSession", False):

            r.delete_cookie("PyXivCSRF")
            r.delete_cookie("PyXivSession")

        return r

    @app.route("/")
    def home():

        if g.isAuthorized:
            mode = request.args.get("mode", "all")
            data = getLandingPage(mode)
            return render_template(
                "index.html", data=data, rankingData=getLandingRanked()
            )

        data = getLandingRanked()
        return render_template("index.html", data=data)

    @app.route("/robots.txt")
    def robotsTxt():
        print("Possible crawler:", request.user_agent, "accessed the robots.txt")
        return (
            "\nCrawl-delay: 15\nUser-Agent: *\nDisallow: /\nDisallow: /proxy\nAllow: /artworks/*\nDisallow: /artworks/*/comments\nAllow: /users/*",
            {"Content-Type": "text/plain"},
        )

    @app.route("/about")
    def about():

        return render_template("settings/about.html")

    @app.route("/jump.php")
    def pixivRedir():
        return render_template("leave.html", dest=list(request.args.keys())[0])

    return app
