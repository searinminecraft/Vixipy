from flask import g, request, abort
import requests
from . import cfg
import time
from urllib.parse import quote


class PixivError(Exception):
    pass


class UnknownPixivError(Exception):
    pass


def getHeaders(useMobileAgent=False):

    headers = {
        "Cookie": f"PHPSESSID={g.get('userPxSession') if g.get('userPxSession') else cfg.PxSession}",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/132.0"
            if not useMobileAgent
            else "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36"
        ),  #  tbh maybe I should just use a Windows UA
        "Accept-Language": cfg.PxAcceptLang,
    }

    if g.get("userPxCSRF"):
        headers["x-csrf-token"] = g.userPxCSRF

    return headers


def pixivReq(endpoint, additionalHeaders: dict = {}, useMobileAgent=False):

    start = time.perf_counter()
    req = requests.get(
        "https://www.pixiv.net" + endpoint,
        headers={**getHeaders(useMobileAgent), **additionalHeaders},
    )
    end = time.perf_counter()

    print(
        f"PIXIVAPI | Request {req.url} - {req.status_code} - {round((end - start) * 1000)}ms [{request.user_agent}]"
    )

    if req.status_code == 429:
        raise PixivError("Rate limited")

    if req.status_code == 404:
        abort(404)

    try:
        resp = req.json()
    except Exception:
        raise UnknownPixivError(str(req.status_code) + ": " + req.text) from None

    # isSucceed is used on mobile ajax API, while error is used for regular ajax API
    if not resp.get("isSucceed", False) or resp.get("error", False):

        if resp.get("error"):
            try:
                raise PixivError(resp["message"])
            except KeyError:
                try:
                    raise PixivError(resp["error"])
                except KeyError:
                    raise PixivError("Unknown error")

    return resp


def pixivPostReq(
    endpoint,
    *,
    jsonPayload: dict = None,
    rawPayload: str = None,
    additionalHeaders: dict = {},
    useMobileAgent: bool = False,
):
    """
    Send a POST request to pixiv.

    Params:

    endpoint: the endpoint path to send a request to
    jsonPayload: the payload as a dict
    rawPayload: the raw url-encoded payload
    additionalHeaders: additional headers to pass
    useMobileAgent: whether to use a mobile user agent
    """

    start = time.perf_counter()
    if jsonPayload:
        req = requests.post(
            "https://www.pixiv.net" + endpoint, headers=getHeaders(), json=jsonPayload
        )
    elif rawPayload:
        origHeaders = getHeaders()

        req = requests.post(
            "https://www.pixiv.net" + endpoint,
            headers={
                **origHeaders,
                **additionalHeaders,
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            },
            data=rawPayload,
        )
    else:
        raise TypeError("Neither json payload nor raw payload were provided.")
    end = time.perf_counter()

    print(
        f"PIXIVAPI | POST {req.url} - {req.status_code} - {round((end - start) * 1000)}ms -- [{request.user_agent}]"
    )

    resp = req.json()
    # isSucceed is used on mobile ajax API, while error is used for regular ajax API
    if not resp.get("isSucceed", False) or resp.get("error", False):

        if resp.get("error"):
            try:
                raise PixivError(resp["message"])
            except KeyError:
                try:
                    raise PixivError(resp["error"])
                except KeyError:
                    raise PixivError("Unknown error")

    return resp


def getLanding(mode: str = "all"):
    """
    Get the landing page. Usually the front page of pixiv
    """
    return pixivReq(f"/ajax/top/illust?mode={mode}")


def getLatestFromFollowing(mode: str, page: int):
    """
    Get the latest works from users the user is following
    """
    return pixivReq(f"/ajax/follow_latest/illust?mode={mode}&p={page}")


def getUserInfo(userId: int):
    """
    Get information about a user
    """
    return pixivReq(f"/ajax/user/{userId}?full=1")


def getArtworkInfo(_id: int):
    """
    Get information about an artwork
    """
    return pixivReq(f"/ajax/illust/{_id}")


def getArtworkPages(_id: int):
    """
    Get the pages of an artwork
    """
    return pixivReq(f"/ajax/illust/{_id}/pages")


def getArtworkComments(_id: int, offset: int = 0, limit: int = 100):
    """
    Get artwork comments
    """
    return pixivReq(
        f"/ajax/illusts/comments/roots?illust_id={_id}&offset={offset}&limit={limit}"
    )


def getArtworkReplies(comment_id: int, page: int = 1):
    """
    Get Artwork Replies
    """

    return pixivReq(
        f"/ajax/illusts/comments/replies?comment_id={comment_id}&page={page}"
    )


def getDiscovery(mode: str = "all", limit: int = 30):
    """
    Get the artworks on discovery
    """
    return pixivReq(f"/ajax/discovery/artworks?mode={mode}&limit={limit}")


