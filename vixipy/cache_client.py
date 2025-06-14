from __future__ import annotations

import aiomcache
from quart import current_app
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Quart

async def close_mc():
    await current_app.cache_client.close()

def init_app(app: Quart):
    app.cache_client = aiomcache.Client(
        app.config.get("MEMCACHED_HOST", "127.0.0.1"),
        int(app.config.get("MEMCACHED_PORT", 11211))
    )

    app.after_serving(close_mc)

    