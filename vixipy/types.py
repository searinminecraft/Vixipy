from .converters import proxy, convert_pixiv_link
from datetime import datetime
from quart import request
import markupsafe
from bs4 import BeautifulSoup

from typing import Optional

NO_IMAGE = "https://s.pximg.net/common/images/no_profile.png"
NO_IMAGE_S = "https://s.pximg.net/common/images/no_profile_s.png"


def blank_to_none(v) -> Optional[str]:
    return v if v != "" else None


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
        self.uploadDate_raw = d["createDate"]
        self.bookmarked = d.get("bookmarkData") is not None
        self.bookmark_id = d["bookmarkData"]["id"] if d.get("bookmarkData") else None
        self.bookmark_private = (
            d["bookmarkData"]["private"] if d.get("bookmarkData") else False
        )
        self.uploadDate = datetime.fromisoformat(self.uploadDate_raw)
        self.xrestrict = d["xRestrict"]
        self.r18 = self.xrestrict >= 1
        self.r18g = self.xrestrict == 2
        self.sl = d["sl"]
        self.sensitive = self.sl >= 4
        self.alt = d["alt"]
        self.authorId = d["userId"]
        self.authorName = d["userName"]
        self.pages = int(d["pageCount"])
        self.ai = int(d["aiType"]) == 2
        self.isUgoira: bool = self.type == 2

        self.json: dict = d

    @property
    def xrestrict_friendlyname(self):
        names = {1: "R-18", 2: "R-18G"}

        return names.get(int(self.xrestrict), "R-18")


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

        self.thumb = proxy(d["urls"]["regular"])
        self.authorHandle = d["userAccount"]
        self.width = d["width"]
        self.height = d["height"]
        self.bookmarkCount = d["bookmarkCount"]
        self.likeCount = d["likeCount"]
        self.liked = d["likeData"]
        self.commentCount = d["commentCount"]
        self.viewCount = d["viewCount"]
        self.deficient = d["urls"]["regular"] is None

        self.original = d["isOriginal"]
        self.loginonly = d["isLoginOnly"]
        self.ai = d["aiType"] == 2
        self.description = d["illustComment"]
        self.description_stripped = markupsafe.Markup(self.description).striptags()

        self.other_works: list[ArtworkEntry] = []
        self.works_missing: list[int] = []

        for x in d["userIllusts"]:
            if d["userIllusts"][x] is None:
                self.works_missing.append(int(x))
            else:
                self.other_works.append(ArtworkEntry(d["userIllusts"][x]))


class ArtworkEntry(ArtworkBase):
    def __init__(self, d):
        super().__init__(d)
        self.unproxied_thumb = d["url"]
        self.thumb = proxy(self.unproxied_thumb)
        self.profileimg = proxy(d.get("profileImageUrl"))
        self.tags: list[str] = d.get("tags", [])

    def __repr__(self):
        return f"<ArtworkEntry {self.id}>"


class RankingEntry(ArtworkEntry):
    def __init__(self, d):
        _cd = datetime.strptime(d["date"], "%Y年%m月%d日 %H:%M")
        super().__init__(
            {
                "id": d["illust_id"],
                "title": d["title"],
                "description": None,
                "illustType": d["illust_type"],
                "createDate": _cd.isoformat(),
                "xRestrict": 0,
                "sl": 2,
                "alt": "",
                "userId": d["user_id"],
                "userName": d["user_name"],
                "pageCount": d["illust_page_count"],
                "aiType": 0,
                "url": d["url"],
                "profileImageUrl": d["profile_img"],
                "bookmarkData": (
                    {
                        "id": int(d["bookmark_id"]),
                        "private": int(d["bookmark_illust_restrict"]) == 1,
                    }
                    if d.get("is_bookmarked")
                    else None
                ),
                "tags": "",
            }
        )
        self.rank: int = int(d["rank"])


