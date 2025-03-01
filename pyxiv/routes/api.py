from quart import Blueprint, Response, current_app, g, request
from ..api import pixivReq, PixivError
from ..core import messages
from .. import cfg
from werkzeug.exceptions import NotFound
import logging

log = logging.getLogger("vixipy.routes.api")

bp = Blueprint("api", __name__)

r18Enabled = None


@bp.after_request
async def after_request(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


@bp.get("/api/configuration")
async def getConfig():
    try:
        global r18Enabled
        if not cfg.AuthlessMode and not current_app.config["nor18"]:
            if r18Enabled is None:
                # Checks if R18 is enabled by trying to access one. It will be cached to prevent pixiv suspicion.
                # WARNING: THIS ILLUSTRATION IS R18!

                try:
                    await pixivReq("get", "/ajax/illust/126452721/pages")
                    r18Enabled = True
                except (NotFound, PixivError):
                    r18Enabled = False
        else:
            r18Enabled = False

        return {
            "error": False,
            "message": "",
            "body": {
                "version": cfg.Version,
                "commit": g.rev,
                "repo": g.repo,
                "instanceName": g.instanceName,
                "ratelimiting": current_app.config["QUART_RATE_LIMITER_ENABLED"],
                "r18": r18Enabled,
                "usesAccount": not cfg.AuthlessMode,
                "acceptLanguage": cfg.PxAcceptLang,
            },
        }
    except Exception as e:
        log.exception("Unable to get configuration")
        return {"error": True, "message": f"Unable to get configuration: {e}"}, 500


@bp.get("/api/internal/ugoira_meta/<int:_id>")
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


@bp.get("/api/messages/<int:thread_id>/contents")
async def getMessages(thread_id: int):
    try:
        data = await messages.getMessageThreadContents(thread_id, max_content_id=request.args.get("max_content_id"))
        c = [x.to_json() for x in data.contents]
        return {"contents": c}
    except PixivError as e:
        return {"error": True, message: str(e.message), body: {}}