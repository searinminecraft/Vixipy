from quart import (
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
from quart_babel import _, refresh

import hashlib
import ipaddress
import re
import urllib.parse
import logging
from aiohttp import ClientSession
import logging

from .. import api
from .. import cfg

from ..core.user import getUserSettingsState

log = logging.getLogger("pyxiv.routes.settings")

settings = Blueprint("settings", __name__, url_prefix="/settings")

COOKIE_MAXAGE = 2592000


@settings.before_request
async def getUserState():
    if cfg.AuthlessMode:
        if g.isAuthorized:
            g.userState = await getUserSettingsState()
        pass
    else:
        g.userState = await getUserSettingsState()


@settings.route("/")
async def settingsIndex():
    return await render_template("settings/pyxivSettings.html")


@settings.route("/<ep>")
async def mainSettings(ep):
    match ep:
        case "account":
            return await render_template("settings/account.html")
        case "viewing":
            return await render_template("settings/viewing.html")
        case "notifications":
            if not g.isAuthorized:
                return await render_template("unauthorized.html")

            c = (await api.getUserSettings())["body"]

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

            return await render_template(
                "settings/notifications.html",
                nsItems=notificationSettingsItems,
                msItems=mailSettingsItems,
            )
        case "language":
            return await render_template(
                "settings/language.html", pv_lang=("en", "ja", "ko", "zh", "zh-tw")
            )
        case "about":
            return await render_template("about")
        case "license":
            return await render_template("settings/license.html")
        case "premium":
            #  :trolley:
            return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ", code=303)
        case _:
            return (
                await render_template(
                    "error.html", errordesc="Invalid endpoint: " + ep
                ),
                404,
            )


@settings.post("/token")
async def setSession():
    f = await request.form

    csrfMatch = '"token":"([0-9a-f]+)"'

    if f.get("token") and f.get("token") != "":

        g.userPxSession = f["token"]

        req = await current_app.pixivApi.get(
            "/en/artworks/99818936",
            headers={
                "Cookie": f"PHPSESSID={f['token']}",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            },
        )

        if req.status != 200:
            await flash(
                _(
                    "Cannot use token. pixiv returned code %(status)d",
                    status=req.status_code,
                ),
                "error",
            )
            return redirect(url_for("settings.mainSettings", ep="account"))

        r = re.search(csrfMatch, await req.text())

        try:
            csrf = r.group(1)
        except IndexError:
            await flash(_("Unable to extract CSRF"), "error")
            return redirect(url_for("settings.settingsMain", ep="account"))

        try:
            await api.pixivReq("get", "/ajax/user/extra")
        except api.PixivError as e:
            await flash(_("Cannot use token: %(error)s", error=e), "error")
            return redirect(url_for("settings.mainSettings", ep="account"))

        resp = await make_response(
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
async def logout():

    resp = await make_response(redirect("/", code=303))
    resp.delete_cookie("PyXivSession")
    resp.delete_cookie("PyXivCSRF")
    await flash(_("You have successfully terminated the session. Goodbye!"))
    return resp


@settings.post("/imgproxy")
async def setImgProxy():

    f = await request.form

    if f["image-proxy"] == "":
        await flash(_("Successfully set proxy server"))
        resp = await make_response(
            redirect(url_for("settings.settingsIndex"), code=303)
        )
        resp.set_cookie(
            "PyXivProxy", f["image-proxy"], max_age=COOKIE_MAXAGE, httponly=True
        )
        return resp

    integrity = "ba3a6764ecad4ab707a12884e4cc338589045d1e9f0dd12037b440fe81592981"

    p = urllib.parse.urlparse(f["image-proxy"])
    i = p.hostname
    scheme = p.scheme if p.scheme != "" else None

    if not scheme:
        await flash(
            _("Please specify a URL scheme. Only http and https are accepted."), "error"
        )
        return redirect(url_for("settings.settingsIndex"), code=303)

    if scheme not in ("http", "https"):
        await flash(
            _(
                "Invalid URL scheme: %(scheme)s. Only http and https are accepted.",
                scheme=scheme,
            ),
            "error",
        )
        return await redirect(url_for("settings.settingsIndex"), code=303)

    async def denyIp():
        await flash(_("This address is not allowed: %(addr)s", addr=i), "error")
        return redirect(url_for("settings.settingsIndex"), code=303)

    try:
        if ipaddress.ip_address(i):
            await flash(
                _(
                    "Due to limitations in Content-Security-Policy directives, IP Addresses are not supported as a proxy server."
                ),
                "error",
            )
            return redirect(url_for("settings.settingsIndex"), code=303)
    except ValueError:
        pass

    if i in ("localhost", "i.pximg.net"):
        return await denyIp()

    finalUrl = (
        f"{f['image-proxy']}/img-original/img/2020/02/04/22/43/08/79286093_p0.png"
    )

    if i != "":
        try:
            s = ClientSession()
            req = await s.get(
                finalUrl,
                headers={"User-Agent": "Vixipy-ProxyServerCheck"},
                allow_redirects=True,
                timeout=5,
            )
            req.raise_for_status()

            data = await req.content.read()
            await s.close()

            isCloudflare = req.headers.get("server") == "cloudflare"

            if isCloudflare:
                await flash(
                    _(
                        "Note: the proxy server you have specified is behind Cloudflare. Images may possibly not load, and may breach your privacy."
                    )
                )

            result = hashlib.sha256(data).hexdigest()

            if not result == integrity:
                await flash(
                    _(
                        "Integrity check failed for image proxy test. Expected %(integrity)s, got %(result)s",
                        integrity=integrity,
                        result=result,
                    ),
                    "error",
                )
                return redirect(url_for("settings.settingsIndex"), code=303)
        except Exception as e:
            log.exception("Failed to check proxy %s:", finalUrl)
            await flash(
                _("An error occured trying to check proxy server: %(error)s", error=e),
                "error",
            )
            return redirect(url_for("settings.settingsIndex"), code=303)

    await flash(_("Successfully set proxy server"))

    resp = await make_response(redirect(url_for("settings.settingsIndex"), code=303))
    resp.set_cookie(
        "PyXivProxy", f["image-proxy"], max_age=COOKIE_MAXAGE, httponly=True
    )
    return resp


@settings.post("/setDisplayPrefs")
async def setPreferences():
    form = await request.form
    hideAIPref = form.get("hideAI")
    hideR18Pref = form.get("hideR18")

    resp = await make_response(
        redirect(url_for("settings.mainSettings", ep="viewing"), code=303)
    )

    resp.delete_cookie("PyXivHideAI")
    resp.delete_cookie("PyXivHideR18")
    resp.delete_cookie("PyXivHideR18G")
    resp.delete_cookie("VixipyHideSensitive")

    for pref in form:
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
            case "hideSensitive":
                resp.set_cookie(
                    "VixipyHideSensitive", "1", max_age=COOKIE_MAXAGE, httponly=True
                )
            case _:
                pass

    await flash(_("Successfully set preferences"))

    return resp


@settings.post("/set-language")
async def setLanguage():
    form = await request.form
    language = form["lang"]

    if language not in current_app.config["languages"] and not language == "":
        flash(_("Invalid language: %(code)s", code=language), "error")
        return redirect(url_for("settings.mainSettings", ep="language"), code=303)

    resp = await make_response(
        redirect(url_for("settings.mainSettings", ep="language"), code=303)
    )

    resp.delete_cookie("lang")
    resp.set_cookie("lang", language, max_age=COOKIE_MAXAGE)
    g.lang = language
    refresh()
    await flash(_("Successfully set language."))
    return resp


@settings.post("/set-pixivision-language")
async def setPixivisionLanguage():
    form = await request.form
    language = form["lang"]
    if language not in ("en", "ja", "ko", "zh", "zh-tw"):
        flash(_("Invalid language: %(code)s", code=language), "error")
        return await redirect(url_for("settings.mainSettings", ep="language"), code=303)

    resp = await make_response(
        await redirect(url_for("settings.mainSettings", ep="language"), code=303)
    )

    resp.delete_cookie("PyXivPixivisionLang")
    resp.set_cookie("PyXivPixivisionLang", language, max_age=COOKIE_MAXAGE)

    flash(_("Successfully set language."))
    return resp
