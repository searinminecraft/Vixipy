from __future__ import annotations

from .handler import pixiv_request
from ..abc.novels import Novel, NovelEntry, NovelSeries


async def get_novel(id: int) -> Novel:
    data = await pixiv_request(f"/ajax/novel/{id}")
    return Novel(data)


async def get_recommended_novels(id: int) -> list[NovelEntry]:
    data = await pixiv_request(
        f"/ajax/novel/{id}/recommend/init", params=[("limit", 20)]
    )
    return [NovelEntry(x) for x in data["novels"]]


async def get_novel_series(id: int) -> NovelSeries:
    data = await pixiv_request(f"/ajax/novel/series/{id}")
    return NovelSeries(data)


async def get_novel_series_contents(id: int, page: int = 1) -> NovelEntry:
    data = await pixiv_request(
        f"/ajax/novel/series_content/{id}",
        params=[("limit", 30), ("last_order", (30 * page) - 30), ("order_by", "asc")],
    )

    __entries: dict[int, NovelEntry] = {
        x["id"]: NovelEntry(x) for x in data["thumbnails"]["novel"]
    }

    for x in data["page"]["seriesContents"]:
        __entries[x["id"]].title = f"#{x['series']['contentOrder']} {x['title']}"

    return list(__entries.values())
