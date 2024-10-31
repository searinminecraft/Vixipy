from .utils.converters import makeProxy
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import quote

#  tbh maybe i should make a Python library
#  that interacts with the pixiv api...


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
        self.comment: str = data["comment"]
        self.image: str = makeProxy(data["image"])
        self.imageBig: str = makeProxy(data["imageBig"])
        self.premium: bool = data["premium"]
        self.background: str = (
            makeProxy(data["background"]["url"]) if data["background"] else None
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
    """

    def __init__(self, data):

        super().__init__(data)

        self.following: int = data["following"]
        self.mypixiv: int = data["mypixivCount"]
        self.official: bool = data["official"]
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
            data["translation"]["en"] if data.get("translation") else None
        )


class Comment:
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
        self.isDeletedUser = data["isDeletedUser"]
        self.comment = data["comment"]
        self.stampId = int(data["stampId"]) if data["stampId"] else None
        self.commentDate = data["commentDate"]
        self.commentParentId = (
            int(data["commentParentId"]) if data["commentParentId"] else None
        )
        self.commentUserId = int(data["commentUserId"])
        self.editable = data["editable"]
        self.hasReplies = data["hasReplies"]


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
            self.enTranslation: str = data["tagTranslation"][self.tag]["en"]
        except (KeyError, IndexError, TypeError):
            self.enTranslation: str = None


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
        self.authorId: int = data["userId"]
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
            case _:
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

        self.bookmarkId: int = (
            data["bookmarkData"]["id"] if data["bookmarkData"] else None
        )

        self.bookmarked: bool = data["bookmarkData"] is not None
        self.liked: int = data["likeData"] == True

        for tag in data["tags"]["tags"]:
            self.tags.append(Tag(tag))


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

        self.thumbUrl: str = makeProxy(data["url"])
        self.authorProfilePic: str = makeProxy(
            data.get(
                "profileImageUrl", "https://s.pximg.net/common/images/no_profile_s.png"
            )
        )
        self.authorUrl: str = f"/users/{self.authorId}"

    def __repr__(self):
        return f"<ArtworkEntry _id={self._id} title={self.title} author={self.authorName} xRestrict={self.xRestrict} isAI={self.isAI} aiType={self.aiType} isUgoira={self.isUgoira}>"


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

    `int` rank: The artwork's rank
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
            }
        )

        self.rank: int = data["rank"]


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
        # needs more testing, it may be possible that some urls may not contain the language specifier ("/en", etc.)
        self.linkUrl: str = data["linkUrl"][3:]
        self.notifiedAt: datetime.datetime = datetime.fromisoformat(data["notifiedAt"])
        self.targetBlank: bool = data["targetBlank"]
        self.notificationType: str = data["type"]
        self.unread: bool = data["unread"] == 1
        self.type: str = data["type"]


class ArtworkDetailsPage:
    def __init__(
        self,
        artwork: Artwork,
        pages: list[ArtworkPage],
        user: User,
        related: list[ArtworkEntry],
    ):

        self.artwork: Artwork = artwork
        self.pages: list[Artwork] = pages
        self.user: User = user
        self.related: list[ArtworkEntry] = related


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
    ):
        self.recommended: list[ArtworkEntry] = recommended
        self.recommendByTag: list[RecommendByTag] = recommendByTag
        self.newestFromFollowing: list[ArtworkEntry] = newestFromFollowing
        self.recommendedUsers: list[RecommendedUser] = recommendedUsers
