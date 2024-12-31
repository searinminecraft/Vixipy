from quart import current_app, g, abort
from . import cfg
import time
from urllib.parse import quote
import logging
import random

log = logging.getLogger("vixipy.api")


class PixivError(Exception):
    pass


class UnknownPixivError(Exception):
    pass


async def pixivReq(
    method,
    endpoint,
    additionalHeaders: dict = {},
    useMobileAgent=False,
    *,
    jsonPayload: dict = None,
    rawPayload: str = None,
):

    headers = {
            "Accept-Language": cfg.PxAcceptLang
    }

    if g.userPxSession:
        headers["Cookie"] = f"PHPSESSID={g.userPxSession}"
    else:
        mockSessionId = "".join([chr(random.randint(97, 122)) for _ in range(33)])

        headers["Cookie"] = f"PHPSESSID={mockSessionId}"
    if g.userPxCSRF:
        headers["x-csrf-token"] = g.userPxCSRF
    if useMobileAgent:
        headers["User-Agent"] = (
            "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
        )
    if rawPayload:
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    start = time.perf_counter()
    log.debug({**current_app.pixivApi.headers, **headers})
    req = await current_app.pixivApi.request(
        method,
        endpoint,
        headers={**headers, **additionalHeaders},
        json=jsonPayload,
        data=rawPayload,
    )
    end = time.perf_counter()

    log.debug(f"Request {req.url} - {req.status} - {round((end - start) * 1000)}ms")

    if req.status == 429:
        raise PixivError("Rate limited")

    if req.status == 404:
        abort(404)

    try:
        resp = await req.json()
        log.debug(resp)
    except Exception:
        text = await req.text()
        raise UnknownPixivError(str(req.status) + ": " + text) from None

    # isSucceed is used on mobile ajax API, while error is used for regular ajax API
    if not resp.get("isSucceed", False) or resp.get("error", False):

        if resp.get("error"):
            try:
                log.error(
                    "An error occurred trying to get %s: Status code %d: %s",
                    req.url,
                    req.status,
                    resp["message"],
                )
                raise PixivError(resp["message"])
            except KeyError:
                try:
                    log.error(
                        "An error occurred trying to get %s: Status code %d: %s",
                        req.url,
                        req.status,
                        resp["error"],
                    )
                    raise PixivError(resp["error"])
                except KeyError:
                    log.error(
                        "An unknown error occurred trying to get %s: Status code %d",
                        req.url,
                        req.status,
                    )
                    raise PixivError("Unknown error")

    return resp


async def getLanding(mode: str = "all"):
    """
    Get the landing page. Usually the front page of pixiv
    """
    return await pixivReq("get", f"/ajax/top/illust?mode={mode}")


async def getLatestFromFollowing(mode: str, page: int):
    """
    Get the latest works from users the user is following
    """
    return await pixivReq("get", f"/ajax/follow_latest/illust?mode={mode}&p={page}")


async def getUserInfo(userId: int, full: bool = True):
    """
    Get information about a user
    """
    return await pixivReq("get", f"/ajax/user/{userId}?full={int(full)}")


async def getArtworkInfo(_id: int):
    """
    Get information about an artwork
    """
    return await pixivReq("get", f"/ajax/illust/{_id}")


async def getArtworkPages(_id: int):
    """
    Get the pages of an artwork
    """
    return await pixivReq("get", f"/ajax/illust/{_id}/pages")


async def getArtworkComments(_id: int, offset: int = 0, limit: int = 100):
    """
    Get artwork comments
    """
    return await pixivReq(
        "get",
        f"/ajax/illusts/comments/roots?illust_id={_id}&offset={offset}&limit={limit}",
    )


async def getArtworkReplies(comment_id: int, page: int = 1):
    """
    Get Artwork Replies
    """

    return await pixivReq(
        "get", f"/ajax/illusts/comments/replies?comment_id={comment_id}&page={page}"
    )


async def getDiscovery(mode: str = "all", limit: int = 30):
    """
    Get the artworks on discovery
    """
    return await pixivReq("get", f"/ajax/discovery/artworks?mode={mode}&limit={limit}")


async def getRelatedArtworks(_id: int, limit: int = 30):
    """
    Get the related artworks for an artwork
    """
    return await pixivReq("get", f"/ajax/illust/{_id}/recommend/init?limit={limit}")


async def getRanking(
    *, mode: str = "daily", date: int = None, content: str = None, p: int = 1
):
    """
    Get artwork ranking data
    """
    path = f"/ranking.php?format=json&p={p}"

    if date:
        path += f"&date={date}&mode={mode}"

    if content and content != "":
        path += f"&content={content}"

    return await pixivReq("get", path)


# holy shit.
async def searchArtwork(
    keyword: str,
    *,
    order: str = None,
    mode: str = None,
    s_mode: str = None,
    wlt: int = None,
    wgt: int = None,
    hlt: int = None,
    hgt: int = None,
    ratio: int = None,
    tool: str = None,
    scd: str = None,
    ecd: str = None,
    p: int = 1,
):
    """
    Search artworks

    params: just refer to https://daydreamer-json.github.io/pixiv-ajax-api-docs/#search-artworks
    """

    path = f"/ajax/search/artworks/{keyword}?p={p}"

    if order:
        path += f"&order={order}"

    if mode:
        path += f"&mode={mode}"

    if s_mode:
        path += f"&s_mode={s_mode}"

    if wlt:
        path += f"&wlt={wlt}"

    if hlt:
        path += f"&hlt={hlt}"

    if wgt:
        path += f"&wgt={wgt}"

    if hgt:
        path += f"&hgt={hgt}"

    if ratio:
        path += f"&ratio={ratio}"

    if tool:
        path += f"&tool={tool}"

    if scd:
        path += f"&scd={scd}"

    if ecd:
        path += f"&ecd={ecd}"

    return await pixivReq("get", path)


