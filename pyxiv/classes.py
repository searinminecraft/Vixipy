from .utils.converters import makeProxy, makeJumpPhp
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse, urlunparse
from markupsafe import escape
from quart_rate_limiter import RateLimiterStoreABC
import pymemcache
from .cfg import UgoiraServer, UgoiraServerNeedsDate, UgoiraServerTrusted


#  tbh maybe i should make a Python library
#  that interacts with the pixiv api...


class MemcacheStore(RateLimiterStoreABC):
    """
    A rate limiter store that uses memcached

    address: The address to connect to a memcached instance
    kwargs: Any arguments to pass to the pymemcache.Client
    """

    def __init__(self, address="localhost", **kwargs):
        self._client: pymemcache.Client = None
        self._args = (address, kwargs)

    async def before_serving(self):
        self._client = pymemcache.Client(self._args[0], **self._args[1])

    async def get(self, key: str, default: datetime) -> datetime:
        result = self._client.get(key)
        if result is None:
            return default
        else:
            return datetime.fromtimestamp(float(result.decode()))

    async def set(self, key: str, tat: datetime) -> None:
        ts = tat.timestamp()
        self._client.set(key, ts)

    async def after_serving(self) -> None:
        self._client.close()
        self._client = None


class PartialUser:
    """
    Base class for all user-related classes

    Properties:
    ===========

    `int` _id: The user's ID
    `str` name: The user's name
    `str` comment: The user's biography
    `str` image: The user's profile picture
    `str` imageBig: The user's profile picture in a higher resolution
    `str` background: The user's banner. Returns `None` if not set
    `bool` premium: Whether the user is subscribed to pixiv premium
    """

    def __init__(self, data):

        self._id: int = int(data["userId"])
        self.name: str = data["name"]
        self.comment: str = data.get("comment")
        self.image: str = makeProxy(data["image"])
        self.imageBig: str = makeProxy(data["imageBig"])
        self.premium: bool = data["premium"]
        self.background: str = (
            makeProxy(data["background"]["url"]) if data["background"] else None
        )


class UserSocials:
    def __init__(self, data):
        self.twitter = (
            makeJumpPhp(data["twitter"]["url"]) if "twitter" in data else None
        )
        self.x = self.twitter
        self.mastodon = makeJumpPhp(data["pawoo"]["url"]) if "pawoo" in data else None
        self.pawoo = self.mastodon
        self.instagram = (
            makeJumpPhp(data["instagram"]["url"]) if "instagram" in data else None
        )
        self.facebook = (
            makeJumpPhp(data["facebook"]["url"]) if "facebook" in data else None
        )


class User(PartialUser):
    """
    Represents a user
    This is a subclass of `PartialUser`

    Properties:
    ===========

    `int` following: The amount of users the user is following
    `int` mypixiv: The user's mypixiv count
    `bool` official: Whether the user is an official account from pixiv
    `str` commentHtml: The HTML-formatted description
    `UserSocials` socials: The user's socials
    `str` webpage: The user's homepage
    """

    def __init__(self, data):

        super().__init__(data)

        self.isFollowed: bool = data["isFollowed"]
        self.following: int = data["following"]
        self.mypixiv: int = data["mypixivCount"]
        self.official: bool = data["official"]
        self.socials: UserSocials = UserSocials(data["social"])
        self.webpage: str = makeJumpPhp(data["webpage"]) if data["webpage"] else None
        soupDesc = BeautifulSoup(data["commentHtml"], "html.parser")

        for link in soupDesc.find_all("a"):
            # dont append jump.php when pixiv has already done this for us
            if link.get("href").__contains__("/jump.php?"):
                continue

            l = link.get("href")
            replacePixiv = ("users", "artworks")

            if l.__contains__("https://www.pixiv.net") and any(
                [l.__contains__(x) for x in replacePixiv]
            ):
                link.attrs["href"] = "/" + "/".join(
                    l.split("https://www.pixiv.net")[1].split("/")[2:]
                )
            else:
                link.attrs["href"] = "/jump.php?" + quote(l)

        self.commentHtml = str(soupDesc)


