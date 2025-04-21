from __future__ import annotations

from quart import (
    Quart,
    g,
    request,
)
from quart_babel import Babel

from aiohttp import ClientSession, DummyCookieJar
import logging
import os
import random
from time import perf_counter
from typing import TYPE_CHECKING

from .routes import (
    index
)
from . import session as pixiv_session_handler

if TYPE_CHECKING:
    from aiohttp import ClientResponse


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
        DEBUG="0"
    )
    app.config.from_prefixed_env("VIXIPY_")

    if app.config["DEBUG"] == "1":
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    log = logging.getLogger("vixipy")
    logging.basicConfig(
        level=loglevel,
        format=("%(asctime)s    %(name)s %(levelname)s: %(message)s"),
        style="%",
    )

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
    # =================================

    pixiv_session_handler.init_app(app)

    # =================================
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
        log.info(r"   \_/  /_/\_\  ⠛⠒⠛⠉⠉⠀⠀⠀⣴⠟⣣⡴⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀v%s", app.config["VIXIPY_VERSION"])
        log.info("~~~~~~~~~~~~~~~~~~~~~~~~⠛⠛~~~~~~~~~~~~~~~~~~~~~~~~~")

        log.info("Vixipy is listening on port %s", app.config["PORT"])
        log.info("")
        log.info("Configuration:")
        log.info("  * Accept Language: %s", app.config["ACCEPT_LANGUAGE"])
        log.info("  * Instance Name: %s", app.config["INSTANCE_NAME"])
        log.info("  * Log HTTP Requests: %s", "yes" if app.config["LOG_HTTP"] == "1" else "no")
        log.info("  * Using Account: %s", "yes" if app.config["TOKEN"] != "" else "no")
        log.info("  * No R18: %s", "yes" if app.config["NO_R18"] == "1" else "no")

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

        app.pixiv: ClientSession = ClientSession(
            "https://www.pixiv.net",
            headers=header_common,
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
            r: ClientResponse = await app.pixiv.head("", allow_redirects=True)
            if phpsessid := r.cookies.get("PHPSESSID"):
                log.info("Got initial PHPSESSID: %s", phpsessid.value)
                app.pixiv_phpsessid = phpsessid.value
            else:
                log.warn("Failed to get PHPSESSID from pixiv. Using random.")
                app.pixiv_phpsessid = "".join([chr(random.randint(97, 122)) for _ in range(33)])
        else:
            r: ClientResponse = await app.pixiv.head("", headers={"Cookie": f"PHPSESSID={app.config['TOKEN']}"}, allow_redirects=True)

        app.pixiv_p_ab_d_id = r.cookies["p_ab_d_id"].value
        app.pixiv_p_ab_id = r.cookies["p_ab_id"].value
        app.pixiv_p_ab_id_2 = r.cookies["p_ab_id_2"].value

        log.info("Obtained p_ab* cookies: _id=%s, _id_2=%s, _d_id=%s",
                app.pixiv_p_ab_id, app.pixiv_p_ab_id_2, app.pixiv_p_ab_d_id)


    @app.after_serving
    async def close_clientsession():
        await app.pixiv.close()
        await app.content_proxy.close()
    # =================================

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