class RankingData:
    def __init__(self, d):
        self.page: int = d["page"]
        self.prev: Optional[int] = d["prev"] if d["prev"] != False else None
        self.next: Optional[int] = d["next"] if d["next"] != False else None
        self.date_r: str = d["date"]
        self.date: datetime = datetime.strptime(self.date_r, "%Y%m%d")
        self.prev_date_r: Optional[str] = (
            d["prev_date"] if d["prev_date"] != False else None
        )
        self.prev_date: Optional[datetime] = (
            datetime.strptime(self.prev_date_r, "%Y%m%d") if self.prev_date_r else None
        )
        self.next_date_r: Optional[str] = (
            d["next_date"] if d["next_date"] != False else None
        )
        self.next_date: Optional[datetime] = (
            datetime.strptime(self.next_date_r, "%Y%m%d") if self.next_date_r else None
        )
        self.mode: str = d["mode"]
        self.content: str = d["content"]
        self.contents: list[RankingEntry] = []

        for x in d["contents"]:
            self.contents.append(RankingEntry(x))


class NovelBase:
    def __init__(self, d: dict):
        self.ai: int = d["aiType"] == 2
        self.bookmark_count: int = d["bookmarkCount"]
        self.create_date: datetime = datetime.fromisoformat(
            d.get("createDate") or d.get("createDateTime")
        )
        self.genre_id: int = int(d["genre"])
        self.id: int = int(d["id"])
        self.original: bool = d["isOriginal"]
        self.reading_time: int = d["readingTime"]
        self.tags: list[str] = d["tags"]
        self.title: str = d["title"]
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.word_count: int = d["wordCount"]
        self.character_count: int = int(
            d.get("characterCount") or d.get("textCount") or d.get("textLength")
        )
        self.xrestrict = d["xRestrict"]

    @property
    def xrestrict_friendlyname(self):
        names = {1: "R-18", 2: "R-18G"}

        return names.get(int(self.xrestrict), "R-18")


class NovelSeriesEntry(NovelBase):
    def __init__(self, d):
        super().__init__(d)
        self.cover: str = proxy(d["cover"]["urls"]["240mw"])
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.oneshot: bool = d["isOneshot"]
        self.caption: str = d["caption"]
        self.concluded: bool = d["isConcluded"]
        self.episode_count: int = d["episodeCount"]
        self.published_episode_count: int = d["publishedEpisodeCount"]
        self.latest_published_date: datetime = datetime.fromisoformat(
            d["latestPublishDateTime"]
        )
        self.latest_episode_id: int = int(d["latestEpisodeId"])
        self.watched: bool = d["isWatched"]
        self.notifying: bool = d["isNotifying"]
        self.published_character_count: int = d["publishedTextLength"]
        self.published_word_count: int = d["publishedWordCount"]
        self.published_reading_time: int = d["publishedReadingTime"]


class NovelSeries:
    def __init__(self, d):
        self.id: int = int(d["id"])
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.xrestrict: int = d["xRestrict"]
        self.original: bool = d["isOriginal"]
        self.concluded: bool = d["isConcluded"]
        self.genre_id: int = int(d["genreId"])
        self.title: str = d["title"]
        self.caption: str = d["caption"]
        self.language: str = d["language"]
        self.tags: list[str] = d["tags"]
        self.published_content_count: int = d["publishedContentCount"]
        self.published_character_count: int = d["publishedTotalCharacterCount"]
        self.published_word_count: int = d["publishedTotalWordCount"]
        self.published_reading_time: int = d["publishedReadingTime"]
        self.latest_published_date: datetime = datetime.fromtimestamp(
            d["lastPublishedContentTimestamp"]
        )
        self.created_date: datetime = datetime.fromtimestamp(d["createdTimestamp"])
        self.updated_date: datetime = datetime.fromtimestamp(d["updatedTimestamp"])
        self.first_novel_id: int = int(d["firstNovelId"])
        self.lastest_novel_id: int = int(d["latestNovelId"])
        self.total: int = d["total"]
        self.cover: str = proxy(d["cover"]["urls"]["480mw"])
        self.watched: bool = d["isWatched"]
        self.ai: bool = d["aiType"] == 2
        self.has_glossary: bool = d["hasGlossary"]


class NovelSeriesNav:
    def __init__(self, d):
        self.title: str = d["title"]
        self.order: int = d["order"]
        self.id: int = int(d["id"])
        self.available: bool = d["available"]


class NovelSeriesNavData:
    def __init__(self, d):
        self.series_id: int = d["seriesId"]
        self.title: str = d["title"]
        self.concluded: bool = d["isConcluded"]
        self.watched: bool = d["isWatched"]
        self.notifying: bool = d["isNotifying"]
        self.order: int = d["order"]
        self.prev: NovelSeriesNav = NovelSeriesNav(d["prev"]) if d["prev"] else None
        self.next: NovelSeriesNav = NovelSeriesNav(d["next"]) if d["next"] else None