class Tag:
    """
    Represents a tag

    Properties:
    ===========

    `str` tag: The tag's name
    `str` enTranslation: The tag's English translation. `None` if not specified
    """

    def __init__(self, data):

        self.tag: str = data["tag"]
        self.enTranslation: str = (
            (
                data["translation"]["en"]
                if data["translation"]["en"] != ""
                else data["translation"]["romaji"]
            )
            if data.get("translation")
            else None
        )


class SimpleTag:
    def __init__(self, data):
        self.tag: str = data["tag"]
        self.tag_translation: str = (
            data["tag_translation"] if data["tag_translation"] != "" else None
        )


class PartialComment:
    """
    Represents a comment.

    Properties:
    ===========
    """

    def __init__(self, data):
        self._id = int(data["id"])
        self.authorId = int(data["userId"])
        self.username = data["userName"]
        self.img = makeProxy(data["img"])
        comment = escape(data["comment"])
        self.comment = str(comment)
        self.stampId = int(data["stampId"]) if data["stampId"] else None
        try:
            self.commentDate = datetime.strptime(data["commentDate"], "%Y-%m-%d %H:%M")
        except ValueError:
            self.commentDate = datetime.strptime(
                data["commentDate"], "%Y-%m-%d %H:%M:%S"
            )
        self.commentParentId = (
            int(data["commentParentId"]) if data["commentParentId"] else None
        )
        self.commentUserId = int(data["commentUserId"])
        self.editable = data["editable"]


class Comment(PartialComment):
    def __init__(self, data):
        super().__init__(data)

        self.isDeletedUser: bool = data["isDeletedUser"]
        self.hasReplies: bool = data["hasReplies"]


class CommentReply(PartialComment):
    def __init__(self, data):
        super().__init__(data)

        self.commentRootId: int = (
            int(data["commentRootId"]) if data["commentRootId"] else None
        )


class TagInfo:
    """
    Represents information about a tag.

    Properties:
    ===========

    `str` tag: The tag's name
    `str` word: Unknown, but it seems to be the same as `tag`
    `str` abstract: The tag's abstract or description. `None` if not set
    `str` image: The tag's image. Returns Anna Yanami if not set
    `int` imageId: The tag's image ID. Returns 121839265 or Anna Yanami if not set
    `str` imageTag: ?
    """

    def __init__(self, data):

        self.tag: str = data["tag"]
        self.word: str = data["word"]
        self.abstract: str = (
            data["pixpedia"]["abstract"] if data["pixpedia"].get("abstract") else None
        )
        self.image: str = (
            makeProxy(data["pixpedia"]["image"])
            if data["pixpedia"].get("image")
            else "/static/yanami.png"
        )
        self.imageId: int = (
            int(data["pixpedia"]["id"]) if data["pixpedia"].get("id") else 121839265
        )
        self.imageTag: str = data["pixpedia"]["tag"]

        try:
            self.enTranslation: str = (
                data["tagTranslation"][self.tag]["en"]
                if data["tagTranslation"][self.tag]["en"] != ""
                else data["tagTranslation"][self.tag]["romaji"]
            )
        except Exception:
            self.enTranslation = None


class ArtworkPage:
    """
    Represents a page in an artwork.

    Properties:
    ===========

    `int` width: Image width
    `int` height: Image height
    `str` originalUrl: The original quality image URL
    `str` thumbUrl: The image's thumbnail URL. Use `originalUrl` to get the original quality.
    """

    def __init__(self, data):
        self.width: int = data["width"]
        self.height: int = data["height"]

        self.originalUrl: str = makeProxy(data["urls"]["original"])
        self.thumbUrl: str = makeProxy(data["urls"]["regular"])


