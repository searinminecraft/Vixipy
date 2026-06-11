from quart import Blueprint, abort, current_app, g, render_template, request
from asyncio import gather
from ..api.handler import pixiv_request
from pprint import pformat
import json

bp = Blueprint("admin", __name__, url_prefix="/admin")
default_headers = {
    "Referer": "https://www.pixiv.net"
}

@bp.before_request
def check_permissions():
    if not g.authorized or g.token not in current_app.accounts:
        abort(404)

@bp.route("/")
async def root():
    return await render_template("admin.html")

async def _execute_api_job(a, endpoint, method, content_type, payload):
    data = await pixiv_request(
        endpoint,
        method,
        headers={**default_headers, "Content-Type": content_type} if method=="post" else default_headers,
        account=a,
        json_payload=json.loads(payload) if content_type=="application/json" else None,
        raw_payload=payload if content_type=="application/x-www-form-url-encoded" else None,
        ignore_cache=True
    )

    return pformat(data), a


@bp.post("/eval")
async def api_eval():
    f = await request.form

    endpoint = f["endpoint"]
    method = f["method"]
    content_type = f["content-type"]
    payload = f["payload"]

    jobs = [_execute_api_job(x, endpoint, method, content_type, payload) for x in current_app.accounts]
    results = await gather(*jobs)
    return await render_template("admin.html", api_results=results)
