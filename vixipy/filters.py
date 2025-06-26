from __future__ import annotations

import logging
from quart import current_app, request
from typing import TYPE_CHECKING

from .types import ArtworkEntry

if TYPE_CHECKING:
    from .types import NovelEntry, NovelSeriesEntry
    from typing import Union

log = logging.getLogger("vixipy.filters")


def check_blacklisted_tag(key: str):
    return any([key.__contains__(x) for x in current_app.config["BLACKLISTED_TAGS"]])


def filter_from_prefs(works: list[Union[ArtworkEntry, NovelEntry, NovelSeriesEntry]]):
    hide_r18_instancewide = current_app.config["NO_R18"]
    hide_r18 = bool(int(request.cookies.get("Vixipy-No-R18", 0)))
    hide_r18g = bool(int(request.cookies.get("Vixipy-No-R18G", 0)))
    hide_ai = bool(int(request.cookies.get("Vixipy-No-AI", 0)))
    hide_sensitive = current_app.config["NO_SENSITIVE"] or bool(
        int(request.cookies.get("Vixipy-No-Sensitive", 0))
    )

    new_works = works.copy()

    for x in works:
        if any([check_blacklisted_tag(y) for y in x.tags]):
            log.debug("Removing %s because one of tags contain blacklisted tag")
            new_works.remove(x)
            continue

        if isinstance(x, ArtworkEntry) and x.sensitive and hide_sensitive:
            log.debug("Removing %s because sensitive = %s", x, x.sensitive)
            new_works.remove(x)
            continue
        if (hide_r18_instancewide and x.xrestrict >= 1) or (
            hide_r18 and x.xrestrict >= 1
        ):
            log.debug("Removing %s because it is R18", x)
            new_works.remove(x)
            continue
        if (hide_r18_instancewide and x.xrestrict >= 1) or (
            (hide_r18 and x.xrestrict != 0) or (hide_r18g and x.xrestrict == 2)
        ):
            log.debug("Removing %s because it is R18G", x)
            new_works.remove(x)
            continue
        if x.ai and hide_ai:
            log.debug("Removing %s because it is AI", x)
            new_works.remove(x)
            continue

    return new_works
