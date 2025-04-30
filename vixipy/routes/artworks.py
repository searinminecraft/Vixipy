from __future__ import annotations

from quart import Blueprint, render_template
from asyncio import gather
from typing import TYPE_CHECKING

from ..api import get_artwork, get_artwork_pages, get_recommended_works, get_user, get_user_illusts_from_ids

if TYPE_CHECKING:
    from ..types import Artwork, ArtworkEntry, ArtworkPage, PartialUser

bp = Blueprint("artworks", __name__)


@bp.get("/artworks/<int:id>")
async def _get_artwork(id: int):
    work: Artwork = await get_artwork(id)
    pages, recommend, user, works = await gather(
        get_artwork_pages(id),
        get_recommended_works(id),
        get_user(work.authorId),
        get_user_illusts_from_ids(work.authorId, work.works_missing[:50]),
    )

    pages: list[ArtworkPage]
    recommend: list[ArtworkEntry]
    user: PartialUser
    works: list[ArtworkEntry]

    return await render_template(
        "artworks.html", work=work, pages=pages, recommend=recommend, user=user, user_works=sorted(works + work.other_works, key=lambda _: int(_.id))
    )
