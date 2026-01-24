from __future__ import annotations

from quart import (
    Blueprint,
    abort,
    render_template,
    request,
)

from asyncio import gather
from typing import TYPE_CHECKING
from ..api.artworks import get_artwork, get_artwork_pages
from ..lib.monet import scheme_from_url, get_scheme_from_color

if TYPE_CHECKING:
    from ..types import Artwork, ArtworkPage

bp = Blueprint("monet", __name__)


@bp.route("/material-you", methods=("GET", "POST"))
async def color_preview():
    _method = request.args.get("method", "color")
    _scheme = request.args.get("scheme", "tonal_spot")

    if _method == "artwork":
        _id = request.args["id"]
        data = await get_artwork(_id)
        res = await scheme_from_url(data.json["urls"]["thumb"], False, _scheme)
    elif _method == "color":
        _color = request.args.get("color", "#0096fa")
        res = get_scheme_from_color(_color, _scheme)
    else:
        abort(400)

    res_d = ""
    res_l = ""
    for x, y in res["dark"].items():
        res_d += f"  --md-sys-color-{x}: {y};\n"
    for x, y in res["light"].items():
        res_l += f"  --md-sys-color-{x}: {y};\n"

    css = (
        ":root {\n" + res_l + "}\n"
        "\n"
        "@media (prefers-color-scheme: dark) {\n"
        ":root {\n" + res_d + "}\n"
        "}\n"
        "\n"
    )

    return await render_template("monet.html.j2", color_data=res, css=css)
