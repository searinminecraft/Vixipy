from __future__ import annotations

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
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional

bp = Blueprint("settings", __name__)
log = logging.getLogger("vixipy.routes.settings")

MAX_AGE = 60 * 60 * 24 * 30 * 6

class TranslationCredit:
    def __init__(self, name: str, languages: list[str], link: Optional[str] = None, profile_img: Optional[str] = None):
        self.name: str = name
        self.languages: list[str] = languages
        self.link: Optional[str] = link
        self.profile_img: Optional[str] = profile_img

    def __repr__(self):
        return (
            "<TranslationCredit "
            f"name={self.name} "
            f"languages={self.languages} "
            f"link={self.link} "
            f"profile_img={self.profile_img}>"
        )
    
    def translate_languages(self, language_code):
        self.languages = [babel.Locale(x).get_display_name(language_code) for x in self.languages]


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
        themes=current_app.config["ADDITIONAL_THEMES"] + current_app.config["DEFAULT_THEMES"]
    )


@bp.post("/settings/set_proxy_server")
async def set_proxy_server():
    f = await request.form
    r = await make_response(redirect(url_for("settings.main"), code=303))
    r.set_cookie("Vixipy-Image-Proxy", f["proxy"], max_age=MAX_AGE, httponly=True)
    return r


@bp.post("/settings/set_color")
async def set_color():
    f = await request.form
    r = await make_response(redirect(url_for("settings.main"), code=303))
    r.set_cookie("Vixipy-Theme", f["color"], max_age=MAX_AGE, httponly=True)
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
        can_view_r18 = can_view_r18g = not current_app.config["NO_R18"]
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
        str(int(not f.get("hide-ai") == "on")),
        max_age=MAX_AGE,
        httponly=True,
    )

    r18g = not f.get("hide-r18g") == "on"
    r18 = not f.get("hide-r18") == "on"
    sensitive = not f.get("hide-sensitive") == "on"
    preview = f.get("preview-mode") == "on"
    blur = f.get("blur") == "on"

    log.debug((sensitive, r18, r18g))

    r.set_cookie(
        "Vixipy-No-R18",
        str(int(r18)),
        max_age=MAX_AGE,
        httponly=True,
    )
    r.set_cookie(
        "Vixipy-No-R18G",
        str(int(r18g)),
        max_age=MAX_AGE,
        httponly=True,
    )
    r.set_cookie(
        "Vixipy-No-Sensitive",
        str(int(sensitive)),
        max_age=MAX_AGE,
        httponly=True,
    )
    r.set_cookie(
        "Vixipy-Preview-Mode",
        str(int(preview)),
        max_age=MAX_AGE,
        httponly=True,
    )
    r.set_cookie(
        "Vixipy-Blur-Sensitive",
        str(int(blur)),
        max_age=MAX_AGE,
        httponly=True
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

@bp.get("/settings/about")
async def about_page():
    return await render_template("settings/about.html")

@bp.get("/settings/acknowledgements")
async def acknowledgements():
    language = request.cookies.get("Vixipy-Language", "en") or "en"
    TRANSLATION_CREDITS: list[TranslationCredit] = {
        TranslationCredit("Vyxie", ["fil", "ja"], "https://codeberg.org/kita", "/proxy/3rd_party/profile_image/codeberg/kita"),
        TranslationCredit("cutekita", ["de"], "https://github.com/coolesding", "/proxy/3rd_party/profile_image/github/coolesding"),
        TranslationCredit("SomeTr", ["uk", "de"], "https://codeberg.org/SomeTr"),
        TranslationCredit("Poesty Li", ["zh_Hans"], "https://codeberg.org/poesty"),
        TranslationCredit("Hayden", ["zh_Hans"], "https://codeberg.org/haydenwu", "/proxy/3rd_party/profile_image/codeberg/haydenwu"),
        TranslationCredit("lainie", ["ru"], "https://laincorp.tech")
    }

    for x in TRANSLATION_CREDITS:
        x.translate_languages(language)
    
    return await render_template("settings/acknowledgements.html", i18n_cred=sorted(TRANSLATION_CREDITS, key=lambda _: _.name))
