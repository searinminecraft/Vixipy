from __future__ import annotations

from datetime import datetime
import logging
from quart import current_app, render_template
import re
from typing import TYPE_CHECKING
from ._types import PixivisionEntry, PixivisionTag
from ...converters import convert_pixiv_link, proxy

if TYPE_CHECKING:
    from bs4 import Tag


BG_IMG_RE = re.compile(r"background-image:url\((.+)\)")
log = logging.getLogger("vixipy.lib.pixivision.components")


class PixivisionComponent:
    def __init__(self, component: str):
        self.component = component

    async def render(self):
        """Renders the component"""
        try:
            return await render_template(
                f"pixivision/components/{self.component}.html", data=self
            )
        except Exception as e:
            log.exception("Failure rendering the component %s", self.component)
            return await render_template(
                f"pixivision/components/render_error.html", error=e
            )


class BodyParagraph(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("body_paragraph")

        self._main = d.div
        self.body = None

    async def render(self):
        for y in self._main.find_all("a"):
            y.attrs["href"] = convert_pixiv_link(y.attrs["href"])

        self.body = "\n".join([str(x) for x in self._main.contents])

        return await super().render()


class PixivArtwork(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("pixiv_artwork")

        self.author_link = d.select_one("a.am__work__user-icon-container").attrs["href"]
        self.author_img = d.select_one("img.am__work__uesr-icon").attrs["src"]
        self.title = d.select_one("h3.am__work__title a").text
        self.author_name = d.select_one("p.am__work__user-name a").text
        self.image_link = d.select_one("div.am__work__main a").attrs["href"]
        self.image = d.select_one("div.am__work__main img").attrs["src"]

    async def render(self):
        self.image_link = convert_pixiv_link(self.image_link)
        self.image = proxy(self.image)
        self.author_link = convert_pixiv_link(self.author_link)
        self.author_img = proxy(self.author_img)
        return await super().render()


class Heading(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("heading")

        self._main = d
        self.type = d.select_one("h1, h2, h3, h4, h5, h6").name
        self.contents = d.text
        self.id = d.attrs.get("id")

    async def render(self):
        for x in self._main.find_all("img"):
            x.attrs["src"] = proxy(x.attrs["src"])
        return await super().render()


class SubHeading(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("subheading")

        self.type = d.select_one("h1, h2, h3, h4, h5, h6").name
        self.contents = d.text
        self.id = d.attrs.get("id")


class ArticleThumb(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("article_thumb")

        self.image = d.select_one(".aie__image").attrs["src"]
        self.alt = d.select_one(".aie__image").attrs["alt"]
        self.clearfix = d.select_one(".fab__clearfix").text or None

    async def render(self):
        self.image = proxy(self.image)
        return await super().render()


class Image(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("image")

        self.image = d.select_one("img").attrs["src"]
        l = d.select_one("a")
        self.link = l.attrs["href"] if l else None
        self.clearfix = d.select_one(".fab__clearfix").text or None

    async def render(self):
        self.image = proxy(self.image)
        self.link = convert_pixiv_link(self.link)
        return await super().render()


class ArticleCard(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("article_card")

        main = d.select_one("article._article-card")

        image = BG_IMG_RE.search(
            main.find("div", class_="_thumbnail").attrs["style"].replace(" ", "")
        ).group(1)
        date = datetime.strptime(main.find("time").text, "%Y.%m.%d")
        title_element = main.find("h2", class_="arc__title")
        id = int(title_element.a.attrs["data-gtm-label"])
        title = title_element.text
        category = main.find("a", attrs={"data-gtm-action": "ClickCategory"}).attrs[
            "data-gtm-label"
        ]

        tag_list: list[PixivisionTag] = []
        tag_list_element = main.find("ul", class_="_tag-list")

        for x in tag_list_element:
            tag_name = x.a.attrs["data-gtm-label"]
            tag_id = int(x.a.attrs["href"].split("/")[-1])
            tag_list.append(PixivisionTag(tag_id, tag_name))

        self.entry = PixivisionEntry(id, title, date, image, category, tag_list)

    async def render(self):
        self.entry.image = proxy(self.entry.image)
        return await super().render()


class _TOCEntry:
    def __init__(self, href, name):
        self.href = href
        self.name = name


class TableOfContents(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("table_of_contents")

        self.contents: list[_TOCEntry] = []

        for x in d.select("li a"):
            self.contents.append(_TOCEntry(x.attrs["href"], x.text))


class Profile(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("profile")
        log.debug(d)

        image = d.select_one("img")
        self.image = image.attrs["src"]
        self.image_alt = image.attrs["alt"]
        self.links = []
        self.name = d.find_all("li")[0].text
        self.info = d.select_one("li._medium-editor-text").text

        for x in d.select("li:last-child a"):
            self.links.append([x.attrs["href"], x.text])

    async def render(self):
        self.image = proxy(self.image)

        for x, y in enumerate(self.links):
            self.links[x][0] = convert_pixiv_link(y[0])

        return await super().render()


class Credit(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("credit")
        self.text = d.select_one("p.fab__credit").text


class Movie(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("movie")
        self.link = d.select_one("iframe").attrs["src"]

    async def render(self):
        self.link = convert_pixiv_link(self.link)
        return await super().render()


class BrokenComponent(PixivisionComponent):
    def __init__(self, error: Exception):
        self.error = error

    async def render(self):
        return await render_template(
            "pixivision/components/render_error.html", error=self.error
        )


class Question(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("question")
        self._orig = d.select_one(".fab__paragraph")

    async def render(self):
        for x in self._orig.find_all("a"):
            x.attrs["href"] = convert_pixiv_link(x.attrs["href"])
        self.text = " ".join([str(x) for x in self._orig.contents]).replace("── ", "")

        return await super().render()


class Answer(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("answer")
        self._orig = d.select_one(".answer-text")
        self.image = d.select_one("img").attrs["src"]

    async def render(self):
        log.debug("Answer render")
        for x in self._orig.find_all("a"):
            x.attrs["href"] = convert_pixiv_link(x.attrs["href"])

        self.text = " ".join([str(x) for x in self._orig.contents])
        self.image = proxy(self.image)

        return await super().render()


class Caption(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("caption")
        self.text = d.select_one(".fab__caption").text


class UnimplementedComponent(PixivisionComponent):
    def __init__(self, component_name):
        self.component_name = component_name
        super().__init__("unknown")

    async def render(self):
        if current_app.config["DEBUG"]:
            return await super().render()
