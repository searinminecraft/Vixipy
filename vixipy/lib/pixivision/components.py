from __future__ import annotations

from quart import render_template
from typing import TYPE_CHECKING
from ...converters import convert_pixiv_link, proxy

if TYPE_CHECKING:
    from bs4 import Tag


class PixivisionComponent:
    def __init__(self, component: str):
        self.component = component

    async def render(self):
        """Renders the component"""
        return await render_template(
            f"pixivision/components/{self.component}.html", data=self
        )


class BodyParagraph(PixivisionComponent):
    def __init__(self, d: Tag):
        super().__init__("body_paragraph")

        self.body = "\n".join([str(x) for x in d.div.contents])


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

        self.type = d.name
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
        self.link = d.select_one("a").attrs["href"]
        self.clearfix = d.select_one(".fab__clearfix").text or None

    async def render(self):
        self.image = proxy(self.image)
        self.link = convert_pixiv_link(self.link)
        return await super().render()


class UnimplementedComponent(PixivisionComponent):
    def __init__(self):
        super().__init__("unknown")
