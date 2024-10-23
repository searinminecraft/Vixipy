from flask import Blueprint, render_template, request
from ..utils.converters import makeProxy

from pyxivision import PixivisionArticle


pixivision = Blueprint("pixivision", __name__, url_prefix="/pixivision")


@pixivision.route("/a/<int:_id>")
def getPixivisionArticle(_id: int):

    langPref = request.cookies.get("PyXivPixivisionLang", "en")
    article = PixivisionArticle(_id, langPref)

    if article.image:
        article.image = makeProxy(article.image)

    return render_template("pixivision/article.html", article=article)