class PartialArtwork:
    """
    Base class for all artwork-related classes.

    Properties:
    ===========

    `int` _id: The artwork ID
    `str` title: The artwork's title
    `int` xRestrict: The raw value of the content filter type.
    Can be any of the following:

    0: Not rated
    1: R-18G
    Other: R-18

    `bool` isAI: Whether the artwork is AI generated
    `int` illustType: The raw value of the type of illustration.
    Can be any of the following:

    0: Illustration
    1: Manga
    2: Ugoira

    `bool` isUgoira: Whether the artwork is Ugoira.
    `int` pageCount: The amount of pages of the artwork
    `str` authorName: The name of the author
    `int` authorId: The ID of the author
    `str` xRestrictClassification: A string representation of the content filter
    `str` illustTypeClassification: A string representation of the artwork type
    """

    def __init__(self, data):
        self._id: int = data["id"]
        self.title: str = data["title"]
        self.xRestrict: int = data["xRestrict"]
        self.isAI: bool = data["aiType"] == 2
        self.aiType: int = data["aiType"]
        self.illustType: int = data["illustType"]
        self.isUgoira: bool = self.illustType == 2
        self.pageCount: int = data["pageCount"]
        self.authorName: str = data["userName"]
        self.authorId: int = int(data["userId"])
        self.sl: int = int(data["sl"])
        self.isSensitive: int = self.sl >= 4
        self.createDate: datetime.datetime = (
            datetime.fromisoformat(data["createDate"])
            if data.get("createDate")
            else None
        )
        self.updateDate: datetime.datetime = (
            datetime.fromisoformat(data["updateDate"])
            if data.get("updateDate")
            else None
        )
        self.uploadDate: datetime.datetime = (
            datetime.fromisoformat(data["uploadDate"])
            if data.get("uploadDate")
            else None
        )
        self.alt: str = data.get("alt", self.title)

        soupDesc = BeautifulSoup(data["description"], "html.parser")

        for link in soupDesc.find_all("a"):
            # dont append jump.php when pixiv has already done this for us
            if link.get("href").__contains__("/jump.php?"):
                continue

            l = link.get("href")
            replacePixiv = ("users", "artworks")

            if l.__contains__("https://www.pixiv.net") and any(
                [l.__contains__(x) for x in replacePixiv]
            ):
                link.attrs["href"] = "/" + "/".join(
                    l.split("https://www.pixiv.net")[1].split("/")[2:]
                )
            else:
                link.attrs["href"] = "/jump.php?" + quote(l)

        self.description = str(soupDesc)
        self.descriptionRaw = soupDesc.text

    @property
    def xRestrictClassification(self) -> str:
        match self.xRestrict:
            case 0:
                return None
            case 1:
                return "R-18"
            case 2:
                return "R-18G"

    @property
    def illustTypeClassification(self) -> str:
        match self.illustType:
            case 0:
                return "Illustration"
            case 1:
                return "Manga"
            case 2:
                return "Ugoira"


class Artwork(PartialArtwork):
    """
    Represents an artwork.
    This is a subclass of `PartialArtwork`

    Properties:
    ===========

    `str` thumbUrl: The thumbnail image URL
    `str` originalUrl: The original quality image URL
    `int` viewCount: The amount of views the artwork has
    `int` likeCount: The amount of likes the artwork has
    `int` bookmarkCount: The amount of bookmarks the artwork has
    `list[Tag]` tags: The artwork's tags
    `int` bookmarkId: The ID of the current user's bookmark. `None` if the user hasn't bookmarked the artwork
    `bool` bookmarked: Whether the current user has bookmarked the post
    `bool` liked: Whether the current user has liked the post
    `list[ArtworkEntry]` userIllusts: Other works from user
    """

    def __init__(self, data):

        super().__init__(data)

        self.thumbUrl: str = makeProxy(data["urls"]["regular"])
        self.originalUrl: str = makeProxy(data["urls"]["original"])

        self.viewCount: int = data["viewCount"]
        self.likeCount: int = data["likeCount"]
        self.bookmarkCount: int = data["bookmarkCount"]
        self.commentCount: int = data["commentCount"]
        self.commentOff: bool = data["commentOff"] == 1
        self.tags: list[Tag] = []
        self.isOriginal: bool = data["isOriginal"]
        self.width: int = data["width"]
        self.height: int = data["height"]
        self.restrict: int = int(data["restrict"])
        self.isPrivate: bool = self.restrict >= 1

        self.bookmarkId: int = (
            data["bookmarkData"]["id"] if data["bookmarkData"] else None
        )

        self.bookmarked: bool = data["bookmarkData"] is not None
        self.liked: int = data["likeData"] == True

        for tag in data["tags"]["tags"]:
            self.tags.append(Tag(tag))

        self.userIllustIds = list(data["userIllusts"].keys())
        self.userIllusts = []

        self.ugoiraUrl = ""
        for i in data["userIllusts"]:
            i = data["userIllusts"][i]
            if not i:
                continue
            
            if self.isUgoira and UgoiraServerNeedsDate and i["id"] == data["id"]:
                self.ugoiraUrl = i["createDate"].split("+")[0].replace("-", "/").replace("T", "/").replace(":", "/") 
                
            self.userIllusts.append(ArtworkEntry(i))

        if self.isUgoira:
            if self.ugoiraUrl != "":
                self.ugoiraUrl += "/" + str(data["id"])
            else:
                self.ugoiraUrl = str(data["id"])

            if UgoiraServerTrusted:
                self.ugoiraUrl = UgoiraServer % self.ugoiraUrl
            else:
                self.ugoiraUrl = "/proxy/ugoira/" + self.ugoiraUrl


