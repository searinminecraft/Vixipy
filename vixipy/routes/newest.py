from __future__ import annotations

from quart import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
)
from quart_rate_limiter import limit_blueprint, timedelta

from ..api import get_newest_works
from ..decorators import tokenless_require_login
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from werkzeug.datastructures import ImmutableDict

bp = Blueprint("newest", __name__)
limit_blueprint(bp, 2, timedelta(seconds=6))

@bp.route("/newest")
@tokenless_require_login
async def newest_main():
    args: ImmutableDict = request.args


    data = await get_newest_works(
        args.get("type", "illust"),
        r18=args.get("r18") == "true",
    )
    return await render_template("newest/index.html", data=data)
    
@bp.route("/new_illust.php")
async def pixiv_compat_redirect():
    return redirect(url_for("newest.newest_main", **request.args), code=308)
