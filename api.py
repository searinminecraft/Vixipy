from flask import g
import requests
import cfg
import time

class PixivError(Exception):
    pass

def getHeaders():

    headers ={
        "Cookie": f"PHPSESSID={g.get('userPxSession') if g.get('userPxSession') else cfg.PxSession}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0", #  tbh maybe I should just use a Windows UA
        "Accept-Language": cfg.PxAcceptLang
    }

    if g.get("userPxCSRF"):
        headers["X-CSRF-Token"] = g.userPxCSRF

    return headers

def pixivReq(endpoint):
    
    start = time.perf_counter()
    req = requests.get("https://www.pixiv.net" + endpoint, headers=getHeaders())
    end = time.perf_counter()

    print(f"Request {req.url} - {req.status_code} - {round((end - start) * 1000)}ms")

    resp = req.json()
    if resp["error"]:
        raise PixivError(resp["message"])

    return resp

def getLanding(mode: str = "all"):
    return pixivReq(f"/ajax/top/illust?mode={mode}")

def getLatestFromFollowing(mode: str, page: int):
    return pixivReq(f"/ajax/follow_latest/illust?mode={mode}&p={page}")

def getUserInfo(userId: int):
    return pixivReq(f"/ajax/user/{userId}?full=1")

def getArtworkInfo(_id: int):
    return pixivReq (f"/ajax/illust/{_id}")

def getArtworkPages(_id: int):
    return pixivReq(f"/ajax/illust/{_id}/pages")

def getDiscovery(mode: str = "all", limit: int = 30):
    return pixivReq(f"/ajax/discovery/artworks?mode={mode}&limit={limit}")