class ArtworkEntry(PartialArtwork):
    """
    Represents an artwork entry (the artworks shown in recommended, rankings, etc.)
    This is a subclass of `PartialArtwork`

    Properties:
    ===========

    `str` thumbUrl: The thumbnail image URL
    `str` authorProfilePic: The author's profile picture
    `str` authorUrl: The author's URL
    """

    def __init__(self, data):

        super().__init__(data)

        self.thumbUrl: str = (
            makeProxy(data["url"])
            if data["url"] != "https://s.pximg.net/common/images/limit_unknown_360.png"
            else "/static/img/deleted.png"
        )
        self.authorProfilePic: str = makeProxy(
            data.get(
                "profileImageUrl", "https://s.pximg.net/common/images/no_profile_s.png"
            )
        )
        self.authorUrl: str = f"/users/{self.authorId}"

    def __repr__(self):
        return f"<ArtworkEntry _id={self._id} title={self.title} author={self.authorName} xRestrict={self.xRestrict} isAI={self.isAI} aiType={self.aiType} isUgoira={self.isUgoira}>"


class TrendingTag:
    def __init__(
        self, tag: str, info: ArtworkEntry, translation: str, trendingRate: int
    ):
        self.tag: str = tag
        self.info: ArtworkEntry = info
        self.translation: str = translation
        self.trendingRate: int = trendingRate

    def __repr__(self):
        return f"<TrendingTag tag={self.tag} info={self.info} translation={self.translation} trendingRate={self.trendingRate}>"


class UserFollowData:
    """
    Represents data for following/followed/mypixiv users

    Properties:
    ===========

    `int` userId: The user's ID
    `str` userName: The user's name
    `str` profileImageUrl: proxied profile picture URL
    `str` userComment: The user's bio
    `bool` following: Whether the user is following the user
    `bool` followed: Whether the user has followed the current user
    `bool` isMypixiv: Whether the user is a current user's mypixiv
    `list[ArtworkEntry]` illusts: To show off the user's illustrations
    """

    def __init__(self, data):
        self.userId: int = int(data["userId"])
        self.userName: str = data["userName"]
        self.profileImageUrl: str = makeProxy(data["profileImageUrl"])
        self.userComment: str = data["userComment"]
        self.following: bool = data["following"]
        self.followed: bool = data["followed"]
        self.isMypixiv: bool = data["followed"]
        self.illusts: list[ArtworkEntry] = [ArtworkEntry(x) for x in data["illusts"]]

    def __repr__(self):
        return f"<UserFollowData userId={self.userId} userName={self.userName} profileImageUrl={self.profileImageUrl} following={self.following} followed={self.followed} isMypixiv={self.isMypixiv} illusts={self.illusts}>"


