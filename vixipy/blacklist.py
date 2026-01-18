from __future__ import annotations

import logging
from quart import abort, request, current_app
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Quart


log = logging.getLogger(__name__)


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
        "Claude",
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
            ip = request.remote_addr if not current_app.config["BEHIND_REVERSE_PROXY"] else request.headers.get["X-Real-IP"]
            log.info("User agent %s [%s] has been blocked due to user agent blacklist", str(request.user_agent), ip)
            abort(403)


def init_app(app: Quart):
    app.before_request(check_user_agent)
