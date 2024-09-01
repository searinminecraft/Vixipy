from flask import Flask, Response, g, make_response, render_template, request

import api

from routes.settings import settings
from routes.proxy import proxy

app = Flask(__name__)
app.register_blueprint(proxy)
app.register_blueprint(settings)

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

@app.errorhandler(Exception)
def handleError(e):
    resp = make_response(render_template("error.html", error=e))
    return resp, 500

@app.before_request
def getPxSession():
    g.userPxSession = request.cookies.get("PyXivSession")
    g.userPxCSRF = request.cookies.get("PyXivCSRF")

    if not g.userPxSession and not g.userPxCSRF:
        g.isAuthorized = False
    else:
        g.isAuthorized = True

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/authtest')
@authRequired
def authtest():
    return api.getLanding()
