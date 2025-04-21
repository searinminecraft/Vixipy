from __future__ import annotations

from asyncio import gather
from quart import g, request
from typing import TYPE_CHECKING

from .api import pixiv_request


if TYPE_CHECKING:
    from quart import Quart

async def get_session_data():
    c = request.cookies
    g.authorized = c.get("Vixipy-Token")
    g.language = c.get("Vixipy-Language")

    if g.authorized:
        g.token = c.get("Vixipy-Token")
        g.csrf = c.get("Vixipy-CSRF")
        g.p_ab_d_id = c.get("Vixipy-p_ab_d_id")
        g.p_ab_id = c.get("Vixipy-p_ab_id")
        g.p_ab_id_2 = c.get("Vixipy-p_ab_id_2")

        await gather(
            pixiv_request("/rpc/notify_count.php", params=[("op", "count_unread")], headers={"Accept": "application/json", "Referer": "https://www.pixiv.net/en"}),
            pixiv_request(f"/ajax/user/{g.token.split('_')[0]}", params=[("full", "sadfasdf")]),
            pixiv_request("/ajax/user/extra")
        )

def init_app(app: Quart):
    app.before_request(get_session_data)
