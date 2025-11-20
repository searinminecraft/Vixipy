from __future__ import annotations

from quart import Quart, Response, current_app, g, make_response, request, redirect
from quart_babel import Babel
from quart_rate_limiter import RateLimiter, RateLimiterStoreABC, remote_addr_key

from aiohttp import ClientSession, DummyCookieJar
from datetime import datetime, timezone
import logging
import mimetypes
import os
import random
from time import perf_counter
from typing import TYPE_CHECKING, TypedDict

from .routes import (
    index,
    proxy,
    vanity,
    artworks,
    login,
    search,
    discovery,
    users,
    user_action,
    profile_edit,
    novels,
    api,
    settings,
    ugoira_converter,
    notifications,
    monet,
    rankings,
    newest,
    jump,
    pixivision,
    test,
    collection,
)
from . import (
    cache_client,
    config as cfg,
    csp,
    error_handler,
    session as pixiv_session_handler,
    blacklist,
)

if TYPE_CHECKING:
    from aiohttp import ClientResponse
    from aiomcache import Client


class Token(TypedDict):
    token: str
    p_ab_id: str
    p_ab_id_2: str
    p_ab_d_id: str
    yuid_b: str


class MemcacheStore(RateLimiterStoreABC):
    """
    A rate limiter store that uses memcached

    address: The address to connect to a memcached instance
    kwargs: Any arguments to pass to the pymemcache.Client
    """

    def __init__(self, client: Client):
        self._client: Client = client

    async def get(self, key: str, default: datetime) -> datetime:
        result = await self._client.get(bytes(key, "utf-8"))
        if result is None:
            return default
        else:
            return datetime.utcfromtimestamp(float(result.decode())).replace(
                tzinfo=timezone.utc
            )

    async def set(self, key: str, tat: datetime) -> None:
        ts = tat.timestamp()
        await self._client.set(bytes(key, "utf-8"), bytes(str(ts), "utf-8"))

    @staticmethod
    async def before_serving():
        pass

    @staticmethod
    async def after_serving():
        pass


async def limiter_key_func():
    if g.authorized:
        return g.token

    if current_app.config["BEHIND_REVERSE_PROXY"]:
        return request.headers["X-Forwarded-For"] or request.remote_addr

    return await remote_addr_key()


def create_app():
    app = Quart(__name__, instance_relative_config=True, static_folder=None)
    app.config.from_mapping(
        VIXIPY_VERSION="3.4.1",
        ACCEPT_LANGUAGE="en_US,en;q=0.9",
        BEHIND_REVERSE_PROXY=False,
        BLACKLISTED_TAGS=[],
        SECRET_KEY="Vyxie",
        INSTANCE_NAME="Vixipy",
        LANGUAGES=["en", "ja", "zh_Hans", "zh_Hant", "fil", "de", "ru", "uk"],
        LOG_HTTP="1",
        LOG_PIXIV="1",
        CACHE_PIXIV_REQUESTS="0",
        CACHE_TTL="300",
        NO_R18="0",
        NO_SENSITIVE="0",
        PORT="8000",
        TOKEN="",
        IMG_PROXY="/proxy/i.pximg.net",
        PIXIV_DIRECT_CONNECTION="0",
        ACQUIRE_SESSION="0",
        QUART_RATE_LIMITER_ENABLED=False,
        COMPRESS_RESPONSE=True,
        DEFAULT_THEMES=[
            "red",
            "orange",
            "yellow",
            "green",
            "sea-green",
            "purple",
            "pink",
            "pixiv-cyan",
            "monochrome",
        ],
        ADDITIONAL_THEMES=[],
        DEFAULT_THEME="",
    )
    app.config.from_prefixed_env("VIXIPY")
    app.config.from_pyfile(app.instance_path + "/config.py", silent=True)
    cfg.convert_config(app)
    csp.init_app(app)

    app.tokens: list[Token] = []
    app.no_token = False

    log = logging.getLogger("vixipy")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def get_user_language():
        if lang := request.cookies.get("Vixipy-Language"):
            return lang

        return request.accept_languages.best_match(app.config["LANGUAGES"])

    Babel(app, locale_selector=get_user_language)
    if app.config["COMPRESS_RESPONSE"]:
        from quart_compress import Compress

        Compress(app)

    app.register_blueprint(index)
    app.register_blueprint(proxy)
    app.register_blueprint(vanity)
    app.register_blueprint(artworks)
    app.register_blueprint(login)
    app.register_blueprint(search)
    app.register_blueprint(discovery)
    app.register_blueprint(users)
    app.register_blueprint(user_action)
    app.register_blueprint(profile_edit)
    app.register_blueprint(novels)
    app.register_blueprint(api)
    app.register_blueprint(settings)
    app.register_blueprint(ugoira_converter)
    app.register_blueprint(notifications)
    app.register_blueprint(monet)
    app.register_blueprint(rankings)
    app.register_blueprint(newest)
    app.register_blueprint(jump)
    app.register_blueprint(pixivision)
    app.register_blueprint(test)
    app.register_blueprint(collection)

    # =================================

    if app.config["LOG_HTTP"]:

        @app.before_request
        async def record_begin_time():
            g.req_start = perf_counter()

        @app.after_request
        async def log_req(r):
            g.req_end = perf_counter()
            g.time_taken = (g.req_end - g.req_start) * 1000

            log.info(
                "%s %s - %s %dms", request.method, request.url, r.status, g.time_taken
            )
            return r

    blacklist.init_app(app)

    @app.before_request
    async def check_path():
        if request.path.startswith("/en"):
            stripped = request.path.removeprefix("/en")
            if stripped == "":
                return redirect("/", code=308)
            else:
                return redirect(stripped, code=308)

    @app.after_request
    async def funny_headers(r: Response):
        r.headers["Server"] = "Monika"
        r.headers["X-Powered-By"] = "Your Reality"
        return r

    if app.config["DEBUG"]:

        @app.after_request
        async def disable_cache(r: Response):
            r.headers["Cache-Control"] = "no-cache"
            return r

    # =================================

    pixiv_session_handler.init_app(app)
    error_handler.init_app(app)
    cache_client.init_app(app)

    limiter = RateLimiter(
        app, store=MemcacheStore(app.cache_client), key_function=limiter_key_func
    )
    # =================================

    @app.route("/static/<path:resource>")
    async def custom_static_folder(resource: str):

        if app.config["DEBUG"]:
            h = {"Cache-Control": "no-cache"}
        else:
            h = {"Cache-Control": "max-age=86400"}

        try:
            async with await app.open_instance_resource("custom/" + resource) as f:
                r = await f.read()
                return r, {"Content-Type": mimetypes.guess_file_type(resource)[0], **h}
        except Exception:
            async with await app.open_resource("static/" + resource) as f:
                r = await f.read()
                return r, {"Content-Type": mimetypes.guess_type(resource)[0], **h}

    @app.route("/robots.txt")
    async def robots_txt():
        try:
            async with await app.open_instance_resource("custom/robots.txt") as f:
                r = await f.read()
                return r, {"Content-Type": "text/plain"}
        except Exception:
            return await custom_static_folder("robots.txt")

    # =================================

    @app.after_serving
    async def close_clientsession():
        await app.pixiv.close()
        await app.content_proxy.close()
        await app.pixivision.close()

    # =================================

    return app
