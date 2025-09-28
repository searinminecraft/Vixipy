from ..lib.pixivision import get_landing_page, get_article, get_tag, get_category

from quart import Blueprint, render_template, request
from quart_rate_limiter import limit_blueprint, timedelta

bp = Blueprint("pixivision", __name__)
limit_blueprint(bp, 1, timedelta(seconds=5))


@bp.route("/pixivision")
async def main():
    data = await get_landing_page(int(request.args.get("p", 1)))

    return await render_template("pixivision/index.html", data=data)


@bp.route("/pixivision/a/<int:id>")
async def article(id: int):
    data = await get_article(id)
    return await render_template("pixivision/article.html", data=data)


@bp.route("/pixivision/t/<int:id>")
async def tag(id: int):
    data, pg = await get_tag(id, int(request.args.get("p", 1)))
    return await render_template("pixivision/tag.html", data=data, pg=pg, id=id)


@bp.route("/pixivision/s/")
async def search(): ...


@bp.route("/pixivision/c/<c>")
async def category(c: str):
    data, pg = await get_category(c, int(request.args.get("p", 1)))
    return await render_template("pixivision/category.html", data=data, pg=pg, c=c)
