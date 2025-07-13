from __future__ import annotations
from quart import Blueprint, abort, current_app, request

from ..api import pixiv_request, get_artwork
from ..lib.monet import get_scheme_css
import asyncio
import traceback
import logging
from typing import Union, TYPE_CHECKING
from urllib.parse import quote
from werkzeug.exceptions import HTTPException, BadRequest, NotFound

if TYPE_CHECKING:
    from quart import Response

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


@bp.errorhandler(NotFound)
async def handle_not_found(e: Exception):
    return make_error("Couldn't find requested page", code=404)


@bp.after_request
async def set_header_common(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


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


@bp.route("/api/configuration")
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
            raise Exception
    except Exception:
        log.exception("Failure retrieving commit")
        git_o = "unknown"

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


@bp.get("/api/illust/<int:id>/ugoira_meta")
async def ugoira_meta(id: int):
    work = await get_artwork(id)
    if not work.isUgoira:
        return make_error("Work is not ugoira", 400)
    
    data = await pixiv_request(f"/ajax/illust/{id}/ugoira_meta")
    return make_json_response(body=data)

@bp.get("/api/illust/<int:id>/material-you")
async def generate_material_theme_from_artwork(id: int):
    try:
        work = await pixiv_request(f"/ajax/illust/{id}")
        img = work["urls"]["small"]
        if not img:
            raise Exception
        req = await current_app.content_proxy.get(img)
        c = await req.read()

        result = await asyncio.get_running_loop().run_in_executor(
            None,
            get_scheme_css,
            c
        )

        return result, {"Content-Type": "text/css"}
    except Exception:
        log.exception("Failure generating color scheme for ID %d" , id)
        return "", {"Content-Type": "text/css"}

