from flask import g
import requests
import cfg

class PixivError(Exception):
    pass

def checkSuccess(f):

    def inner(*args, **kwargs):
        r = f(*args, **kwargs)
        if r["error"] == True:
            raise PixivError(r["message"])
        return r
    return inner

def getHeaders():

    if g.get('userPxSession'):
        print("using user provided pxsession")

    return {
        "Cookie": f"PHPSESSID={g.get('userPxSession') if g.get('userPxSession') else cfg.PxSession}",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0", #  tbh maybe I should just use a Windows UA
        "Accept-Language": cfg.PxAcceptLang
    }

@checkSuccess
def getLanding():

    req = requests.get("https://www.pixiv.net/ajax/top/illust",
                 headers=getHeaders())
    return req.json()

@checkSuccess
def getLatestFromFollowing(mode: str, page: int):

    req = requests.get(f"https://www.pixiv.net/ajax/follow_latest/illust?mode={mode}&p={page}",
                       headers=getHeaders())
    return req.json()

