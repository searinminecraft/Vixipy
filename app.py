from flask import Flask, Response, g, make_response, render_template, request

config = {
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 600
}

import api

from core.index import getLanding

from routes import settings
from routes import proxy

def create_app():
    app = Flask(__name__)

    app.config.from_mapping(config)

    app.register_blueprint(proxy.proxy)
    app.register_blueprint(settings.settings)

    def authRequired(f):
        def inner(*args, **kwargs):
            if not g.userPxSession and not g.userPxCSRF:
                return render_template("unauthorized.html"), 401

            return f(*args, **kwargs)

        return inner

    @app.errorhandler(api.PixivError)
    def handlePxError(e):
        resp = make_response(render_template("error.html", error=f"Pixiv: {e}"))
        return resp, 500

    @app.before_request
    def getPxSession():
        g.userPxSession = request.cookies.get("PyXivSession")
        g.userPxCSRF = request.cookies.get("PyXivCSRF")

        if not g.userPxSession and not g.userPxCSRF:
            g.isAuthorized = False
        else:
            g.isAuthorized = True

            userdata = api.getUserInfo(int(str(g.userPxSession).split("_")[0]))["body"]
            g.curruserId = userdata["userId"]
            g.currusername = userdata["name"]
            g.curruserimage = userdata["image"].replace("https://", "/proxy/")

    @app.route('/')
    def home():


        if g.isAuthorized:
            data = getLanding("all")
            return render_template("index.html", data=data)

    @app.route('/authtest')
    @authRequired
    def authtest():
        return api.getLanding()

    return app
