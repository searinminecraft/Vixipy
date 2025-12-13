from __future__ import annotations
from quart import Blueprint, abort, current_app, request
from quart_rate_limiter import rate_limit, timedelta

from ..api.handler import PixivError, pixiv_request
from ..api.artworks import get_artwork, get_newest_works
from ..decorators import tokenless_require_login
from ..lib.monet import scheme_from_url
import asyncio
import traceback
import logging
from typing import Union, TYPE_CHECKING
from urllib.parse import quote
from werkzeug.exceptions import (
    HTTPException,
    BadRequest,
    NotFound,
    TooManyRequests,
    Unauthorized,
    Forbidden,
)

if TYPE_CHECKING:
    from quart import Response
    from werkzeug.datastructures import ImmutableDict

bp = Blueprint("api", __name__, url_prefix="/api")
log = logging.getLogger("vixipy.routes.api")


def make_error(message: str, code: int = 500, body: Union[dict, list] = []):
    return {"error": True, "message": message, "body": body}, code


def make_json_response(message: str = "", body: Union[dict, list] = []):
    return {"error": False, "message": message, "body": body}


@bp.errorhandler(HTTPException)
async def handle_bad_request(e: HTTPException):
    code_map = {
        400: "Invalid request",
        401: "Authorization required to access endpoint",
        403: "Insufficient permission to access resource",
        404: "Resource not found or does not exist",
        405: "Method not allowed",
        429: "Too many requests. Try again another time"
    }
    return make_error(code_map.get(e.code, "Invalid request"), e.code)


@bp.errorhandler(Exception)
async def handle_errors(e: Exception):
    return make_error(
        "Exception error", body={"error": str(e), "traceback": traceback.format_exc()}
    )


@bp.after_request
async def set_header_common(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


@bp.route("/search/autocomplete")
async def autocomplete_handler():
    keyword = request.args["keyword"]

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


@bp.route("/configuration")
async def node_info():
    account = not current_app.no_token

    try:
        git_p = await asyncio.create_subprocess_exec(
            "git",
            "rev-parse",
            "--short",
            "HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        git_o, err = await git_p.communicate()
        if err:
            raise RuntimeError(err.decode("utf-8"))
    except Exception:
        log.exception("Failure retrieving commit")
        rev = None
    else:
        rev = str(git_o.decode("utf-8")).rstrip()

    return make_json_response(
        body={
            "acceptLanguage": current_app.config["ACCEPT_LANGUAGE"],
            "commit": rev,
            "instanceName": current_app.config["INSTANCE_NAME"],
            "r18": not current_app.config["NO_SENSITIVE"]
            and not current_app.config["NO_R18"],
            "sensitiveWorks": not current_app.config["NO_SENSITIVE"],
            "ratelimiting": current_app.config["QUART_RATE_LIMITER_ENABLED"],
            "repo": "https://codeberg.org/vixipy/Vixipy",
            "usesAccount": account,
            "logHttp": current_app.config["LOG_HTTP"],
            "logPixiv": current_app.config["LOG_PIXIV"],
            "version": current_app.config["VIXIPY_VERSION"],
            "bypassCloudflare": current_app.config["PIXIV_DIRECT_CONNECTION"],
            "imageProxy": current_app.config["IMG_PROXY"],
        }
    )


@bp.get("/illust/<int:id>/ugoira_meta")
@rate_limit(1, timedelta(seconds=5))
async def ugoira_meta(id: int):
    try:
        work = await get_artwork(id)
    except PixivError as e:
        if e.code == 404:
            abort(404)
        else:
            abort(e.code)

    if not work.isUgoira:
        return make_error("Work is not ugoira", 400)

    data = await pixiv_request(f"/ajax/illust/{id}/ugoira_meta")
    return make_json_response(body=data)


@bp.get("/illust/<int:id>/material-you")
async def gen_scheme_from_artwork(id: int):
    try:
        work = await pixiv_request(f"/ajax/illust/{id}")
        scheme = request.args.get("scheme", "tonal_spot")
        img = work["urls"]["thumb"]
        if not img:
            raise Exception

        result = await scheme_from_url(img, True, scheme)

        return result, {"Content-Type": "text/css", "Cache-Control": "max-age=31536000"}
    except Exception:
        log.exception("Failure generating color scheme for ID %d", id)
        return "", {"Content-Type": "text/css"}


@bp.get("/user/<int:id>/material-you")
async def gen_scheme_from_user(id: int):
    try:
        data = await pixiv_request(f"/ajax/user/{id}")
        scheme = request.args.get("scheme", "tonal_spot")
        if background := data["background"]:

            img = background["url"]
            result = await scheme_from_url(img, True, scheme)
            return result, {
                "Content-Type": "text/css",
                "Cache-Control": "max-age=31536000",
            }

        return "", {"Content-Type": "text/css"}
    except Exception:
        log.exception("Failure generating color scheme for ID %d", id)
        return "", {"Content-Type": "text/css"}


@bp.route("/illust/new")
@tokenless_require_login
async def _get_new_works():
    args: ImmutableDict = request.args

    no_r18 = current_app.config["NO_SENSITIVE"] or current_app.config["NO_R18"]

    if no_r18 and request.args.get("r18") == "true":
        abort(403)

    try:
        data = await get_newest_works(
            type_=args.get("type", "illust"),
            r18=args.get("r18") == "true",
            last_id=args.get("last_id", 0),
        )
    except PixivError:
        abort(403)
    except Exception:
        raise

    illusts = []
    for x in data.illusts:
        illusts.append(
            {
                "id": x.id,
                "title": x.title,
                "thumb": x.thumb,
                "r18": x.r18,
                "ai": x.ai,
                "user_id": x.authorId,
                "user_name": x.authorName,
                "profile_image": x.profileimg,
                "page_count": x.pages,
                "alt": x.alt,
            }
        )
    return make_json_response(body={"last_id": data.last_id, "illusts": illusts})
