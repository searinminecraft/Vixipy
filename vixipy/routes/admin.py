from quart import Blueprint, abort, current_app, g, render_template, request
from asyncio import gather
from ..api.handler import pixiv_request
from pprint import pformat

bp = Blueprint("admin", __name__, url_prefix="/admin")

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
        headers={"Content-Type": content_type},
        account=a,
        raw_payload=payload
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
