from __future__ import annotations

from quart import abort, request
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Quart


async def check_user_agent():
    ua = str(request.user_agent)
    agents = (
        "Amazonbot",
        "anthropic-ai",
        "AppleBot-Extended",
        "Bytespider",
        "CCBot",
        "CensysInspect",
        "ChatGPT-User",
        "Claude-Web",
        "cohere-ai",
        "DiffBot",
        "FacebookBot",
        "FriendlyCrawler",
        "Google-Extended",
        "GPTBot",
        "ICC-Crawler",
        "ImagesiftBot",
        "img2dataset",
        "meta-externalagent",
        "OAI-SearchBot",
        "Omgili",
        "PerplexityBot",
        "PetalBot",
        "Scrapy",
        "Timpibot",
        "VelenPublicWebCrawler",
        "YouBot",
        "FB_IAB",
    )

    if any([ua.__contains__(x) for x in agents]):
        if not request.path.startswith("/static"):
            abort(403)


def init_app(app: Quart):
    app.before_request(check_user_agent)
