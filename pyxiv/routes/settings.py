from flask import (
    Blueprint,
    make_response,
    redirect,
    request,
    g,
    render_template,
    url_for,
)

import re
import requests

from .. import api
from .. import cfg

from ..core.user import getUserSettingsState

settings = Blueprint("settings", __name__, url_prefix="/settings")

COOKIE_MAXAGE = 60 * 60 * 24 * 7  #  7 days


@settings.before_request
def getUserState():

    g.userState = getUserSettingsState()

@settings.route("/")
def settingsIndex():
    return render_template("settings/pyxivSettings.html")

@settings.route("/<ep>")
def mainSettings(ep):
    match ep:
        case "account":
            return render_template("settings/account.html")
        case "viewing":
            return render_template("settings/viewing.html")
        case "notifications":
            c = api.getUserSettings()["body"]
            
            notificationSettingsItems = {}
            mailSettingsItems = {}

            for ns in c["notifications"]["items"]:
                if ns["type"] != "setting":
                    continue

                notificationSettingsItems[ns["settingKey"]] = {"label": ns["label"], "disabled": ns["disabled"], "value": ns["value"]}

            for ms in c["mail"]["items"]:
                if ms["type"] != "setting":
                    continue

                mailSettingsItems[ms["settingKey"]] = {"label": ms["label"], "disabled": ms["disabled"], "value": ms["value"]}

            return render_template("settings/notifications.html", nsItems=notificationSettingsItems, msItems=mailSettingsItems)
        case "about":
            return render_template("about")
        case "premium":
            #  :trolley:
            return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=303)
        case _:
            return render_template("error.html", error="Invalid endpoint: " + ep), 404

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

        resp = make_response(redirect(url_for("settings.mainSettings", ep="account"), code=303))
        resp.set_cookie(
            "PyXivSession", f["token"], max_age=COOKIE_MAXAGE, httponly=True
        )
        resp.set_cookie("PyXivCSRF", csrf, max_age=COOKIE_MAXAGE, httponly=True)
        return resp
    else:
        return render_template("error.html", error="No token supplied."), 400


@settings.route("/logout")
def logout():

    resp = make_response(redirect("/", code=303))
    resp.delete_cookie("PyXivSession")
    resp.delete_cookie("PyXivCSRF")
    return resp


@settings.post("/imgproxy")
def setImgProxy():

    f = request.form

    resp = make_response(redirect(url_for("settings.settingsIndex"), code=303))
    resp.set_cookie(
        "PyXivProxy", f["image-proxy"], max_age=COOKIE_MAXAGE, httponly=True
    )
    return resp


@settings.post("/setDisplayPrefs")
def setPreferences():
    hideAIPref = request.form.get("hideAI")
    hideR18Pref = request.form.get("hideR18")

    resp = make_response(redirect(url_for("settings.mainSettings", ep="viewing"), code=303))

    resp.delete_cookie("PyXivHideAI")
    resp.delete_cookie("PyXivHideR18")
    resp.delete_cookie("PyXivHideR18G")

    for pref in request.form:
        match pref:
            case "hideAI":
                resp.set_cookie(
                    "PyXivHideAI", "1", max_age=COOKIE_MAXAGE, httponly=True
                )
            case "hideR18":
                resp.set_cookie(
                    "PyXivHideR18", "1", max_age=COOKIE_MAXAGE, httponly=True
                )
            case "hideR18G":
                resp.set_cookie(
                    "PyXivHideR18G", "1", max_age=COOKIE_MAXAGE, httponly=True
                )
            case _:
                pass

    return resp
