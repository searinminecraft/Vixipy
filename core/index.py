
import api

def getLanding(mode: str):

    res = {
            "thumbs": {},
            "recommend": {},
            "recommendByTag": {},
            "tagTranslations": {}
    }

    recommendByTag = {

    }

    data = api.getLanding(mode)["body"]

    for illust in data["thumbnails"]["illust"]:
        res["thumbs"][illust["id"]] = illust

    for r in data["page"]["recommendByTag"]:
        res["recommendByTag"][r["tag"]] = r

    for x in data["tagTranslation"]:
        res["tagTranslations"][x] = data["tagTranslation"][x].get("en")

    return res
