from __future__ import annotations

from quart import (
    Blueprint,
    render_template
)
from asyncio import gather
from typing import TYPE_CHECKING

from ..api import (
    get_artwork,
    get_artwork_pages,
    get_recommended_works
)

if TYPE_CHECKING:
    from ..types import (
        Artwork,
        ArtworkEntry,
        ArtworkPage
    )

bp = Blueprint("artworks", __name__)


@bp.get('/artworks/<int:id>')
async def _get_artwork(id: int):
    work: Artwork = await get_artwork(id)
    pages, recommend = await gather(
        get_artwork_pages(id),
        get_recommended_works(id),
    )

    pages: list[ArtworkPage]
    recommend: list[ArtworkEntry]

    return await render_template("artworks.html", work=work, pages=pages, recommend=recommend)
    