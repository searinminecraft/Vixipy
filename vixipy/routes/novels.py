from quart import (
    Blueprint,
    render_template,
    redirect,
    url_for
)


from ..api import get_novel, get_user, pixiv_request
bp = Blueprint("novels", __name__)


@bp.route("/novel/show/<int:id>")
async def novel_main(id: int):
    data = await get_novel(id)
    user = await get_user(data.user_id)
    return await render_template("novels/novel.html", data=data, user=user)