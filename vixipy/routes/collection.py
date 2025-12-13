from quart import abort, render_template, Blueprint

from ..api.handler import pixiv_request
from ..converters import proxy
from ..types import ArtworkEntry, CollectionEntry, TagTranslation

from enum import Enum
import logging

bp = Blueprint("collection", __name__)
log = logging.getLogger("vixipy.routes.collection")


class CollectionRecommendByTag:
    def __init__(self, tag: str, content: list[CollectionEntry]):
        self.tag = tag
        self.content = content


class CollectionTile:
    def __init__(self, d: dict):
        self.posX: int = d["layout"]["position"]["x"]
        self.posY: int = d["layout"]["position"]["y"]
        self.sizeX: int = d["layout"]["size"]["x"]
        self.sizeY: int = d["layout"]["size"]["y"]

    @property
    def grid_area(self):
        return (
            "grid-area: "
            f"{self.posY + 1} / "
            f"{self.posX + 1} / "
            f"{self.sizeY + self.posY + 1} / "
            f"{self.sizeX + self.posX + 1}"
        )


class IllustTile(CollectionTile):
    def __init__(self, d: dict, illust_data: ArtworkEntry, urls: dict[str, str]):
        super().__init__(d)
        self.thumb = proxy(urls["540x540"])
        self.illust_data = illust_data


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


@bp.route("/collections/<int:id>")
async def get_collection(id: int):
    data = await pixiv_request(f"/ajax/collection/{id}")
    collection = CollectionEntry(data["data"]["userCollections"][str(id)])
    log.debug("Got collection: %s", collection)

    tiles: list[CollectionTile] = []
    _illusts_map = (
        {x["id"]: x for x in data["thumbnails"]["illust"]}
        if len(data["thumbnails"]["illust"]) > 0
        else {}
    )

    for x in data["data"]["detail"]["tiles"]:
        if x["type"] == "Work":
            if x["workType"] == "illust":
                target = _illusts_map[x["workId"]]
                tiles.append(IllustTile(x, ArtworkEntry(target), target["urls"]))
            else:
                log.warn("Unknown workType %s, stub!", x["workType"])
                tiles.append(CollectionTile(x))
        else:
            log.warn("Unknown type %s, stub!", x["type"])
            tiles.append(CollectionTile(x))

    log.debug("Tiles: %s", tiles)

    return await render_template(
        "collection/collection.html", collection=collection, tiles=tiles
    )