class RecommendedUser(PartialUser):
    """
    Represents a recommended user
    This is a subclass of `PartialUser`

    Properties:
    ===========

    `dict` commission: Raw properties for commission data. For internal use
    `bool` acceptRequest: Whether the user is accepting commissions
    `bool` isSubscribedReopenNotification: Whether the current is subscribed to when the user will reopen commissions again
    """

    def __init__(self, data, recentArtworks: list[ArtworkEntry]):

        super().__init__(data)

        self.commission = data["commission"]
        self.acceptRequest = (
            self.commission["acceptRequest"] if self.commission else False
        )
        self.isSubscribedReopenNotification = (
            self.commission["isSubscribedReopenNotification"]
            if self.commission
            else False
        )
        self.recentArtworks: list[ArtworkEntry] = recentArtworks


class RankingEntry(ArtworkEntry):
    """
    Represents an entry in rankings.
    This is a subclass of `ArtworkEntry`

    Properties:
    ===========

    `int` attr: Ranking attributes
    `int` bookmarkable: Whether it can be bookmarked or not
    `datetime` date: The date it was uploaded
    `int` height: Illustration height
    `int` illustBookStyle: ?
    `dict` illustContentType: Content type
    `int` ratingCount: Like/bookmark count?
    `int` width: Illustration width
    `int` rank: The artwork's rank
    `int` yesRank: ?
    """

    def __init__(self, data):

        #  this one has a different structure, so we need to reuse
        #  the classes when possible

        super().__init__(
            {
                "id": data["illust_id"],
                "title": data["title"],
                "url": data["url"],
                "userId": data["user_id"],
                "userName": data["user_name"],
                "xRestrict": 0,  #  no way to determine
                "aiType": 0,
                "illustType": int(data["illust_type"]),
                "pageCount": int(data["illust_page_count"]),
                "profileImageUrl": data["profile_img"],
                "description": "",
                "sl": 4 if data["is_masked"] else 0,
            }
        )

        self.attr: str = data["attr"]
        self.bookmarkable: bool = data.get("bookmarkable", False)
        self.date: datetime = datetime.strptime(data["date"], "%Y年%m月%d日 %H:%M")
        self.height: int = data["height"]
        self.illustBookStyle: int = int(data["illust_book_style"])
        self.illustContentType: dict = data["illust_content_type"]
        self.illustUploadTimestamp: datetime = datetime.fromtimestamp(
            data["illust_upload_timestamp"]
        )
        self.ratingCount: int = data["rating_count"]
        self.width: int = data["width"]
        self.rank: int = data["rank"]
        self.yesRank: int = data["yes_rank"]


class Ranking:
    def __init__(self, data):
        self.content: str = data["content"]
        self.contents: list[RankingEntry] = [RankingEntry(x) for x in data["contents"]]
        self._date: int = int(data["date"])
        self.mode: str = data["mode"]
        self.next: int = data["next"] if type(data["next"]) == int else None
        self._nextDate: str = (
            data["next_date"] if type(data["next_date"]) == str else None
        )
        self.page: int = data["page"]
        self.prev: int = data["prev"] if type(data["prev"]) == int else None
        self._prevDate: str = data["prev_date"] if type("prev_date") == str else None

        self.date: datetime = datetime.strptime(str(self._date), "%Y%m%d")
        self.nextDate: datetime = (
            datetime.strptime(str(self._nextDate), "%Y%m%d") if self._nextDate else None
        )
        self.prevDate: datetime = (
            datetime.strptime(str(self._prevDate), "%Y%m%d") if self._prevDate else None
        )


class SearchResults:
    """
    Represents search results.

    Properties:
    ===========

    `list[ArtworkEntry]` popularRecent: The recent popular artworks
    `list[ArtworkEntry]` popularAllTime: The all-time popular artworks
    `list[Tag]` relatedTags: The related tags
    `int` lastPage: The last page. Hard-capped to 1000 by the API
    `list[ArtworkEntry]` results: The results of the search.
    """

    def __init__(self, data):
        self.popularRecent: list[ArtworkEntry] = [
            ArtworkEntry(x) for x in data["popular"]["recent"]
        ]
        self.popularAllTime: list[ArtworkEntry] = [
            ArtworkEntry(x) for x in data["popular"]["permanent"]
        ]
        self.relatedTags: list[Tag] = []
        self.lastPage: int = data["illustManga"]["lastPage"]
        self.total: int = data["illustManga"]["total"]
        self.results: list[ArtworkEntry] = [
            ArtworkEntry(x) for x in data["illustManga"]["data"]
        ]

        for related in data["relatedTags"]:

            newTagData = {}

            newTagData["tag"] = related
            if related in data["tagTranslation"]:
                newTagData["translation"] = {
                    "en": data["tagTranslation"][related]["en"]
                }

            self.relatedTags.append(Tag(newTagData))

    def __len__(self):
        return self.total


