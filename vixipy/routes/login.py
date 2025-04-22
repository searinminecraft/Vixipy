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
    url_for
)
from quart_babel import _

from ..api import pixiv_request, PixivError
import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aiohttp import ClientResponse

bp = Blueprint("login", __name__)
log = logging.getLogger("vixipy.routes.login")
COOKIE_MAXAGE = 2592000

@bp.route("/self/login", methods=["GET", "POST"])
async def login_page():
    return_path = request.args.get("return_to", "/")
    if g.authorized:
        return redirect(return_path)

    if request.method == "POST":
        f = await request.form
        token = f["token"]

        try:
            await pixiv_request("/ajax/user/extra", cookies={"PHPSESSID": token})
            log.debug("Login success, get CSRF next...")
        except PixivError:
            await flash(_("Invalid token"), "error")
            return await render_template("login.html")

        r: ClientResponse = await current_app.pixiv.get("", allow_redirects=True, headers={"Cookie": f"PHPSESSID={token}"})
        r.raise_for_status()
        t = await r.text()

        try:
            csrf = re.search(r'\\"token\\":\\"([0-9a-f]+)\\"', t).group(1)
        except IndexError:
            await flash(_("Unable to extract CSRF"))
            return await render_template("login.html")

        p_ab_id = r.cookies["p_ab_id"].value
        p_ab_id_2 = r.cookies["p_ab_id_2"].value
        p_ab_d_id = r.cookies["p_ab_d_id"].value
        log.debug("Extracted necessary info:")
        log.debug("csrf = %s", csrf)
        log.debug("p_ab_id = %s", p_ab_id)
        log.debug("p_ab_id_2 = %s", p_ab_id_2)
        log.debug("p_ab_d_id = %s", p_ab_d_id)

        res = await make_response(redirect(return_path))
        res.set_cookie("Vixipy-Token", token, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-CSRF", csrf, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-p_ab_id", p_ab_id, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-p_ab_id_2", p_ab_id_2, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-p_ab_d_id", p_ab_d_id, max_age=COOKIE_MAXAGE, httponly=True)
        return res



    return await render_template("login.html")