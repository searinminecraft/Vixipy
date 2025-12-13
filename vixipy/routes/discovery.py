from quart import Blueprint, abort, current_app, g, render_template, request

import logging

from ..api.discovery import get_discovery, get_recommended_users
from ..decorators import tokenless_require_login
from ..filters import filter_from_prefs as ff

bp = Blueprint("discovery", __name__)
log = logging.getLogger("vixipy.routes.discovery")


@bp.route("/discovery")
@tokenless_require_login
async def discovery_root():

    data = await get_discovery(mode=request.args.get("mode", "all"))

    return await render_template("discovery/illustrations.html", data=ff(data))


@bp.route("/discovery/users")
@tokenless_require_login
async def discovery_users():
    data = await get_recommended_users()
    log.debug(data)
    return await render_template("discovery/users.html", data=data)
