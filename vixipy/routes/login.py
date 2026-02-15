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
from ..abc.users import UserSelfData
from ..session import _generate_ab_cookies
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
            req = await pixiv_request("/ajax/user/self", cookies={"PHPSESSID": token})
            user = UserSelfData(req)
        except PixivError:
            await flash(_("Invalid token"), "error")
            return await render_template("login.html.j2", bg=proxy(background), id=id)

        gen_c = _generate_ab_cookies()        

        res = await make_response(redirect(return_path))
        res.set_cookie("Vixipy-Token", token, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-CSRF", user.csrf_token, max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-p_ab_id", gen_c[2], max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie("Vixipy-yuid_b", gen_c[0], max_age=COOKIE_MAXAGE, httponly=True)
        res.set_cookie(
            "Vixipy-p_ab_id_2", gen_c[3], max_age=COOKIE_MAXAGE, httponly=True
        )
        res.set_cookie(
            "Vixipy-p_ab_d_id", str(user.p_ab_d_id), max_age=COOKIE_MAXAGE, httponly=True
        )
        return res

    return await render_template("login.html.j2", bg=proxy(background), id=id)
