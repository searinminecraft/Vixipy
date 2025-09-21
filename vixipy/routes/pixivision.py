from ..lib.pixivision import get_landing_page, get_article

from quart import Blueprint, render_template, request

bp = Blueprint("pixivision", __name__)

@bp.route("/pixivision")
async def main():
    data = await get_landing_page(
        int(request.args.get("p", 1))
    )


    return await render_template("pixivision/index.html", data=data)


@bp.route("/pixivision/a/<int:id>")
async def article(id: int):
    data = await get_article(id)
    return await render_template("pixivision/article.html", data=data)


@bp.route("/pixivision/t/<int:id>")
async def tag(id: int):
    ...


@bp.route("/pixivision/s/")
async def search():
    ...


@bp.route("/pixivision/c/<c>")
async def category(c: str):
    ...
