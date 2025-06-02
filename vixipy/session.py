from __future__ import annotations

from asyncio import gather
from quart import g, request
from typing import TYPE_CHECKING

from .api import get_notification_count, get_self_extra, get_user

if TYPE_CHECKING:
    from quart import Quart
    from .types import User, UserExtraData


async def get_session_data():
    if any(
        request.path.startswith(f"/{x}")
        for x in ("favicon.ico", "robots.txt", "static", "proxy", "sass")
    ):
        return

    c = request.cookies
    g.authorized = c.get("Vixipy-Token")
    g.language = c.get("Vixipy-Language")

    if g.authorized:
        g.token = c.get("Vixipy-Token")
        g.csrf = c.get("Vixipy-CSRF")
        g.p_ab_d_id = c.get("Vixipy-p_ab_d_id")
        g.p_ab_id = c.get("Vixipy-p_ab_id")
        g.p_ab_id_2 = c.get("Vixipy-p_ab_id_2")
        g.yuid_b = c.get("Vixipy-yuid_b")

        if request.path.startswith("/api"):
            return
        if request.headers.get("X-Vixipy-Quick-Action") == "true":
            return

        notification_count, user, extra = await gather(
            get_notification_count(), get_user(g.token.split("_")[0]), get_self_extra()
        )
    
        notification_count: int
        user: User
        extra: UserExtraData
    
        g.current_user = user
        g.notification_count = notification_count
        g.current_user_extra = extra


def init_app(app: Quart):
    app.before_request(get_session_data)
