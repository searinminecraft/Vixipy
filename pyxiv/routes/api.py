from quart import Blueprint, Response
from ..api import pixivReq
from werkzeug.exceptions import NotFound

bp = Blueprint("api", __name__)


@bp.after_request
async def after_request(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


@bp.route("/api/internal/ugoira_meta/<int:_id>")
async def ugoira_meta(_id: int):
    try:
        data = await pixivReq("get", f"/ajax/illust/{_id}/ugoira_meta")
    except NotFound:
        return {
            "error": True,
            "message": "The requested resource either does not exist or is not an ugoira.",
        }, 404
    except Exception:
        return {"error": True, "message": "Internal server error"}, 500

    return data
