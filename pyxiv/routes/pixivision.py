from quart import Blueprint, render_template, request, current_app
from ..utils.converters import makeProxy

from urllib.parse import urlparse


pixivision = Blueprint("pixivision", __name__, url_prefix="/pixivision")


@pixivision.route("/")
async def pixivisionRoot():

    langPref = request.cookies.get("PyXivPixivisionLang", "en")
    page = int(request.args.get("p", 1))
    data = await current_app.pyxivision.getLanding(lang=langPref, page=page)

    if data.spotlight:
        data.spotlight.image = makeProxy(data.spotlight.image)

    for article in data.articles:
        article.image = makeProxy(article.image)

    for featured in data.featured:
        featured.image = makeProxy(featured.image)

    for rank in data.ranking:
        rank.image = makeProxy(rank.image)

    return await render_template("pixivision/index.html", data=data)


@pixivision.route("/a/<int:_id>")
async def getPixivisionArticle(_id: int):

    langPref = request.cookies.get("PyXivPixivisionLang", "en")
    article = await current_app.pyxivision.getArticle(_id, langPref)

    for work in article.works:
        work.authorImage = makeProxy(work.authorImage)
        work.image = makeProxy(work.image)
        work.link = urlparse(work.link).path
        work.authorLink = urlparse(work.authorLink).path

    if article.image:
        article.image = makeProxy(article.image)

    return await render_template("pixivision/article.html", article=article)
