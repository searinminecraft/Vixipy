from utils.converters import makeProxy

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

        self.background = makeProxy(data["background"]["url"]) if data["background"] else None

class Tag:
    def __init__(self, data):

        self.tag = data["tag"]
        self.enTranslation = data["translation"]["en"] if data.get("translation") else None

class ArtworkPage:
    def __init__(self, data):
        self.width = data["width"]
        self.height = data["height"]

        self.originalUrl = makeProxy(data["urls"]["original"])
        self.thumbUrl = makeProxy(data["urls"]["regular"])

class Artwork:
    def __init__(self, data):
        self._id = data["id"]
        self.title = data["title"]
        self.xRestrict = data["xRestrict"]
        self.thumbUrl = makeProxy(data["urls"]["regular"])
        self.originalUrl = makeProxy(data["urls"]["original"])
        self.pageCount = data["pageCount"]
        
        self.viewCount = data["viewCount"]
        self.likeCount = data["likeCount"]
        self.bookmarkCount = data["bookmarkCount"]
        self.tags: list[Tag] = []

        self.bookmarkId = data["bookmarkData"]["id"] if data["bookmarkData"] else None

        self.bookmarked = data["bookmarkData"] is not None
        self.liked = data["likeData"] == True

        self.authorName = data["userName"]
        self.authorId = data["userId"]

        for tag in data["tags"]["tags"]:
            self.tags.append(Tag(tag))

    @property
    def xRestrictClassification(self):
        match self.xRestrict:
            case 0:
                return None
            case 1:
                return "R-18G"
            case _:
                return "R-18"


class ArtworkEntry:
    def __init__(self, data):
        self._id = data["id"]
        self.title = data["title"]
        self.isAI = data["aiType"] == 2
        self.thumbUrl = makeProxy(data["url"])
        self.description = data["description"] if data["description"] != "" else None
        self.pageCount = data["pageCount"]
        self.xRestrict = data["xRestrict"]
        self.authorId = data["userId"]
        self.authorName = data["userName"]
        self.authorProfilePic = makeProxy(data["profileImageUrl"])
        self.authorUrl = f"/users/{self.authorId}"

    @property
    def xRestrictClassification(self):
        match self.xRestrict:
            case 0:
                return None
            case 1:
                return "R-18G"
            case _:
                return "R-18"

class RecommendByTag:
    def __init__(self, name: str, artworks: list[ArtworkEntry]):
        self.name: str = name
        self.artworks: list[ArtworkEntry] = artworks

class LandingPageLoggedIn:
    def __init__(self, recommended: list[ArtworkEntry], recommendByTag: list[RecommendByTag]):
        self.recommended: list[ArtworkEntry] = recommended
        self.recommendByTag: list[RecommendByTag] = recommendByTag

class ArtworkDetailsPage:
    def __init__(self, artwork: Artwork,
                 pages: list[ArtworkPage],
                 user: User,
                 related: list[ArtworkEntry]):

        self.artwork: Artwork = artwork
        self.pages: list[Artwork] = pages
        self.user: User = user
        self.related: list[ArtworkEntry] = related
