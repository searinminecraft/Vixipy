from flask import (
    Blueprint,
    abort,
    make_response,
    redirect,
    request,
    g,
    render_template,
    url_for,
)

import re
import requests

import api
import cfg

settings = Blueprint("settings", __name__, url_prefix="/settings")


@settings.route("/")
def mainSettings():
    return render_template("settings.html")


@settings.post("/token")
def setSession():
    f = request.form

    csrfMatch = '"token":"([0-9a-f]+)"'

    if f.get("token") and f.get("token") != "":

        g.userPxSession = f["token"]

        try:
            api.getLatestFromFollowing("all", 1)
        except api.PixivError as e:
            return (
                render_template(
                    "error.html", error=f"Cannot use token. Make sure it's valid. ({e})"
                ),
                400,
            )

        # If you're curious, this test URL is an illustration of Anna Yanami.
        # And don't worry its definitely not NSFW
        req = requests.get(
            "https://www.pixiv.net/en/artworks/121633055",
            headers={
                "Cookie": f"PHPSESSID={f['token']}",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
            },
        )

        if req.status_code != 200:
            return (
                render_template(
                    "error.html",
                    error="Cannot use token. Make sure it's valid. (failed at status code)",
                ),
                400,
            )

        r = re.search(csrfMatch, req.text)

        try:
            csrf = r.group(1)
        except IndexError:
            return (
                render_template(
                    "error.html",
                    error="Cannot use token. Make sure it's valid. (failed at: csrf)",
                ),
                400,
            )

        resp = make_response(redirect(url_for("settings.mainSettings"), code=303))
        resp.set_cookie("PyXivSession", f["token"])
        resp.set_cookie("PyXivCSRF", csrf)
        return resp
    else:
        return render_template("error.html", error="No token supplied."), 400


@settings.route("/logout")
def logout():

    resp = make_response(redirect(url_for("settings.mainSettings"), code=303))
    resp.delete_cookie("PyXivSession")
    resp.delete_cookie("PyXivCSRF")
    return resp
