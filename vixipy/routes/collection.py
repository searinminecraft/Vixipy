from quart import abort, render_template, Blueprint

from ..api import pixiv_request
from ..types import CollectionEntry, TagTranslation

import logging

bp = Blueprint("collection", __name__)
log = logging.getLogger("vixipy.routes.collection")


class CollectionRecommendByTag:
    def __init__(self, tag: str, content: list[CollectionEntry]):
        self.tag = tag
        self.content = content


@bp.route("/collection")
async def index():
    data = await pixiv_request("/ajax/top/collection")

    _collections: list[CollectionEntry] = [
        CollectionEntry(x) for x in data["thumbnails"]["collection"]
    ]

    log.debug("Collections: %s", _collections)
    _collection_map: dict[int, CollectionEntry] = {x.id: x for x in _collections}

    recommended = [
        _collection_map[int(x)] for x in data["page"]["recommendCollectionIds"]
    ]
    all_collections = [
        _collection_map[int(x)] for x in data["page"]["everyoneCollectionIds"]
    ]
    recommend_by_tag: list[CollectionRecommendByTag] = []

    for x in data["page"]["tagRecommendCollectionIds"]:
        recommend_by_tag.append(
            CollectionRecommendByTag(
                x["tag"], [_collection_map[int(y)] for y in x["ids"]]
            )
        )

    log.debug("Recommended by tag: %s", recommend_by_tag)
    log.debug("Recommended: %s", recommended)

    return await render_template(
        "collection/index.html",
        recommended=recommended,
        all_collections=all_collections,
        recommend_by_tag=recommend_by_tag,
    )
