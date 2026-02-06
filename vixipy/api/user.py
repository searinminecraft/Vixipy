from __future__ import annotations

from .handler import pixiv_request
from ..abc.users import User, UserExtraData, PartialUser, UserPageIllusts, UserFollowRes
from ..abc.artworks import ArtworkEntry


async def get_user(id: int, full: bool = False) -> User:
    data = await pixiv_request(f"/ajax/user/{id}", params=[("full", int(full))])
    if full:
        return User(data)
    else:
        return PartialUser(data)


async def get_user_profile_top(id: int) -> list[ArtworkEntry]:
    data = await pixiv_request(f"/ajax/user/{id}/profile/top")
    illusts = [ArtworkEntry(data["illusts"][x]) for x in data["illusts"]]
    manga = [ArtworkEntry(data["manga"][x]) for x in data["manga"]]
    return sorted(illusts + manga, key=lambda _: _.id, reverse=True)


async def get_user_illusts(
    id: int, content_type: str = "illust", page: int = 1, tag: str = None
):
    params = [("id", id), ("type", content_type), ("p", page)]

    if tag:
        params.append(("tag", tag))

    data = await pixiv_request("/touch/ajax/user/illusts", params=params)

    return UserPageIllusts(data)


async def get_user_bookmarks(
    id: int, page: int = 1, tag: str = ""
) -> tuple[int, list[ArtworkEntry]]:
    data = await pixiv_request(
        f"/ajax/user/{id}/illusts/bookmarks",
        params=[
            ("tag", tag),
            ("offset", (48 * page) - 48),
            ("limit", 48),
            ("rest", "show"),
        ],
    )
    return data["total"], [ArtworkEntry(x) for x in data["works"]]


async def get_notification_count() -> int:
    data = await pixiv_request(
        f"/rpc/notify_count.php",
        params=[("op", "count_unread")],
        headers={"Referer": "https://www.pixiv.net"},
    )
    return data["popboard"]


async def get_self_extra() -> UserExtraData:
    data = await pixiv_request("/ajax/user/extra")
    return UserExtraData(data)


async def get_user_illusts_from_ids(user_id: int, ids: list[int]) -> list[ArtworkEntry]:
    if len(ids) == 0:
        return []

    data = await pixiv_request(
        f"/ajax/user/{user_id}/illusts", params=[("ids[]", x) for x in ids]
    )
    return [ArtworkEntry(x) for x in data.values()]


async def get_user_following(
    id: int, page: int = 1, rest: str = "show", acceptingRequests: bool = False
) -> list[UserEntry]:

    if rest not in ("show", "hide"):
        raise ValueError("Invalid value for rest")

    data = await pixiv_request(
        f"/ajax/user/{id}/following",
        params=[
            ("offset", (24 * page) - 24),
            ("limit", 24 * page),
            ("rest", rest),
            ("acceptingRequests", int(acceptingRequests)),
        ],
    )

    return UserFollowRes(data)


async def get_user_followers(id: int, page: int = 1):
    data = await pixiv_request(
        f"/ajax/user/{id}/followers",
        params=[("offset", (24 * page) - 24), ("limit", 24 * page)],
    )

    return UserFollowRes(data)


async def get_user_mypixiv(id: int, page: int = 1):
    data = await pixiv_request(
        f"/ajax/user/{id}/mypixiv",
        params=[
            ("offset", (24 * page) - 24),
            ("limit", 24 * page),
        ],
    )

    return UserFollowRes(data)


async def get_series(id: int):
    data = await pixiv_request(f"/ajax/series/{id}")