class NovelEntry(NovelBase):
    def __init__(self, d):
        super().__init__(d)
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.description: str = d["description"]
        self.bookmarked = d["bookmarkData"] is not None
        self.cover = proxy(d["url"])


class Novel(NovelBase):
    def __init__(self, d):
        super().__init__(d)
        self.description: str = d["description"]
        self.view_count: int = d["viewCount"]
        self.bungei: bool = d["isBungei"]
        self.content: str = d["content"]
        self.cover: str = proxy(d["coverUrl"])
        self.bookmarked: bool = d["bookmarkData"] is not None
        self.liked: bool = d["likeData"]
        self.tags: list[str] = [x["tag"] for x in d["tags"]["tags"]]
        self.series_nav_data: Optional[NovelSeriesNavData] = (
            NovelSeriesNavData(d["seriesNavData"]) if d["seriesNavData"] else None
        )
        self.user_novels: list[NovelEntry] = []

        for x in d["userNovels"].values():
            if x is not None:
                self.user_novels.append(NovelEntry(x))

        self.comment_count: int = d["commentCount"]
        self.commentOff: bool = bool(d["commentOff"])
        self.language: str = d["language"]


class ArtworkPage:
    def __init__(self, d, page):
        self.reg = proxy(d["urls"]["regular"])
        self.orig = proxy(d["urls"]["original"])
        self.width = d["width"]
        self.height = d["height"]
        self.page = page


class TagTranslation:
    def __init__(self, orig: str, d):
        self.orig: str = orig
        self.en: Optional[str] = d.get("en") or None
        self.ko: Optional[str] = d.get("ko") or None
        self.zh: Optional[str] = d.get("zh") or None
        self.zh_tw: Optional[str] = d.get("zh_tw") or None
        self.romaji: Optional[str] = d.get("romaji") or None

    @property
    def default(self):
        pref = request.cookies.get("Vixipy-Language", "en") or "en"
        if all([not self.en, not self.ko, not self.zh, not self.zh_tw]):
            return self.orig
        if pref == "en":
            return self.en or self.romaji or self.orig
        if pref == "ko":
            return self.ko or self.romaji or self.orig
        if pref == "ja":
            return self.orig
        if pref == "zh_Hans":
            return self.zh or self.orig
        if pref == "zh_Hant":
            return self.zh_tw or self.orig
        return self.en or self.romaji or self.orig

    def __repr__(self):
        return f"<TagTranslation {self.orig} default={self.default}>"


class RecommendByTag:
    def __init__(
        self, illusts: list[ArtworkEntry], name: str, translation: TagTranslation
    ):
        self.illusts = illusts
        self.name = name
        self.translation = translation


class SearchResultsBase:
    def __init__(
        self,
        d,
    ):
        _related_tags = d["relatedTags"]
        _tag_translation = d["tagTranslation"]
        if isinstance(_tag_translation, list):
            self.related_tags = [Tag(x, None) for x in _related_tags]
        else:
            if isinstance(_related_tags, list):
                self.related_tags = _related_tags
            else:
                self.related_tags = [
                    Tag(x, _tag_translation.get(x, {"en": None})["en"])
                    for x in _related_tags
                ]


