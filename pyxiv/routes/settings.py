from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    request,
    g,
    render_template,
    url_for,
    flash,
)
from flask_babel import _

import hashlib
import ipaddress
import re
import requests
import urllib.parse

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
            flash(_("Cannot use token: %(error)s", error=e), "error")
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
            flash(_("Cannot use token. pixiv returned code %(status)d", status=req.status_code), "error")
            return redirect(url_for("settings.mainSettings", ep="account"))

        r = re.search(csrfMatch, req.text)

        try:
            csrf = r.group(1)
        except IndexError:
            flash(_("Unable to extract CSRF"), "error")
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
        flash(_("No token was supplied."), "error")
        return redirect(url_for("settings.mainSettings"))


@settings.route("/logout")
def logout():

    resp = make_response(redirect("/", code=303))
    resp.delete_cookie("PyXivSession")
    resp.delete_cookie("PyXivCSRF")
    flash(_("You have successfully terminated the session. Goodbye!"))
    return resp


@settings.post("/imgproxy")
def setImgProxy():

    f = request.form

    integrity = "ba3a6764ecad4ab707a12884e4cc338589045d1e9f0dd12037b440fe81592981"

    p = urllib.parse.urlparse(f["image-proxy"])
    i = p.hostname
    scheme = p.scheme if p.scheme != '' else None

    if not scheme:
        flash(_("Please specify a URL scheme. Only http and https are accepted."), "error")
        return redirect(url_for("settings.settingsIndex"), code=303)

    if scheme not in ("http", "https"):
        flash(_("Invalid URL scheme: %(scheme)s. Only http and https are accepted.", scheme=scheme), "error")
        return redirect(url_for("settings.settingsIndex"), code=303)

    def denyIp():
        flash(_("This address is not allowed: %(addr)s", addr=i), "error")
        return redirect(url_for("settings.settingsIndex"), code=303)

    try:
        if ipaddress.ip_address(i).is_private:
            return denyIp()
    except ValueError:
        pass

    if i in ("localhost", "i.pximg.net"):
        return denyIp()

    finalUrl = f"{f['image-proxy']}/img-original/img/2020/02/04/22/43/08/79286093_p0.png"

    if i != "":
        try:
            req = requests.get(
                finalUrl,
                headers={"User-Agent": "PyXiv-ProxyServerCheck"},
                allow_redirects=True,
                timeout=5,
            )
            req.raise_for_status()
            isCloudflare = req.headers.get("server") == "cloudflare"

            if isCloudflare:
                flash( _("Note: the proxy server you have specified is behind Cloudflare. Images may possibly not load, and may breach your privacy.") )

            result = hashlib.sha256(req.content).hexdigest()

            if not result == integrity:
                flash(
                    _("Integrity check failed for image proxy test. Expected %(integrity)s, got %(result)s",
                      integrity=integrity,
                      result=result),
                    "error",
                )
                return redirect(url_for("settings.settingsIndex"), code=303)
        except requests.ConnectTimeout:
            flash(_("Timed out trying to check proxy server. It may be down."), "error")
            return redirect(url_for("settings.settingsIndex"), code=303)
        except Exception as e:
            flash(_("An error occured trying to check proxy server: %(error)s", error=e), "error")
            return redirect(url_for("settings.settingsIndex"), code=303)

    flash(_("Successfully set proxy server"))

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
