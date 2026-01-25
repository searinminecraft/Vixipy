from __future__ import annotations

from quart import g, request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Quart


def add_htmx_request_header():
    g.hx_boosted = request.headers.get("HX-Boosted") == "true"
    g.hx_current_url = request.headers.get("HX-Current-Url")
    g.hx_history_restore_request = request.headers.get("HX-History-Restore-Request") == "true"
    g.hx_prompt = request.headers.get("HX-Prompt")
    g.hx_request = request.headers.get("HX-Request") == "true"
    g.hx_target = request.headers.get("HX-Target")
    g.hx_trigger_name = request.headers.get("HX-Trigger-Name")
    g.hx_trigger = request.headers.get("HX-Trigger")


def init_app(app: Quart):
    app.before_request(add_htmx_request_header)