class SearchResultsTop(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total_novel: int = d["novel"]["total"]
        self.novels: list[NovelEntry] = [NovelEntry(x) for x in d["novel"]["data"]]
        if im := d.get("illustManga"):
            self.total_illustmanga: int = d["illustManga"]["total"]
            self.total: int = self.total_illustmanga + d["novel"]["total"]
            self.results: list[ArtworkEntry] = [
                ArtworkEntry(x) for x in d["illustManga"]["data"]
            ]
        else:
            _illusts = d["illust"]
            _manga = d["manga"]

            self.total_illustmanga: int = _illusts["total"] + _manga["total"]
            self.total = self.total_illustmanga + d["novel"]["total"]
            self.results: list[ArtworkEntry] = sorted(
                [ArtworkEntry(x) for x in _illusts["data"]]
                + [ArtworkEntry(x) for x in _manga["data"]],
                key=lambda _: _.id,
                reverse=True,
            )

        _popular = d["popular"]
        self.popular_recent = [ArtworkEntry(x) for x in _popular["recent"]]
        self.popular_permanent = [ArtworkEntry(x) for x in _popular["permanent"]]


class SearchResultsIllust(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["illust"]["total"]
        self.last: int = d["illust"]["lastPage"]
        self.results: list[ArtworkEntry] = []

        for x in d["illust"]["data"]:
            if x.get("isAdContainer"):
                continue
            self.results.append(ArtworkEntry(x))


class SearchResultsManga(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["manga"]["total"]
        self.last: int = d["manga"]["lastPage"]
        self.results: list[ArtworkEntry] = []

        for x in d["manga"]["data"]:
            if x.get("isAdContainer"):
                continue
            self.results.append(ArtworkEntry(x))


class SearchResultsNovel(SearchResultsBase):
    def __init__(self, d):
        super().__init__(d)
        self.total: int = d["novel"]["total"]
        self.results: list[NovelEntry] = [NovelEntry(x) for x in d["novel"]["data"]]
        self.last: int = d["novel"]["lastPage"]


class PixpediaInfo:
    def __init__(self, d):
        self.abstract: Optional[str] = d.get("abstract")
        self.image: Optional[str] = proxy(d.get("image"))


class TagInfo:
    def __init__(self, d):
        self.tag = d["tag"]
        self.pixpedia: PixpediaInfo = PixpediaInfo(d["pixpedia"])
        self.translation: Optional[TagTranslation] = None
        self.favorite_tags: list[str] = d["myFavoriteTags"]
        self.is_favorite: bool = self.tag in self.favorite_tags
        if self.tag in d["tagTranslation"]:
            self.translation = TagTranslation(self.tag, d["tagTranslation"][self.tag])


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


class CommentBase:
    def __init__(self, d):
        self.id: int = int(d["id"])
        self.user_id: int = int(d["userId"])
        self.username: str = d["userName"]
        self.img: str = proxy(d["img"])
        self.comment: str = d["comment"]
        self.stamp_id: Optional[int] = int(d["stampId"]) if d["stampId"] else None
        self.date: datetime = datetime.strptime(d["commentDate"], "%Y-%m-%d %H:%M")
        self.editable: bool = d["editable"]

    @property
    def stamp_image(self):
        return (
            f"/proxy/s.pximg.net/common/images/stamp/generated-stamps/{self.stamp_id}_s.jpg"
            if self.stamp_id
            else None
        )


class Comment(CommentBase):
    def __init__(self, d):
        super().__init__(d)
        self.is_deleted_user: bool = d["isDeletedUser"]
        self.has_replies: bool = d["hasReplies"]


class CommentBaseResponse:
    def __init__(self, comments: list[Comment], has_next: bool):
        self.comments: list[Comment] = comments
        self.has_next: bool = has_next


class NewIllustResponse:
    def __init__(self, d):
        self.last_id: int = int(d["lastId"])
        self.illusts: list[ArtworkEntry] = [ArtworkEntry(x) for x in d["illusts"]]


class CollectionEntry:
    def __init__(self, d):
        self.id: int = int(d["id"])
        self.user_id: int = int(d["userId"])
        self.user_name: str = d["userName"]
        self.profile_image: str = proxy(d["profileImageUrl"])
        self.title: str = d["title"]
        self.tags: list[str] = d["tags"]
        self.caption: Optional[str] = d["caption"] or None
        self.language: str = d["language"]
        self.sl: int = d["sl"]
        self.sensitive: bool = self.sl >= 4
        self.xrestrict: int = d["xRestrict"]
        self.bookmark_count: int = d["bookmarkCount"]
        self.is_bookmarked: bool = d["bookmarkData"] is not None
        self.comment_off: bool = d["commentOff"]
        self.spoiler: bool = d["isSpoiler"]
        self.bookmarkable: bool = d["isBookmarkable"]
        self.view_count: int = d["viewCount"]
        self.cited_data_hash: str = d["citedDataHash"]
        self.status: str = d["status"]
        self.published: datetime = (
            datetime.strptime(d["publishedDateTime"], "%Y-%m-%d %H:%M:%S"),
        )
        self.thumb = proxy(d["thumbnailImageUrl"])

    def __repr__(self):
        return f"<CollectionEntry title={self.title} id={self.id} user_id={self.user_id} user_name={self.user_name}>"
