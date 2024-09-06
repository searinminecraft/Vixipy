from flask import Flask, Response, g, make_response, render_template, request
import traceback

from requests import ConnectionError

from . import api
from . import cfg

from .core.landing import getLandingPage, getLandingRanked
from .core.user import getUser

from .routes import settings, proxy, devtest, artworks, discover, userAction, users, tag


def create_app():
    app = Flask(__name__)

    app.register_blueprint(proxy.proxy)
    app.register_blueprint(settings.settings)
    app.register_blueprint(artworks.artworks)
    app.register_blueprint(devtest.devtest)
    app.register_blueprint(discover.discover)
    app.register_blueprint(userAction.userAction)
    app.register_blueprint(users.users)
    app.register_blueprint(tag.tag)

    @app.errorhandler(api.PixivError)
    def handlePxError(e):
        resp = make_response(render_template("error.html", error=e, pixivError=True))
        return resp, 500

    @app.errorhandler(404)
    def notFound(e):
        return "404 not found", 404

    @app.errorhandler(Exception)
    def handleError(e):
        traceback.print_exc()
        resp = make_response(
            render_template("error.html", error=f"{e.__class__.__name__}: {e}")
        )
        return resp, 500

    @app.errorhandler(ConnectionError)
    def handleConnectionError(e):
        resp = make_response(
            render_template(
                "error.html",
                error=f"Unable to complete request. Check instance's network connection or contact the instance administrator if the issue persists.",
            )
        )
        return resp, 500

    @app.before_request
    def beforeReq():

        route = request.full_path.split("/")[1]

        if route in ("static", "proxy", "robots.txt", "favicon.ico"):
            return

        g.version = "1.2"
        g.instanceName = cfg.PxInstanceName

        g.userPxSession = request.cookies.get("PyXivSession")
        g.userPxCSRF = request.cookies.get("PyXivCSRF")
        g.userProxyServer = request.cookies.get("PyXivProxy", "")

        if not g.userPxSession and not g.userPxCSRF:
            g.isAuthorized = False

            if route in ("self",):
                return render_template("unauthorized.html"), 401

        else:
            g.isAuthorized = True

            g.userdata = getUser(g.userPxSession.split("_")[0])

    @app.route("/")
    def home():

        if g.isAuthorized:
            mode = request.args.get("mode", "all")
            data = getLandingPage(mode)
            return render_template("index.html", data=data)

        data = getLandingRanked()
        return render_template("index.html", data=data)

    @app.route("/robots.txt")
    def robotsTxt():
        print("Possible crawler:", request.user_agent, "accessed the robots.txt")
        return (
            "User-Agent: *\nDisallow: /\nDisallow: /proxy\nAllow: /artworks/*\nAllow: /users/*",
            {"Content-Type": "text/plain"},
        )

    @app.route("/about")
    def about():

        return render_template("about.html")

    return app
