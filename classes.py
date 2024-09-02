from utils.converters import makeProxy

class Artwork:

    def __init__(self, data):

        self._id = data["id"]
        self.title = data["title"]
        self.isAI = data["aiType"] == 2
        self.thumbUrl = makeProxy(data["url"])
        self.tags = data["tags"]
        self.bookmarkData = data["bookmarkData"]
        self.description = data["description"] if data["description"] != "" else None
        self.pageCount = data["pageCount"]
        self.xRestrict = data["xRestrict"]
        self.width = data["width"]
        self.height = data["height"]
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

    def __init__(self, name: str, artworks: list[Artwork]):

        self.name: str = name
        self.artworks: list[Artwork] = artworks

class LandingPageLoggedIn:

    def __init__(self, recommended: list[Artwork], recommendByTag: list[RecommendByTag]):

        self.recommended: list[Artwork] = recommended
        self.recommendByTag: list["recommendByTag"] = recommendByTag
