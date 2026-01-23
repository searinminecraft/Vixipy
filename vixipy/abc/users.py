from __future__ import annotations

from .artworks import ArtworkEntry
from ..converters import proxy, convert_pixiv_link
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional


class PartialUser:
    def __init__(self, d):
        self.id = int(d["userId"])
        self.name = d["name"]
        self.image = proxy(d["image"])
        self.imageBig = proxy(d["imageBig"])
        self.premium = d["premium"]
        self.followed = d["isFollowed"]
        self.isMypixiv = d["isMypixiv"]
        self.blocked = d["isBlocking"]
        self.background = proxy(d["background"]["url"]) if d["background"] else None


class UserSocials:
    def __init__(self, d):
        self.twitter_o = d["twitter"]["url"] if "twitter" in d else None
        self.twitter = convert_pixiv_link(self.twitter_o)
        self.instagram_o = d["instagram"]["url"] if "instagram" in d else None
        self.instagram = convert_pixiv_link(self.instagram_o)
        self.facebook_o = d["facebook"]["url"] if "facebook" in d else None
        self.facebook = convert_pixiv_link(self.facebook_o)
        self.pawoo = "pawoo" in d


class User(PartialUser):
    def __init__(self, d):
        super().__init__(d)
        self.following = d["following"]
        self.mypixiv = d["mypixivCount"]
        self.followedBack = d["followedBack"]
        self.comment = d["comment"]
        self.webpage = d["webpage"]
        self.official = d["official"]
        self.social = UserSocials(d["social"])
        self.comment = d["comment"]

        if d["commentHtml"] != "":
            self.comment_html = BeautifulSoup(d["commentHtml"])

            for x in self.comment_html.find_all("a"):
                x.attrs["href"] = convert_pixiv_link(x.attrs["href"])
        else:
            self.comment_html = None


class UserExtraData:
    def __init__(self, d):
        self.following = d["following"]
        self.followers = d["followers"]
        self.mypixivCount = d["mypixivCount"]
        self.background = proxy(d["background"]["url"]) if d["background"] else None


class CommissionInfo:
    def __init__(self, d: dict):
        self.accept_request: bool = d["acceptRequest"]
        self.is_subscribed_reopen_notification: bool = d[
            "isSubscribedReopenNotification"
        ]


class UserRecommendObject(PartialUser):
    def __init__(self, d: dict):
        super().__init__(d)
        self.comment: str = d["comment"]


class UserEntry:
    def __init__(self, user: UserRecommendObject, illusts: list[ArtworkEntry]):
        self.user: UserRecommendObject = user
        self.illusts: list[ArtworkEntry] = illusts

    def __repr__(self):
        return f"<RecommendedUser user={self.user} recent={self.illusts}>"


class UserFollowObject:
    def __init__(self, d: dict):
        self.id: int = d["userId"]
        self.name: str = d["userName"]
        self.image: str = proxy(d["profileImageSmallUrl"])
        self.imageBig: str = proxy(d["profileImageUrl"])
        self.comment: str = d["userComment"]
        self.followed: bool = d["following"]
        self.followedBack: bool = d["followed"]
        self.blocked: bool = d["isBlocking"]
        self.isMypixiv: bool = d["isMypixiv"]
        self.commission: Optional[CommissionInfo] = (
            CommissionInfo(d["commission"]) if d.get("commission") else None
        )


class UserFollowRes:
    def __init__(self, d: dict):
        self.total: int = int(d["total"])
        self.users: list[UserEntry] = []

        pages, r = divmod(self.total, 24)
        if r > 0:
            pages += 1

        self.pages = pages

        for x in d["users"]:
            user: UserFollowObject = UserFollowObject(x)
            illusts: list[ArtworkEntry] = []

            for y in x["illusts"]:
                illusts.append(ArtworkEntry(y))

            self.users.append(UserEntry(user, illusts))


class UserPageIllusts:
    def __init__(self, d: dict):
        self.total: int = d["total"]
        self.last_page: int = d["lastPage"]
        self.illusts: list[ArtworkEntry] = [
            ArtworkEntry(
                {
                    "id": int(x["id"]),
                    "title": x["title"],
                    "description": x["comment"],
                    "illustType": x["type"],
                    "createDate": datetime.fromtimestamp(
                        x["upload_timestamp"]
                    ).isoformat(),
                    "xRestrict": int(x["x_restrict"]),
                    "sl": x["sl"],
                    "userId": int(x["author_details"]["user_id"]),
                    "userName": x["author_details"]["user_name"],
                    "alt": x["alt"],
                    "aiType": x["ai_type"],
                    "pageCount": x["page_count"],
                    "url": x["url_s"],
                    "profileImageUrl": None,
                }
            )
            for x in d["illusts"]
        ]
