from flask import g
import requests
from . import cfg
import time
from urllib.parse import quote


class PixivError(Exception):
    pass


def getHeaders():

    headers = {
        "Cookie": f"PHPSESSID={g.get('userPxSession') if g.get('userPxSession') else cfg.PxSession}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",  #  tbh maybe I should just use a Windows UA
        "Accept-Language": cfg.PxAcceptLang,
    }

    if g.get("userPxCSRF"):
        headers["x-csrf-token"] = g.userPxCSRF

    return headers


def pixivReq(endpoint, additionalHeaders: dict = {}):

    start = time.perf_counter()
    req = requests.get("https://www.pixiv.net" + endpoint, headers={
        **getHeaders(), **additionalHeaders
        })
    end = time.perf_counter()

    print(
        f"PIXIVAPI | Request {req.url} - {req.status_code} - {round((end - start) * 1000)}ms"
    )

    resp = req.json()
    if resp.get("error"):
        raise PixivError(resp["message"])

    return resp


def pixivPostReq(
    endpoint,
    *,
    jsonPayload: dict = None,
    rawPayload: str = None,
    additionalHeaders: dict = {},
):
    """
    Send a POST request to pixiv.

    Params:

    endpoint: the endpoint path to send a request to
    jsonPayload: the payload as a dict
    rawPayload: the raw url-encoded payload
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
        f"PIXIVAPI | POST {req.url} - {req.status_code} - {round((end - start) * 1000)}ms"
    )

    resp = req.json()
    if resp["error"]:
        raise PixivError(resp["message"])

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
    path = f"/ranking.php?format=json&mode={mode}&p={p}"

    if date:
        path += f"&date={date}"

    if content:
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


def getNewestArtworks():
    """Get newest artworks"""

    return pixivReq("/ajax/illust/new")


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
