from __future__ import annotations

from ._types import *
from .components import *

from datetime import datetime
import logging
import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Optional
    from bs4 import Tag


BG_IMG_RE = re.compile(r"background-image:url\((.+)\)")
COMPONENT_RE = re.compile(r"_feature-article-body__(.+)")
log = logging.getLogger("vixipy.lib.pixivision.parser")


def parse_spotlight(t: Tag) -> Optional[PixivisionEntry]:
    main = t.find("article", class_="_article-eyecatch-card spotlight")
    if not main:
        return None

    image = BG_IMG_RE.search(
        main.find("div", class_="_thumbnail aec__thumbnail")
        .attrs["style"]
        .replace(" ", "")
    ).group(1)
    date = datetime.strptime(main.find("time").text, "%Y.%m.%d")
    title_element = main.find("h2", class_="aec__title")
    id = int(title_element.a.attrs["data-gtm-label"])
    # Sadly this is truncated server side. Whatever...
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

    return PixivisionEntry(id, title, date, image, category, tag_list)


def parse_article_entries(t: Tag) -> list[PixivisionEntry]:
    result: list[PixivisionEntry] = []

    for card in t.find_all("li", class_="article-card-container"):
        main = card.article

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

        result.append(PixivisionEntry(id, title, date, image, category, tag_list))

    return result


def parse_article(t: Tag):
    mapping: dict[str, PixivisionComponent] = {
        "paragraph": BodyParagraph,
        "pixiv_illust": PixivArtwork,
        "heading": Heading,
        "article_thumbnail": ArticleThumb,
        "image": Image,
    }

    res: list[PixivisionComponent] = []
    total = 0
    parsed = 0

    for x in t.find("div", class_="_feature-article-body"):
        r = COMPONENT_RE.search(x.attrs["class"][1]).group(1)
        if r in mapping:
            res.append(mapping[r](x))
            log.debug("Parsed %s", r)

            parsed += 1
        else:
            log.warn("Component %s unimplemented!", r)

        total += 1

    log.debug("Parsed %d of %d components", parsed, total)
    log.debug("Resulting components: %s", res)
    return res
