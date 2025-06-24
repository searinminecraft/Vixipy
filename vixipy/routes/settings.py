from quart import (
    Blueprint,
    g,
    redirect,
    request,
    render_template,
    url_for,
    current_app,
    make_response,
)

from ..api import pixiv_request
import babel

bp = Blueprint("settings", __name__)

MAX_AGE = 60 * 60 * 24 * 30 * 6


@bp.route("/settings")
async def main():
    proxies = [
        "https://pixiv.ducks.party",
        "https://pximg.cocomi.eu.org",
        "https://i.suimoe.com",
        "https://i.yuki.sh",
        "https://pximg.obfs.dev",
        "https://pixiv.darkness.services",
        "https://pi.169889.xyz",
        "https://i.pixiv.re",
    ]

    return await render_template(
        "settings/main.html",
        proxies=proxies,
        is_instance_custom_proxy_server=not current_app.config["IMG_PROXY"].startswith(
            "/proxy/i.pximg.net"
        ),
    )


@bp.post("/settings/set_proxy_server")
async def set_proxy_server():
    f = await request.form
    r = await make_response(redirect(url_for("settings.main"), code=303))
    r.set_cookie("Vixipy-Image-Proxy", f["proxy"], max_age=MAX_AGE, httponly=True)
    return r


@bp.route("/settings/viewing")
async def viewing():
    if not current_app.no_token or g.authorized:
        capabilities_data = await pixiv_request("/ajax/settings/self")

        can_view_sensitive = (
            not current_app.config["NO_SENSITIVE"]
            and capabilities_data["user_status"]["sensitive_view_setting"] == 1
        )
        can_view_ai = not capabilities_data["user_status"]["hide_ai_works"]
        can_view_r18 = (
            can_view_sensitive
            and not current_app.config["NO_R18"]
            and int(capabilities_data["user_status"]["user_x_restrict"]) >= 1
        )
        can_view_r18g = (
            can_view_r18
            and int(capabilities_data["user_status"]["user_x_restrict"]) == 2
        )
    else:
        can_view_sensitive = not current_app.config["NO_SENSITIVE"]
        can_view_r18 = can_view_r18g = False
        can_view_ai = True

    return await render_template(
        "settings/display.html",
        ai=can_view_ai,
        r18=can_view_r18,
        r18g=can_view_r18g,
        sensitive=can_view_sensitive,
        no_token=current_app.no_token,
    )


@bp.post("/settings/set_content_filter")
async def set_content_filter():
    f = await request.form
    r = await make_response(redirect(url_for("settings.viewing"), code=303))
    r.set_cookie(
        "Vixipy-No-AI",
        str(int(f.get("hide-ai") == "on")),
        max_age=MAX_AGE,
        httponly=True,
    )
    r.set_cookie(
        "Vixipy-No-R18",
        str(int(f.get("hide-r18") == "on")),
        max_age=MAX_AGE,
        httponly=True,
    )
    r.set_cookie(
        "Vixipy-No-R18G",
        str(int(f.get("hide-r18g") == "on")),
        max_age=MAX_AGE,
        httponly=True,
    )
    r.set_cookie(
        "Vixipy-No-Sensitive",
        str(int(f.get("hide-sensitive") == "on")),
        max_age=MAX_AGE,
        httponly=True,
    )
    return r


@bp.route("/settings/language-and-location")
async def language_location():
    langs = {x: babel.Locale(x).language_name for x in current_app.config["LANGUAGES"]}
    return await render_template("settings/language.html", langs=langs)


@bp.post("/settings/set_language")
async def set_language():
    f = await request.form
    r = await make_response(redirect(url_for("settings.language_location"), code=303))
    r.set_cookie("Vixipy-Language", f["lang"], max_age=MAX_AGE, httponly=True)
    return r

