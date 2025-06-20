from quart import Blueprint, abort, request

from ..api import pixiv_request
import traceback
import logging
from typing import Union
from urllib.parse import quote
from werkzeug.exceptions import HTTPException, BadRequest, NotFound

bp = Blueprint("api", __name__)
log = logging.getLogger("vixipy.routes.api")


def make_error(message: str, code: int = 500, body: Union[dict, list] = []):
    return {"error": True, "message": message, "body": body}, code


def make_json_response(message: str = "", body: Union[dict, list] = []):
    return {"error": False, "message": message, "body": body}


@bp.errorhandler(BadRequest)
async def handle_bad_request(e: BadRequest):
    return make_error("Invalid request", 400)


@bp.errorhandler(Exception)
async def handle_errors(e: Exception):
    return make_error(
        "Exception error", body={"error": str(e), "traceback": traceback.format_exc()}
    )


@bp.route("/api/search/autocomplete")
async def autocomplete_handler():
    keyword = request.args.get("keyword")
    if not keyword:
        abort(400)

    data = await pixiv_request(
        "/rpc/cps.php",
        params=[("keyword", quote(keyword, safe="")), ("lang", "en")],
        headers={"Referer": "https://www.pixiv.net"},
    )

    result: list[dict] = []

    for x in data["candidates"]:
        log.debug(x)
        if x["type"] in ("romaji", "tag_translation"):
            result.append(
                {
                    "name": x["tag_name"],
                    "sub": x.get("tag_translation"),
                    "access_count": int(x["access_count"]),
                }
            )
        else:
            result.append(
                {
                    "name": x["tag_name"],
                    "sub": None,
                    "access_count": int(x["access_count"]),
                }
            )

    return make_json_response(
        body=sorted(result, key=lambda _: _["access_count"], reverse=True)
    )
