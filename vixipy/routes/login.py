from __future__ import annotations

from quart import (
    Blueprint,
    current_app,
    flash,
    g,
    make_response,
    request,
    redirect,
    render_template,
    url_for,
)
from quart_babel import _

from ..api.handler import pixiv_request, PixivError
from ..constants import LOGIN_PAGE_BACKGROUNDS
from ..converters import proxy
import logging
import random
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

bp = Blueprint("login", __name__)
log = logging.getLogger("vixipy.routes.login")
COOKIE_MAXAGE = 60 * 60 * 24 * 30 * 6
#               ^    ^    ^    ^    ^
#               sec  min  hr   day  mo


@bp.route("/self/login", methods=["GET", "POST"])
async def login_page():
    return_path = request.args.get("return_to", "/")
    if g.authorized:
        return redirect(return_path)

    background = random.choice(LOGIN_PAGE_BACKGROUNDS)
    id = re.search(
        r"https:\/\/i\.pximg\.net\/c\/540x540_70\/img-master\/img\/\d{4}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/\d{2}\/(\d+)_p\d+_master1200\.jpg",
        background,
    ).group(1)

    if request.method == "POST":
        f = await request.form
        token = f["token"]
        return_path = f.get("return_to", "/")

        try:
            await pixiv_request("/ajax/user/extra", cookies={"PHPSESSID": token})
            log.debug("Login success, get CSRF next...")
        except PixivError:
            await flash(_("Invalid token"), "error")
            return await render_template("login.html", bg=proxy(background), id=id)

        if current_app.config["PIXIV_DIRECT_CONNECTION"]:
            r: ClientResponse = await current_app.pixiv.get(
                "",
                allow_redirects=True,
                headers={"Cookie": f"PHPSESSID={token}"},
                server_hostname="www.pixiv.net",
            )
            unauth_r: ClientResponse = await current_app.pixiv.get(
                "", allow_redirects=True, server_hostname="www.pixiv.net"
            )
        else:
            r: ClientResponse = await current_app.pixiv.get(
                "", allow_redirects=True, headers={"Cookie": f"PHPSESSID={token}"}
            )
            unauth_r: ClientResponse = await current_app.pixiv.get(
                "", allow_redirects=True
            )

        r.raise_for_status()
        t = await r.text()

        try:
            csrf = re.search(r'\\"token\\":\\"([0-9a-f]+)\\"', t).group(1)
        except IndexError:
            await flash(_("Unable to extract CSRF"))
            return await render_template("login.html", bg=proxy(background), id=id)

        p_ab_id = r.cookies["p_ab_id"].value
        p_ab_id_2 = r.cookies["p_ab_id_2"].value
        p_ab_d_id = r.cookies["p_ab_d_id"].value
        yuid_b = unauth_r.cookies["yuid_b"].value
        log.debug("Extracted necessary info:")
        log.debug("csrf = %s", csrf)
        log.debug("p_ab_id = %s", p_ab_id)
        log.debug("p_ab_id_2 = %s", p_ab_id_2)
        log.debug("p_ab_d_id = %s", p_ab_d_id)

        res = await make_response(redirect(return_path))
        res.set_cookie("Vixipy-Token", token, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-CSRF", csrf, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-p_ab_id", p_ab_id, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-yuid_b", yuid_b, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie(
            "Vixipy-p_ab_id_2", p_ab_id_2, max_age=COOKIE_MAXAGE, httponly=True
        )
        res.set_cookie(
            "Vixipy-p_ab_d_id", p_ab_d_id, max_age=COOKIE_MAXAGE, httponly=True
        )
        return res

    return await render_template("login.html", bg=proxy(background), id=id)
