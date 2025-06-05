from __future__ import annotations

from quart import (
    Quart,
    Response,
    g,
    request,
)
from quart_babel import Babel

from aiohttp import ClientSession, DummyCookieJar
import logging
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
    user_action
)
from . import session as pixiv_session_handler
from . import error_handler

if TYPE_CHECKING:
    from aiohttp import ClientResponse

class Token(TypedDict):
    token: str
    p_ab_id: str
    p_ab_id_2: str
    p_ab_d_id: str
    yuid_b: str


def create_app():
    app = Quart(__name__, instance_relative_config=True)
    app.config.from_mapping(
        VIXIPY_VERSION="3",
        ACCEPT_LANGUAGE="en_US,en;q=0.9",
        SECRET_KEY="Vyxie",
        INSTANCE_NAME="Vixipy",
        LANGUAGES=[],
        LOG_HTTP="1",
        NO_R18="0",
        PORT="8000",
        TOKEN="",
        IMG_PROXY="/proxy/i.pximg.net",
        PIXIV_DIRECT_CONNECTION="0"
    )
    app.config.from_prefixed_env("VIXIPY")
    app.tokens: list[Token] = []
    app.no_token = False

    log = logging.getLogger("vixipy")

    try:
        app.config["PIXIV_DIRECT_CONNECTION"] = bool(int(app.config["PIXIV_DIRECT_CONNECTION"]))
    except Exception:
        app.config["PIXIV_DIRECT_CONNECTION"] = False

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

    # =================================
    if app.config["LOG_HTTP"] == "1":

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

    if app.config["DEBUG"]:

        @app.after_request
        async def disable_cache(r: Response):
            r.headers["Cache-Control"] = "no-cache"
            return r

    # =================================

    pixiv_session_handler.init_app(app)
    error_handler.init_app(app)

    # =================================
    @app.before_serving
    def init_logger():
        if app.config["DEBUG"]:
            loglevel = logging.DEBUG
            logging.getLogger("asyncio").setLevel(logging.ERROR)
        else:
            loglevel = logging.INFO

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
        log.info("  * Instance Name: %s", app.config["INSTANCE_NAME"])
        log.info(
            "  * Log HTTP Requests: %s",
            "yes" if app.config["LOG_HTTP"] == "1" else "no",
        )
        log.info("  * Using Account: %s", "yes" if app.config["TOKEN"] != "" else "no")
        log.info("  * No R18: %s", "yes" if app.config["NO_R18"] == "1" else "no")
        log.info("  * Image Proxy: %s", app.config["IMG_PROXY"])
        log.info("  * Bypass Cloudflare: %s", app.config["PIXIV_DIRECT_CONNECTION"])
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
            )
        else:
            app.pixiv: ClientSession = ClientSession(
                "https://210.140.139.155",
                headers={**header_common, "Host": "www.pixiv.net"},
                connector_owner=False,
                cookie_jar=DummyCookieJar(),
            )

        app.content_proxy: ClientSession = ClientSession(
            headers={**header_common, "Referer": "https://www.pixiv.net"},
            connector_owner=False,
            cookie_jar=DummyCookieJar(),
        )

    @app.before_serving
    async def credential_init():
        if app.config["TOKEN"] == "":
            app.no_token = True

             
            if app.config["PIXIV_DIRECT_CONNECTION"]:
                log.debug("Use Direct Connection to pixiv")
                r: ClientResponse = await app.pixiv.head("", allow_redirects=True, server_hostname="www.pixiv.net")
            else:
                r: ClientResponse = await app.pixiv.head("", allow_redirects=True)
            r.raise_for_status()
            if phpsessid := r.cookies.get("PHPSESSID"):
                log.info("Got initial PHPSESSID: %s", phpsessid.value)
                t_res = phpsessid.value
            else:
                log.warn("Failed to get PHPSESSID from pixiv. Using random.")
                t_res = "".join(
                    [chr(random.randint(97, 122)) for _ in range(33)]
                )

            app.tokens.append({
                "token": t_res,
                "p_ab_d_id": r.cookies["p_ab_d_id"].value,
                "p_ab_id": r.cookies["p_ab_id"].value,
                "p_ab_id_2": r.cookies["p_ab_id_2"].value,
                "yuid_b": r.cookies["yuid_b"].value
            })
        else:
            for t in app.config["TOKEN"].split(","):
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
                        "",
                        allow_redirects=True,
                        server_hostname="www.pixiv.net"
                    )
                else:
                    r2: ClientResponse = await app.pixiv.head(
                        "",
                        allow_redirects=True,
                    )


                app.tokens.append({
                    "token": t,
                    "p_ab_d_id": r.cookies["p_ab_d_id"].value,
                    "p_ab_id": r.cookies["p_ab_id"].value,
                    "p_ab_id_2": r.cookies["p_ab_id_2"].value,
                    "yuid_b": r2.cookies["yuid_b"].value
                })
            
            if len(app.tokens) == 0:
                raise RuntimeError("No tokens to use.")

    @app.after_serving
    async def close_clientsession():
        await app.pixiv.close()
        await app.content_proxy.close()

    # =================================

    return app
