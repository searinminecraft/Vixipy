from __future__ import annotations

from quart import Quart, Response, current_app, g, make_response, request, redirect
from quart_babel import Babel
from quart_rate_limiter import RateLimiter, RateLimiterStoreABC, remote_addr_key

from aiohttp import ClientSession, DummyCookieJar
from datetime import datetime
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
    upload,
    discovery,
    users,
    user_action,
    profile_edit,
    novels,
    api,
    settings,
)
from . import cache_client, config as cfg, csp, error_handler, session as pixiv_session_handler

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
            return datetime.fromtimestamp(float(result.decode()))

    async def set(self, key: str, tat: datetime) -> None:
        ts = tat.timestamp()
        await self._client.set(
            bytes(key, "utf-8"), bytes(str(ts), "utf-8"))

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
        VIXIPY_VERSION="3",
        ACCEPT_LANGUAGE="en_US,en;q=0.9",
        BEHIND_REVERSE_PROXY=False,
        BLACKLISTED_TAGS=[],
        SECRET_KEY="Vyxie",
        INSTANCE_NAME="Vixipy",
        LANGUAGES=["en", "ja", "fil", "ru", "uk"],
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

    babel = Babel(app, locale_selector=get_user_language)

    app.register_blueprint(index)
    app.register_blueprint(proxy)
    app.register_blueprint(vanity)
    app.register_blueprint(artworks)
    app.register_blueprint(login)
    app.register_blueprint(search)
    app.register_blueprint(upload)
    app.register_blueprint(discovery)
    app.register_blueprint(users)
    app.register_blueprint(user_action)
    app.register_blueprint(profile_edit)
    app.register_blueprint(novels)
    app.register_blueprint(api)
    app.register_blueprint(settings)

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

    limiter = RateLimiter(app, store=MemcacheStore(app.cache_client), key_function=limiter_key_func)

    # =================================
    @app.before_serving
    def init_logger():
        if app.config["DEBUG"]:
            loglevel = logging.DEBUG
            logging.getLogger("asyncio").setLevel(logging.ERROR)
        else:
            loglevel = logging.INFO

        if not app.config["DEBUG"]:
            logging.getLogger("vixipy.api").setLevel(
                logging.INFO if app.config["LOG_PIXIV"] else logging.WARNING
            )

        logging.basicConfig(
            level=loglevel,
            format=("%(asctime)s    %(name)s %(levelname)s: %(message)s"),
            style="%",
        )

    @app.before_serving
    def init_msg():
        if os.path.exists(os.path.join(app.instance_path, ".running")):
            return
        log.info("                ⠀⠀⠀⠀⢀⡴⣆⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⣼⣿⡗⠀⠀⠀⠀")
        log.info("                ⠀⠀⠀⣠⠟⠀⠘⠷⠶⠶⠶⠾⠉⢳⡄⠀⠀⠀⠀⠀⣧⣿⠀⠀⠀⠀⠀")
        log.info("                ⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣤⣤⣤⣤⣤⣿⢿⣄⠀⠀⠀⠀")
        log.info(r" __   ____  __  ⠀⠀⡇⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠙⣷⡴⠶⣦")
        log.info(r" \ \ / /\ \/ /  ⠀⠀⢱⡀⠀⠉⠉⠀⠀⠀⠀⠛⠃⠀⢠⡟⠂⠀⠀⢀⣀⣠⣤⠿⠞⠛⠋")
        log.info(r"  \ V /  >  <   ⣠⠾⠋⠙⣶⣤⣤⣤⣤⣤⣀⣠⣤⣾⣿⠴⠶⠚⠋⠉⠁⠀⠀⠀⠀⠀⠀")
        log.info(
            r"   \_/  /_/\_\  ⠛⠒⠛⠉⠉⠀⠀⠀⣴⠟⣣⡴⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀v%s",
            app.config["VIXIPY_VERSION"],
        )
        log.info("~~~~~~~~~~~~~~~~~~~~~~~~⠛⠛~~~~~~~~~~~~~~~~~~~~~~~~~")
        log.info("")
        log.info("Configuration:")
        log.info("  * Accept Language: %s", app.config["ACCEPT_LANGUAGE"])
        log.info("  * Acquire Session: %s", app.config["ACQUIRE_SESSION"])
        log.info("  * Instance Name: %s", app.config["INSTANCE_NAME"])
        log.info("  * Log HTTP Requests: %s", app.config["LOG_HTTP"])
        log.info("  * Log pixiv Requests: %s", app.config["LOG_PIXIV"])
        log.info("  * Cache pixiv Requests: %s", app.config["CACHE_PIXIV_REQUESTS"])
        if app.config["CACHE_PIXIV_REQUESTS"]:
            log.info("  * Cache TTL: %s", app.config["CACHE_TTL"])
        log.info("  * Using Account: %s", len(app.config["TOKEN"]) > 0)
        log.info("  * No R18: %s", app.config["NO_R18"] or app.config["NO_SENSITIVE"])
        log.info("  * No Sensitive Works: %s", app.config["NO_SENSITIVE"])
        log.info("  * Image Proxy: %s", app.config["IMG_PROXY"])
        log.info("  * Bypass Cloudflare: %s", app.config["PIXIV_DIRECT_CONNECTION"])
        log.info("  * Rate Limit Enabled: %s", app.config["QUART_RATE_LIMITER_ENABLED"])
        log.info("  * Debug: %s", app.config["DEBUG"])

        with open(os.path.join(app.instance_path, ".running"), "w") as f:
            f.write("")

    @app.after_serving
    def cleanup():
        try:
            os.remove(os.path.join(app.instance_path, ".running"))
        except (FileNotFoundError, OSError):
            pass

    # =================================

    @app.route("/static/<path:resource>")
    async def custom_static_folder(resource: str):

        try:
            async with await app.open_instance_resource("custom/" + resource) as f:
                r = await f.read()
                return r, {"Content-Type": mimetypes.guess_file_type(resource)[0]}
        except Exception:
            async with await app.open_resource("static/" + resource) as f:
                r = await f.read()
                return r, {"Content-Type": mimetypes.guess_type(resource)[0]}

    @app.route("/robots.txt")
    async def robots_txt():
        try:
            async with await app.open_instance_resource("custom/robots.txt") as f:
                r = await f.read()
                return r, {"Content-Type": "text/plain"}
        except Exception:
            return await custom_static_folder("robots.txt")

    # =================================
    @app.before_serving
    async def prepare_clientsession():
        header_common = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:137.0) Gecko/20100101 Firefox/137.0",
            "Accept-Language": app.config["ACCEPT_LANGUAGE"],
        }

        if not app.config["PIXIV_DIRECT_CONNECTION"]:
            app.pixiv: ClientSession = ClientSession(
                "https://www.pixiv.net",
                headers=header_common,
                connector_owner=False,
                cookie_jar=DummyCookieJar(),
                proxy=app.config.get("PROXY"),
            )
        else:
            app.pixiv: ClientSession = ClientSession(
                "https://210.140.139.155",
                headers={**header_common, "Host": "www.pixiv.net"},
                connector_owner=False,
                cookie_jar=DummyCookieJar(),
                proxy=app.config.get("PROXY"),
            )

        app.content_proxy: ClientSession = ClientSession(
            headers={**header_common, "Referer": "https://www.pixiv.net"},
            connector_owner=False,
            cookie_jar=DummyCookieJar(),
            proxy=app.config.get("PROXY"),
        )

    @app.before_serving
    async def credential_init():
        if len(app.config["TOKEN"]) == 0:
            app.no_token = True

            if not app.config["ACQUIRE_SESSION"]:
                log.info("Skipping session acquisition from pixiv. Using random token.")
                t_res = "".join([chr(random.randint(97, 122)) for _ in range(33)])
                yuidb, p_ab_d_id, p_ab_id, p_ab_id_2 = (
                    pixiv_session_handler._generate_ab_cookies()
                )
                app.tokens.append(
                    {
                        "token": t_res,
                        "p_ab_d_id": p_ab_d_id,
                        "p_ab_id": p_ab_id,
                        "p_ab_id_2": p_ab_id_2,
                        "yuid_b": yuidb,
                    }
                )
            else:
                try:
                    if app.config["PIXIV_DIRECT_CONNECTION"]:
                        log.debug("Use Direct Connection to pixiv")
                        r: ClientResponse = await app.pixiv.head(
                            "", allow_redirects=True, server_hostname="www.pixiv.net"
                        )
                    else:
                        r: ClientResponse = await app.pixiv.head(
                            "", allow_redirects=True
                        )
                    r.raise_for_status()

                    if phpsessid := r.cookies.get("PHPSESSID"):
                        log.info("Got initial PHPSESSID: %s", phpsessid.value)
                        t_res = phpsessid.value
                    else:
                        log.warn("Failed to get PHPSESSID from pixiv. Using random.")
                        t_res = "".join(
                            [chr(random.randint(97, 122)) for _ in range(33)]
                        )

                    app.tokens.append(
                        {
                            "token": t_res,
                            "p_ab_d_id": r.cookies["p_ab_d_id"].value,
                            "p_ab_id": r.cookies["p_ab_id"].value,
                            "p_ab_id_2": r.cookies["p_ab_id_2"].value,
                            "yuid_b": r.cookies["yuid_b"].value,
                        }
                    )
                except Exception as e:
                    log.warn(
                        "Failed to acquire session from pixiv (error: %s). Using fallback token.",
                        str(e),
                    )
                    t_res = "".join([chr(random.randint(97, 122)) for _ in range(33)])
                    yuidb, p_ab_d_id, p_ab_id, p_ab_id_2 = (
                        pixiv_session_handler._generate_ab_cookies()
                    )
                    app.tokens.append(
                        {
                            "token": t_res,
                            "p_ab_d_id": p_ab_d_id,
                            "p_ab_id": p_ab_id,
                            "p_ab_id_2": p_ab_id_2,
                            "yuid_b": yuidb,
                        }
                    )
        else:
            for t in app.config["TOKEN"]:
                try:

                    if app.config["PIXIV_DIRECT_CONNECTION"]:
                        log.debug("Use Direct Connection to pixiv")
                        r: ClientResponse = await app.pixiv.head(
                            "",
                            headers={"Cookie": f"PHPSESSID={t}"},
                            server_hostname="www.pixiv.net",
                            allow_redirects=True,
                        )
                    else:
                        r: ClientResponse = await app.pixiv.head(
                            "",
                            headers={"Cookie": f"PHPSESSID={t}"},
                            allow_redirects=True,
                        )
                    r.raise_for_status()
                except Exception:
                    log.exception("Error at token %s. Skipping.", t)
                    continue

                if app.config["PIXIV_DIRECT_CONNECTION"]:
                    r2: ClientResponse = await app.pixiv.head(
                        "", allow_redirects=True, server_hostname="www.pixiv.net"
                    )
                else:
                    r2: ClientResponse = await app.pixiv.head(
                        "",
                        allow_redirects=True,
                    )

                app.tokens.append(
                    {
                        "token": t,
                        "p_ab_d_id": r.cookies["p_ab_d_id"].value,
                        "p_ab_id": r.cookies["p_ab_id"].value,
                        "p_ab_id_2": r.cookies["p_ab_id_2"].value,
                        "yuid_b": r2.cookies["yuid_b"].value,
                    }
                )

            if len(app.tokens) == 0:
                raise RuntimeError("No tokens to use.")

    @app.after_serving
    async def close_clientsession():
        await app.pixiv.close()
        await app.content_proxy.close()

    # =================================

    return app
