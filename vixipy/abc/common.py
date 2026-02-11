from quart import request


class Tag:
    def __init__(self, name, en=None, romaji=None):
        self.name = name
        self.en = en
        self.romaji = romaji

    def __eq__(self, x):
        return self.name == x or self.en == x or self.romaji == x

    def __str__(self):
        return self.name


class TagTranslation:
    def __init__(self, orig: str, d):
        self.orig: str = orig
        self.en: Optional[str] = d.get("en") or None
        self.ko: Optional[str] = d.get("ko") or None
        self.zh: Optional[str] = d.get("zh") or None
        self.zh_tw: Optional[str] = d.get("zh_tw") or None
        self.romaji: Optional[str] = d.get("romaji") or None

    def __str__(self):
        return self.orig

    def __eq__(self, x):
        return self.orig == x or self.default == x

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