class UserSettingsState:
    def __init__(self, data):

        _ = data["user_status"]
        self.userId = int(_["user_id"])
        self.pixivId = _["user_account"]
        self.userName = _["user_name"]
        self.userCreateTime = datetime.strptime(
            _["user_create_time"], "%Y-%m-%d %H:%M:%S"
        )
        self.userBirth = datetime.strptime(_["user_birth"], "%Y-%m-%d")
        self.xRestrictEnabled = int(_["user_x_restrict"]) >= 1
        self.r18GEnabled = int(_["user_x_restrict"]) == 2
        self.profileImg = makeProxy(_["profile_img"]["main"])
        self.age = _["age"]
        self.isIllustCreator = _["is_illust_creator"]
        self.isNovelCreator = _["is_novel_creator"]
        self.hideAiWorks = _["hide_ai_works"]
        self.readingStatusEnabled = _["reading_status_enabled"]
        self.location = _["location"]


class UserBookmarks:
    """
    Represents a user's bookmarks.

    Properties:
    ===========

    `list[ArtworkEntry]` works: The artworks the user has bookmarked
    `int` total: The total bookmarks
    """

    def __init__(self, data):
        self.works: list[ArtworkEntry] = [ArtworkEntry(x) for x in data["works"]]

        self.total: int = data["total"]

    def __len__(self):
        return self.total


class Notification:
    """
    Represents a notification

    Properties:
    ===========

    `str` content: the contents of the notification
    `str` iconUrl: the notification icon url
    `int` _id: the notification id
    `bool` isProfileIcon: whether the icon is a profile picture
    `str` linkUrl: the url the notification will point to
    `datetime.datetime` notifiedAt: the time the user was notified
    `bool` targetBlank: whether the link should have the `target=_blank` HTML attribute
    `bool` unread: whether the notification is unread
    `str` type: the notification type
    """

    def __init__(self, data):

        self.content: str = data["content"]
        self.iconUrl: str = makeProxy(data["iconUrl"])
        self.isProfileIcon: bool = data["isProfileIcon"]
        self._id: int = data["id"]
        self.linkUrl: str = data["linkUrl"].replace("/en", "")
        self.notifiedAt: datetime.datetime = datetime.fromisoformat(data["notifiedAt"])
        self.targetBlank: bool = data["targetBlank"]
        self.notificationType: str = data["type"]
        self.unread: bool = data["unread"] == 1
        self.type: str = data["type"]


class NewsEntry:
    def __init__(self, data):
        self.categoryId: int = int(data["categoryId"])
        self.date: datetime = datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S")
        self.id: int = int(data["id"])
        self.originId: int = int(data["originId"])
        self.title: str = data["title"]

    def __repr__(self):
        return f"<NewsEntry categoryId={self.categoryId} date={repr(self.date)} id={self.id} originId={self.originId} title={self.title}>"


class NewsArticleMetadata:
    def __init__(self, data):
        self.title = data["title"]
        self.image = makeProxy(data["image"])
        self.description = data["description"]


class NewsArticle(NewsEntry):
    def __init__(self, data):
        super().__init__(data["entry"])
        msg: str = data["entry"]["msg"]

        s = BeautifulSoup(msg, "html.parser")

        for link in s.find_all("a"):
            l = link.get("href")
            link.attrs["href"] = makeJumpPhp(l)

        for img in s.find_all("img"):
            src = img.get("src")
            img.attrs["src"] = makeProxy(src)

        for iframe in s.find_all("iframe"):
            src = iframe.get("src")

            # fixing URL's (to turn them into regular URLs instead of embeds)
            # maybe move this logic to a separate function in the future if needed
            parsed = list(
                urlparse(src)
            )  # ['https', 'www.youtube.com', '/embed/z_qOw0GUJKM', '', 'si=GZk4QJ1H2WKr9h3E', '']
            if parsed[1] == "youtube.com" or parsed[1] == "www.youtube.com":
                parsed[4] = ""
                if parsed[2].startswith("/embed"):
                    parsed[2] = "/watch?v=" + parsed[2][7:]

            src = urlunparse(parsed)
            originalUrl = s.new_tag("i")
            anchor = s.new_tag("a", attrs={"href": makeJumpPhp(src)})
            anchor.string = "Go to iframe page"
            originalUrl.append(anchor)

            iframe.insert_after(originalUrl)
            iframe.attrs["src"] = "/static/blocked.html"

        self.msg = s
        self.ogp_metadata: NewsArticleMetadata = NewsArticleMetadata(
            data["meta"]["ogp"]
        )


