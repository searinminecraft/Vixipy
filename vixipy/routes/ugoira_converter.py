from __future__ import annotations

from quart import (
    Blueprint,
    abort,
    current_app,
    make_response,
    render_template,
)
from typing import TYPE_CHECKING

from ..api import get_artwork

if TYPE_CHECKING:
    from aiohttp import ClientResponse

bp = Blueprint("ugoira", __name__)


@bp.get("/ugoira-converter/ffmpeg-core.wasm")
async def ffmpeg_core_proxy():
    r: ClientResponse = await current_app.content_proxy.get(
        "https://unpkg.com/@ffmpeg/core@0.12.10/dist/umd/ffmpeg-core.wasm"
    )
    r.raise_for_status()

    async def stream():
        async for x in r.content.iter_chunked(10 * 1024):
            yield x

    res = await make_response(stream())
    res.timeout = None

    return res, {
        "Content-Type": "application/wasm",
        "Content-Length": 32232419,
    }


@bp.get("/ugoira-converter/<int:id>")
async def converter_main(id: int):
    data = await get_artwork(id)
    if not data.isUgoira:
        abort(400)

    return await render_template("ugoira-converter/main.html", data=data)
