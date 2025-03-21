from quart import (
    Blueprint,
    abort,
    g,
)
from ..core.novels import getNovel, getRecommendedNovels
from ..core.user import getUser
from asyncio import gather


bp = Blueprint("novels", __name__)


@bp.route("/novels")
async def novels_root():
    abort(501)


@bp.route("/novels/<int:id>")
async def novel_main(id: int):
    data = await getNovel(id)
    user, recommended = await gather(
        getUser(data.userId, False),
        getRecommendedNovels(id),
    )
    return repr(data), {"Content-Type": "text/plain"}


@bp.route("/novels/series/<int:id>")
async def novel_series(id: int):
    abort(501)
