from .utils.converters import makeProxy

#  tbh maybe i should make a Python library
#  that interacts with the pixiv api...


class User:

    def __init__(self, data):

        self._id = data["userId"]
        self.name = data["name"]
        self.comment = data["comment"]
        self.image = makeProxy(data["image"])
        self.imageBig = makeProxy(data["imageBig"])
        self.following = data["following"]
        self.mypixiv = data["mypixivCount"]
        self.premium = data["premium"]
        self.official = data["official"]

        self.background = (
            makeProxy(data["background"]["url"]) if data["background"] else None
        )


class Tag:
    def __init__(self, data):

        self.tag = data["tag"]
        self.enTranslation = (
            data["translation"]["en"] if data.get("translation") else None
        )


class ArtworkPage:
    def __init__(self, data):
        self.width = data["width"]
        self.height = data["height"]

        self.originalUrl = makeProxy(data["urls"]["original"])
        self.thumbUrl = makeProxy(data["urls"]["regular"])


class PartialArtwork:

    def __init__(self, data):
        self._id = data["id"]
        self.title = data["title"]
        self.xRestrict = data["xRestrict"]
        self.isAI = data["aiType"] == 2
        self.illustType = data["illustType"]
        self.isUgoira = self.illustType == 2
        self.pageCount = data["pageCount"]
        self.authorName = data["userName"]
        self.authorId = data["userId"]

    @property
    def xRestrictClassification(self):
        match self.xRestrict:
            case 0:
                return None
            case 1:
                return "R-18"
            case _:
                return "R-18G"

    @property
    def illustTypeClassification(self):
        match self.illustType:
            case 0:
                return "Illustration"
            case 1:
                return "Manga"
            case 2:
                return "Ugoira"


class Artwork(PartialArtwork):
    def __init__(self, data):

        super().__init__(data)

        self.thumbUrl = makeProxy(data["urls"]["regular"])
        self.originalUrl = makeProxy(data["urls"]["original"])
        self.pageCount = data["pageCount"]
        self.description = data["description"]

        self.viewCount = data["viewCount"]
        self.likeCount = data["likeCount"]
        self.bookmarkCount = data["bookmarkCount"]
        self.tags: list[Tag] = []

        self.bookmarkId = data["bookmarkData"]["id"] if data["bookmarkData"] else None

        self.bookmarked = data["bookmarkData"] is not None
        self.liked = data["likeData"] == True

        for tag in data["tags"]["tags"]:
            self.tags.append(Tag(tag))


class ArtworkEntry(PartialArtwork):
    def __init__(self, data):

        super().__init__(data)

        self.thumbUrl = makeProxy(data["url"])
        self.pageCount = data["pageCount"]
        self.authorProfilePic = makeProxy(data["profileImageUrl"])
        self.authorUrl = f"/users/{self.authorId}"


class RankingEntry(ArtworkEntry):
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
            }
        )

        self.rank = data["rank"]


class RecommendByTag:
    def __init__(self, name: str, artworks: list[ArtworkEntry]):
        self.name: str = name
        self.artworks: list[ArtworkEntry] = artworks


class LandingPageLoggedIn:
    def __init__(
        self, recommended: list[ArtworkEntry], recommendByTag: list[RecommendByTag]
    ):
        self.recommended: list[ArtworkEntry] = recommended
        self.recommendByTag: list[RecommendByTag] = recommendByTag


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
