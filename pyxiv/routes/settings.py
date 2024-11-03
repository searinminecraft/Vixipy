from flask import (
    Blueprint,
    make_response,
    redirect,
    request,
    g,
    render_template,
    url_for,
    flash,
)

import re
import requests

from .. import api
from .. import cfg

from ..core.user import getUserSettingsState

settings = Blueprint("settings", __name__, url_prefix="/settings")

COOKIE_MAXAGE = 2592000


@settings.before_request
def getUserState():
    if cfg.AuthlessMode:
        if g.isAuthorized:
            g.userState = getUserSettingsState()
        pass
    else:
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
            if not g.isAuthorized:
                return render_template("unauthorized.html")

            c = api.getUserSettings()["body"]

            notificationSettingsItems = {}
            mailSettingsItems = {}

            for ns in c["notifications"]["items"]:
                if ns["type"] != "setting":
                    continue

                notificationSettingsItems[ns["settingKey"]] = {
                    "label": ns["label"],
                    "disabled": ns["disabled"],
                    "value": ns["value"],
                }

            for ms in c["mail"]["items"]:
                if ms["type"] != "setting":
                    continue

                mailSettingsItems[ms["settingKey"]] = {
                    "label": ms["label"],
                    "disabled": ms["disabled"],
                    "value": ms["value"],
                }

            return render_template(
                "settings/notifications.html",
                nsItems=notificationSettingsItems,
                msItems=mailSettingsItems,
            )
        case "about":
            return render_template("about")
        case "license":
            return render_template("settings/license.html")
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
            flash(f"Cannot use token: {e}", "error")
            return redirect(url_for("settings.mainSettings", ep="account"))

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
            flash(f"Cannot use token. pixiv returned code {req.status_code}", "error")
            return redirect(url_for("settings.mainSettings", ep="account"))

        r = re.search(csrfMatch, req.text)

        try:
            csrf = r.group(1)
        except IndexError:
            flash(f"Cannot use token: Couldn't obtain CSRF token.", "error")
            return redirect(url_for("settings.settingsMain", ep="account"))

        resp = make_response(
            redirect(url_for("settings.mainSettings", ep="account"), code=303)
        )
        resp.set_cookie(
            "PyXivSession", f["token"], max_age=COOKIE_MAXAGE, httponly=True
        )
        resp.set_cookie("PyXivCSRF", csrf, max_age=COOKIE_MAXAGE, httponly=True)
        return resp
    else:
        flash("No token was supplied.", "error")
        return redirect(url_for("settings.mainSettings"))


@settings.route("/logout")
def logout():

    resp = make_response(redirect("/", code=303))
    resp.delete_cookie("PyXivSession")
    resp.delete_cookie("PyXivCSRF")
    flash("You have successfully terminated the session. Goodbye!")
    return resp


@settings.post("/imgproxy")
def setImgProxy():

    f = request.form

    notAllowedIps = (
        "0.",
        "10.",
        "100.",
        "127.",
        "169.254.",
        "172.16.",
        "172.17.",
        "172.18.",
        "172.19.",
        "172.20.",
        "172.21.",
        "172.22.",
        "172.23.",
        "172.24.",
        "172.25.",
        "172.26.",
        "172.27.",
        "172.28.",
        "172.29.",
        "172.30.",
        "172.31.",
        "192.0.0.",
        "192.88.",
        "192.168.",
        "198.18." "198.19.",
        "198.51.100.",
        "203.0.113.",
    )

    i = f["image-proxy"].lower().replace("https://", "").replace("http://", "")

    if any([i.startswith(x) for x in notAllowedIps]) or i in (
        "localhost",
        "i.pximg.net",
    ):
        flash(f"This address is not allowed: {i}", "error")
        return redirect(url_for("settings.settingsIndex"), code=303)

    if i != "":
        try:
            req = requests.get(
                f"http://{i}",
                headers={"User-Agent": "PyXiv-ProxyServerCheck"},
                allow_redirects=True,
            )
            if not req.text.__contains__("imgaz.pixiv.net"):
                flash(
                    "The URL specified does not seem to be a pixiv image proxy server.",
                    "error",
                )
                return redirect(url_for("settings.settingsIndex"), code=303)
        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for("settings.settingsIndex"), code=303)

    resp = make_response(redirect(url_for("settings.settingsIndex"), code=303))
    resp.set_cookie(
        "PyXivProxy", f["image-proxy"], max_age=COOKIE_MAXAGE, httponly=True
    )
    return resp


@settings.post("/setDisplayPrefs")
def setPreferences():
    hideAIPref = request.form.get("hideAI")
    hideR18Pref = request.form.get("hideR18")

    resp = make_response(
        redirect(url_for("settings.mainSettings", ep="viewing"), code=303)
    )

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