class UserInternalIllustDetails:
    def __init__(self, data):
        self.id: int = data["illustId"]
        self.reuploadable: bool = data["reuploadable"]
        self.illustPageCount: int = data["illustPageCount"]
        self.illustThumbnailUrl: str = makeProxy(data["illustThumbnailUrl"])
        self.title: str = data["title"]
        self.caption: str = data["caption"]
        self.allowTagEdit: bool = data["allowTagEdit"]
        self.xRestrict: str = data["xRestrict"]
        self.sexual: bool = data["sexual"]
        self.aiType: str = data["aiType"]
        self.aiGenerated: bool = self.aiType == "aiGenerated"
        self.restrict: str = data["restrict"]
        self.isRestrictLocked: bool = data["isRestrictLocked"]
        self.allowComment: bool = data["allowComment"]
        self.original: bool = data["original"]
        self.tools: list[str] = data["tools"]


class UserExternalServices:
    def __init__(self, data):
        self.twitter: str = data["twitter"]
        self.instagram: str = data["instagram"]
        self.tumblr: str = data["tumblr"]
        self.facebook: str = data["facebook"]
        self.circlems: str = data["circlems"]


class UserMyProfile:
    def __init__(self, data):
        self.coverImage: str = makeProxy(data["coverImage"])
        self.profileImage: str = makeProxy(data["profileImage"])
        self.name: str = data["name"]
        self.comment: str = data["comment"]
        self.externalServices: UserExternalServices = UserExternalServices(
            data["externalService"]
        )
        self.pawooAuthorized: bool = data["pawoo"]["isPawooAuthorized"]
        self.preferDisplayPawoo: bool = data["pawoo"]["preferDisplayPawoo"]
        self.isOfficialUser: bool = data["isOfficialUser"]
        self.jobId: int = data["job"]["value"]
        self.birth: datetime = datetime(
            data["birthYear"]["value"],
            data["birthMonthAndDay"]["month"],
            data["birthMonthAndDay"]["day"],
        )
        self.genderId: bool = data["gender"]["value"]
        self.region: str = data["location"]["region"]
        self.prefecture: str = data["location"]["prefecture"]


class MessageThreadUser:
    def __init__(self, data):
        self.id: int = int(data["user_id"])
        self.username: str = data["user_name"]
        self.icon: str = makeProxy(data["icon_url"])
        self.isPremium: bool = data["is_premium"]
        self.isMypixiv: bool = data["is_mypixiv"]
        self.followed: bool = data["followed"]
        self.blocked: bool = data["blocked"]
        self.isCompleteUser: bool = data["is_complete_user"]


class MessageThreadBase:
    def __init__(self, data):
        self.thread_id: int = int(data["thread_id"])
        self.name: str = data.get("name", data.get("thread_name"))
        self.unreadNum: int = int(data["unread_num"])
        self.memberNum: int = int(data["member_num"])
        self.latestContent: str = data["latest_content"]
        self.official: bool = data["is_official"]
        self.mendako: bool = data["is_mendako"]
        # not sure if 100x100 is the only size
        self.icon: str = makeProxy(data["icon_url"]["100x100"])
        self.modifiedAt: datetime = datetime.fromtimestamp(int(data["modified_at"]))
        self.isPair: bool = data["is_pair"]


