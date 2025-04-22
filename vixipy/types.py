from .converters import proxy
from datetime import datetime

class PartialUser:
    def __init__(self, d):
        self.id = d["userId"]
        self.name = d["name"]
        self.image = proxy(d["image"])
        self.imageBig = proxy(d["imageBig"])
        self.premium = d["premium"]
        self.followed = d["isFollowed"]
        self.isMypixiv = d["isMypixiv"]
        self.blocked = d["isBlocking"]
        self.background = proxy(d["background"]["url"]) if d["background"] else None

class User(PartialUser):
    def __init__(self, d):
        super().__init__(d)
        self.following = d["following"]
        self.mypixiv = d["mypixivCount"]
        self.followedBack = d["followedBack"]
        self.comment = d["comment"]
        self.webpage = d["webpage"]
        self.official = d["official"]

class UserExtraData:
    def __init__(self, d):
        self.following = d["following"]
        self.followers = d["followers"]
        self.mypixivCount = d["mypixivCount"]
        self.background = proxy(d["background"]["url"]) if d["background"] else None

class Tag:
    def __init__(self, name, en=None, romaji=None):
        self.name = name
        self.en = en
        self.romaji = romaji

class ArtworkBase:
    def __init__(self, d):
        self.id = d["id"]
        self.title = d["title"]
        self.description = d["description"]
        self.type = d["illustType"]
        self.uploadDate = datetime.fromisoformat(d["createDate"])
        self.xrestrict = d["xRestrict"]
        self.r18 = self.xrestrict >= 1
        self.r18g = self.xrestrict == 2
        self.sl = d["sl"]
        self.sensitive = self.sl >= 4
        self.alt = d["alt"]
        self.authorId = d["userId"]
        self.authorName = d["userName"]

class Artwork(ArtworkBase):
    def __init__(self, d):
        super().__init__(d)
        self.tags: list[Tag] = []
        for t in d["tags"]["tags"]:
            if _r := t.get("romaji"):
                _romaji = _r
            else:
                _romaji = None
            if _t := t.get("translation"):
                _en = _t["en"]
            else:
                _en = None
            
            self.tags.append(Tag(t["tag"], _en, _romaji))

        self.authorHandle = d["userAccount"]
        self.width = d["width"]
        self.height = d["height"]

        self.pageCount = d["pageCount"]
        self.bookmarkCount = d["bookmarkCount"]
        self.likeCount = d["likeCount"]
        self.commentCount = d["commentCount"]
        self.viewCount = d["viewCount"]

        self.original = d["isOriginal"]
        self.loginonly = d["isLoginOnly"]
        self.ai = d["aiType"] == 2


class ArtworkEntry(ArtworkBase):
    def __init__(self, d):
        super().__init__(d)
        self.thumb = proxy(d["url"])
        self.profileimg = proxy(d["profileImageUrl"])

class ArtworkPage:
    def __init__(self, d):
        self.reg = proxy(d["urls"]["regular"])
        self.orig = proxy(d["urls"]["original"])