def getRelatedArtworks(_id: int, limit: int = 30):
    """
    Get the related artworks for an artwork
    """
    return pixivReq(f"/ajax/illust/{_id}/recommend/init?limit={limit}")


def getRanking(
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

    return pixivReq(path)


# holy shit.
def searchArtwork(
    keyword: str,
    *,
    order: str = None,
    mode: str = "safe",
    s_mode: str = "s_tag",
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

    path = f"/ajax/search/artworks/{keyword}?word={keyword}&mode={mode}&s_mode={s_mode}&p={p}"

    if order:
        path += f"&order=order"

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

    return pixivReq(path)


def getTagInfo(tag: str):
    """
    Get information about a tag
    """

    return pixivReq(f"/ajax/search/tags/{tag}")


def getUserBookmarks(_id: int, tag: str = "", offset: int = 0, limit: int = 30):
    """
    Get a user's bookmarks
    """

    return pixivReq(
        f"/ajax/user/{_id}/illusts/bookmarks?tag={tag}&offset={offset}&limit={limit}&rest=show"
    )


def getNewestArtworks(
    lastId: int = 0, limit: int = 20, _type: str = "illust", r18: bool = False
):
    """Get newest artworks"""

    return pixivReq(
        f"/ajax/illust/new?lastId={lastId}&limit={limit}&type={_type}&r18={str(r18).lower()}"
    )


def getRecommendedUsers(limit: int = 10):
    """Get recommended users (shown in pixiv landing page)"""

    return pixivReq(f"/ajax/discovery/users?limit={limit}")


def getUserArtworks(_id: int):

    return pixivReq(f"/ajax/user/{_id}/profile/all")


def getUserIllustEntries(
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

    return pixivReq(path)


def getUserSettings():

    return pixivReq("/ajax/settings")


def getUserSettingsState():

    return pixivReq("/ajax/settings/self")


def getNotifications():

    return pixivReq("/ajax/notification")


def postComment(illustId: int, authorId: int, comment: str):

    return pixivPostReq(
        "/rpc/post_comment.php",
        rawPayload=f"type=comment&illust_id={illustId}&author_user_id={authorId}&comment={quote(comment)}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net/",
            "Referer": f"https://www.pixiv.net/en/artworks/{illustId}",
            "Accept": "application/json",
        },
    )


def postStamp(illustId: int, authorId: int, stampId: int):
    return pixivPostReq(
        "/rpc/post_comment.php",
        rawPayload=f"type=stamp&illust_id={illustId}&author_user_id={authorId}&stamp_id={stampId}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net/",
            "Referer": f"https://www.pixiv.net/en/artworks/{illustId}",
            "Accept": "application/json",
        },
    )


def getUserIllustManga(_id: int):

    return pixivReq(f"/ajax/user/{_id}/profile/all")


def getUserLatestIllusts(_id: int):

    return pixivReq(f"/ajax/user/{_id}/works/latest")


def getUserTopIllusts(_id: int):
    return pixivReq(f"/ajax/user/{_id}/profile/top")


def retrieveUserIllusts(_id: int, illustIds: list[int]):
    path = f"/ajax/user/{_id}/profile/illusts?work_category=illustManga&is_first_page=1"

    for x in range(len(illustIds)):
        path += f"&ids[]={illustIds[x]}"

    return pixivReq(path)


def getUserFollowing(_id: int, offset: int = 0, limit: int = 30):
    return pixivReq(
        f"/ajax/user/{_id}/following?offset={offset}&limit={limit}&rest=show"
    )


def getUserFollowers(_id: int, offset: int = 0, limit: int = 30):
    return pixivReq(
        f"/ajax/user/{_id}/followers?offset={offset}&limit={limit}&rest=show"
    )


def addTagToFavorites(tag: str):
    return pixivPostReq(f"/ajax/favorite_tags/save", jsonPayload={"tags": [tag]})


def followUser(_id: int, restrict: bool = False):
    return pixivPostReq(
        "/touch/ajax_api/ajax_api.php",
        useMobileAgent=True,
        rawPayload=f"mode=add_bookmark_user&restrict={int(restrict)}&user_id={_id}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net",
            "Referer": f"https://www.pixiv.net/en/users/{_id}",
        },
    )


def unfollowUser(_id: int):
    return pixivPostReq(
        "/touch/ajax_api/ajax_api.php",
        useMobileAgent=True,
        rawPayload=f"mode=delete_bookmark_user&user_id={_id}",
        additionalHeaders={
            "Origin": "https://www.pixiv.net",
            "Referer": f"https://www.pixiv.net/en/users/{_id}",
        },
    )


def getFrequentTags(ids: list[int]):
    """Get frequent tags based on illust IDs"""

    path = "/ajax/tags/frequent/illust"

    for k, v in enumerate(ids):
        if k == 0:
            path += f"?ids[]={int(v)}"
        else:
            path += f"&ids[]={int(v)}"

    return pixivReq(path)
