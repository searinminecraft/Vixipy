from .handler import pixiv_request
from ..abc.artworks import ArtworkEntry
from ..abc.novels import NovelEntry


async def get_latest_works_from_following(
    page: int = 1, mode: str = "all"
) -> tuple[ArtworkEntry, bool]:
    if mode not in ("all", "r18"):
        raise ValueError("invalid mode")

    data = await pixiv_request(
        "/ajax/follow_latest/illust",
        params=[
            ("p", page),
            ("mode", mode),
        ],
    )

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]], data["page"][
        "isLastPage"
    ]


async def get_latest_novels_from_following(page: int = 1, mode: str = "all"):
    if mode not in ("all", "r18"):
        raise ValueError("invalid mode")

    data = await pixiv_request(
        "/ajax/follow_latest/novel",
        params=[
            ("p", page),
            ("mode", mode),
        ],
    )

    return [NovelEntry(x) for x in data["thumbnails"]["novel"]], data["page"][
        "isLastPage"
    ]
