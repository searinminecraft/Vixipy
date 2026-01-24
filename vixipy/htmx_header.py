from __future__ import annotations

from quart import g, request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Quart


async def add_htmx_request_header():
    g.hx_boosted = request.headers.get("hx-boosted") == "true"
    g.hx_current_url = request.headers.get("hx-current-url")
    g.hx_history_restore_request = request.headers.get("hx-history-restore-request") == "true"
    g.hx_prompt = request.headers.get("hx-prompt")
    g.hx_request = request.headers.get("hx-request") == "true"
    g.hx_target = request.headers.get("hx-target")
    g.hx_trigger_name = request.headers.get("hx-trigger-name")
    g.hx_trigger = request.headers.get("hx-trigger")


async def init_app(app: Quart):
    app.before_request(add_htmx_request_header)