class MessageThread(MessageThreadBase):
    def __init__(self, data):
        t = data["thread"]
        super().__init__(t)
        self.pairUserId: int = t["pair_user_id"]
        self.canSendMessage: bool = t["can_send_message"]
        self.users: list[MessageThreadUser] = [
            MessageThreadUser(x) for x in data["users"]
        ]


class MessageThreadContent:
    def __init__(self, d):
        self.contentId: int = int(d["content_id"])
        self.createdAt: datetime = datetime.fromtimestamp(int(d["created_at"]))
        self.type: str = d["content"]["type"]
        self.thumbImg: str | None = (
            makeProxy(d["content"]["image_urls"]["600x600"])
            if self.type == "image"
            else None
        )
        self.image: str | None = (
            makeProxy(d["content"]["image_urls"]["big"])
            if self.type == "image"
            else None
        )
        self.isStarred: bool = d["content"].get("is_starred", False)
        self.username: str = d["user"]["user_name"]
        self.userid: int = int(d["user"]["user_id"])
        self.iconUrl: str = makeProxy(d["user"]["icon_url"]["main_s"])
        self.text: str = d["content"].get("text")

    def to_json(self):
        return {
            "type": self.type,
            "id": self.contentId,
            "created_at": int(self.createdAt.timestamp()),
            "starred": self.isStarred,
            "username": self.username,
            "userid": self.userid,
            "icon": self.iconUrl,
            "text": self.text,
            "image": self.image,
            "thumbnail": self.thumbImg,
        }

class MessageThreadContents:
    def __init__(self, d):
        self.total: int = int(d["total"])
        # {x.split("=")[0]: x.split("=")[1] for x in p.query.split("&")}
        nextUrlArgs = (
            {
                x.split("=")[0]: x.split("=")[1]
                for x in urlparse(d["next_url"]).query.split("&")
            }
            if d["next_url"]
            else {}
        )
        self.nextContentId = nextUrlArgs.get("max_content_id")
        self.contents: list[MessageThreadContent] = [
            MessageThreadContent(x) for x in d["message_thread_contents"]
        ]


class MessageThreadEntry(MessageThreadBase):
    def __init__(self, data):
        super().__init__(data)
        self.isActiveThread: bool = data["is_active_thread"]


class ArtworkDetailsPage:
    def __init__(
        self,
        artwork: Artwork,
        pages: list[ArtworkPage],
        user: User,
        related: list[ArtworkEntry],
        userIllusts: list[ArtworkEntry],
    ):

        self.artwork: Artwork = artwork
        self.pages: list[ArtworkPage] = pages
        self.user: User = user
        self.related: list[ArtworkEntry] = related
        self.userIllusts: list[ArtworkEntry] = userIllusts


class PixivisionEntry:
    def __init__(self, data):
        self.id: int = int(data["id"])
        self.thumbnailUrl: str = makeProxy(data["thumbnailUrl"])
        self.title: str = data["title"]


class RecommendByTag:
    def __init__(self, name: str, artworks: list[ArtworkEntry]):
        self.name: str = name
        self.artworks: list[ArtworkEntry] = artworks


class LandingPageLoggedIn:
    def __init__(
        self,
        recommended: list[ArtworkEntry],
        recommendByTag: list[RecommendByTag],
        newestFromFollowing: list[ArtworkEntry],
        recommendedUsers: list[RecommendedUser],
        pixivisionArticles: list[PixivisionEntry],
        tags: list[SimpleTag],
        trendingTags: list[TrendingTag],
    ):
        self.recommended: list[ArtworkEntry] = recommended
        self.recommendByTag: list[RecommendByTag] = recommendByTag
        self.newestFromFollowing: list[ArtworkEntry] = newestFromFollowing
        self.recommendedUsers: list[RecommendedUser] = recommendedUsers
        self.pixivisionArticles: list[PixivisionEntry] = pixivisionArticles
        self.tags: list[SimpleTag] = tags
        self.trendingTags: list[TrendingTag] = trendingTags


class LandingPageManga:
    def __init__(
        self,
        recommended: list[ArtworkEntry],
        tags: list[SimpleTag],
    ):
        self.recommended: list[ArtworkEntry] = recommended
        self.tags: list[SimpleTag] = tags
