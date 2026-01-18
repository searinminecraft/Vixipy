from __future__ import annotations

from .handler import pixiv_request
from ..abc.artworks import ArtworkEntry
from ..abc.users import UserEntry, PartialUser
from ..filters import filter_from_prefs as ff


async def get_discovery(
    mode: str = "all",
) -> list[ArtworkEntry]:

    data = await pixiv_request(
        "/ajax/discovery/artworks",
        params=[("mode", mode), ("limit", 100)],
        ignore_cache=True,
    )

    return [ArtworkEntry(x) for x in data["thumbnails"]["illust"]]


async def get_recommended_users() -> list[UserEntry]:
    data = await pixiv_request(
        "/ajax/discovery/users", params=[("limit", 50)], ignore_cache=True
    )

    _illusts_to_dict: dict[int, ArtworkEntry] = {
        int(x["id"]): ArtworkEntry(x) for x in data["thumbnails"]["illust"]
    }
    _users_to_dict: dict[int, PartialUser] = {
        int(x["userId"]): PartialUser(x) for x in data["users"]
    }

    result: list[UserEntry] = []

    for x in data["recommendedUsers"]:
        user = _users_to_dict[int(x["userId"])]
        illusts = [_illusts_to_dict[int(y)] for y in x["recentIllustIds"]]
        result.append(UserEntry(user, ff(illusts)))

    return result