async def getTagInfo(tag: str):
    """
    Get information about a tag
    """

    return await pixivReq("get", f"/ajax/search/tags/{tag}")


async def getUserBookmarks(_id: int, tag: str = "", offset: int = 0, limit: int = 30):
    """
    Get a user's bookmarks
    """

    return await pixivReq(
        "get",
        f"/ajax/user/{_id}/illusts/bookmarks?tag={tag}&offset={offset}&limit={limit}&rest=show",
    )


async def getNewestArtworks(
    lastId: int = 0, limit: int = 20, _type: str = "illust", r18: bool = False
):
    """Get newest artworks"""

    return await pixivReq(
        "get",
        f"/ajax/illust/new?lastId={lastId}&limit={limit}&type={_type}&r18={str(r18).lower()}",
    )


async def getRecommendedUsers(limit: int = 10):
    """Get recommended users (shown in pixiv landing page)"""

    return await pixivReq("get", f"/ajax/discovery/users?limit={limit}")


async def getUserArtworks(_id: int):

    return await pixivReq("get", f"/ajax/user/{_id}/profile/all")


async def getUserIllustEntries(
    _id: int, *, work_category: str = "illustManga", lang: str = "en", ids: list
):

    path = (
        f"/ajax/user/{_id}/profile/illusts"
        f"?work_category={work_category}"
        "&is_first_page=0"
        f"&lang={lang}"
    )

    for e in ids:
        path += f"&ids[]={e}"

    return await pixivReq("get", path)


async def getUserSettings():

    return await pixivReq("get", "/ajax/settings")


async def getUserSettingsState():

    return await pixivReq("get", "/ajax/settings/self")


async def getNotifications():

    return await pixivReq("get", "/ajax/notification")


async def postComment(illustId: int, authorId: int, comment: str):

    return await pixivReq(
        "post",
        "/rpc/post_comment.php",
        rawPayload=f"type=comment&illust_id={illustId}&author_user_id={authorId}&comment={quote(comment)}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net/",
            "Referer": f"https://www.pixiv.net/en/artworks/{illustId}",
            "Accept": "application/json",
        },
    )


async def postStamp(illustId: int, authorId: int, stampId: int):
    return await pixivReq(
        "post",
        "/rpc/post_comment.php",
        rawPayload=f"type=stamp&illust_id={illustId}&author_user_id={authorId}&stamp_id={stampId}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net/",
            "Referer": f"https://www.pixiv.net/en/artworks/{illustId}",
            "Accept": "application/json",
        },
    )


async def getUserIllustManga(_id: int):

    return await pixivReq("get", f"/ajax/user/{_id}/profile/all")


async def getUserLatestIllusts(_id: int):

    return await pixivReq("get", f"/ajax/user/{_id}/works/latest")


async def getUserTopIllusts(_id: int):
    return await pixivReq("get", f"/ajax/user/{_id}/profile/top")


async def retrieveUserIllusts(_id: int, illustIds: list[int]):
    path = f"/ajax/user/{_id}/profile/illusts?work_category=illustManga&is_first_page=1"

    for x in range(len(illustIds)):
        path += f"&ids[]={illustIds[x]}"

    return await pixivReq("get", path)


async def getUserFollowing(_id: int, offset: int = 0, limit: int = 30):
    return await pixivReq(
        "get", f"/ajax/user/{_id}/following?offset={offset}&limit={limit}&rest=show"
    )


async def getUserFollowers(_id: int, offset: int = 0, limit: int = 30):
    return await pixivReq(
        "get", f"/ajax/user/{_id}/followers?offset={offset}&limit={limit}&rest=show"
    )


async def addTagToFavorites(tag: str):
    return await pixivReq(
        "post", f"/ajax/favorite_tags/save", jsonPayload={"tags": [tag]}
    )


async def followUser(_id: int, restrict: bool = False):
    return await pixivReq(
        "post",
        "/touch/ajax_api/ajax_api.php",
        useMobileAgent=True,
        rawPayload=f"mode=add_bookmark_user&restrict={int(restrict)}&user_id={_id}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net",
            "Referer": f"https://www.pixiv.net/en/users/{_id}",
        },
    )


async def unfollowUser(_id: int):
    return await pixivReq(
        "post",
        "/touch/ajax_api/ajax_api.php",
        useMobileAgent=True,
        rawPayload=f"mode=delete_bookmark_user&user_id={_id}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net",
            "Referer": f"https://www.pixiv.net/en/users/{_id}",
        },
    )


async def getFrequentTags(ids: list[int]):
    """Get frequent tags based on illust IDs"""

    path = "/ajax/tags/frequent/illust"

    for k, v in enumerate(ids):
        if k == 0:
            path += f"?ids[]={int(v)}"
        else:
            path += f"&ids[]={int(v)}"

    return await pixivReq("get", path)
