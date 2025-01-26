from quart import Blueprint, Response, current_app, g
from ..api import pixivReq
from .. import cfg
from werkzeug.exceptions import NotFound

bp = Blueprint("api", __name__)


@bp.after_request
async def after_request(r: Response):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


@bp.get("/api/configuration")
async def getConfig():
    try:
        return {
            "error": False,
            "message": "",
            "body": {
                "version": cfg.Version,
                "commit": g.rev,
                "repo": g.repo,
                "instanceName": g.instanceName,
                "ratelimiting": current_app.config["QUART_RATE_LIMITER_ENABLED"],
                "r18": not current_app.config["nor18"] and not cfg.AuthlessMode,
                "usesAccount": not cfg.AuthlessMode,
                "acceptLanguage": cfg.PxAcceptLang,
            },
        }
    except Exception:
        return {"error": True, "message": "Unable to get configuration"}, 500


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
