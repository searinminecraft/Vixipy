from flask import g
import requests
import cfg

class PixivError(Exception):
    pass

def checkSuccess(f):

    def inner(*args, **kwargs):
        r = f(*args, **kwargs)
        try:
            if r["error"] == True:
                raise PixivError(r["message"])
        except Exception:
            raise PixivError(r)

        return r

    return inner

def getHeaders():

    headers ={
        "Cookie": f"PHPSESSID={g.get('userPxSession') if g.get('userPxSession') else cfg.PxSession}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0", #  tbh maybe I should just use a Windows UA
        "Accept-Language": cfg.PxAcceptLang
    }

    if g.get("userPxCSRF"):
        headers["X-CSRF-Token"] = g.userPxCSRF

    return headers

@checkSuccess
def getLanding(mode: str = "all"):

    req = requests.get(f"https://www.pixiv.net/ajax/top/illust?mode={mode}",
                 headers=getHeaders())
    return req.json()

@checkSuccess
def getLatestFromFollowing(mode: str, page: int):

    req = requests.get(f"https://www.pixiv.net/ajax/follow_latest/illust?mode={mode}&p={page}",
                       headers=getHeaders())
    return req.json()

@checkSuccess
def getUserInfo(userId: int):

    req = requests.get(f"https://www.pixiv.net/ajax/user/{userId}?full=1", headers=getHeaders())
    return req.json()

@checkSuccess
def getArtworkInfo(_id: int):

    req = requests.get(f"https://www.pixiv.net/ajax/illust/{_id}", headers=getHeaders())
    return req.json()

@checkSuccess
def getArtworkPages(_id: int):

    req = requests.get(f"https://www.pixiv.net/ajax/illust/{_id}/pages", headers=getHeaders())
    return req.json()
