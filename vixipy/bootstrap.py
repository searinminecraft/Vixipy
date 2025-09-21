from __future__ import annotations

import logging
import random
from aiohttp import DummyCookieJar, ClientSession
from typing import TYPE_CHECKING
from . import session as pixiv_session_handler

if TYPE_CHECKING:
    from quart import Quart

log = logging.getLogger("vixipy.bootstrap")


def init_logger(app: Quart):
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

    log.debug("Logger initialized.")


def init_msg(app: Quart):
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


async def init_clientsession(app: Quart):
    header_common = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept-Language": app.config["ACCEPT_LANGUAGE"],
        "Accept-Encoding": "gzip",
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
        log.debug("Using direct connection to pixiv.")

    app.content_proxy: ClientSession = ClientSession(
        headers={**header_common, "Referer": "https://www.pixiv.net"},
        connector_owner=False,
        cookie_jar=DummyCookieJar(),
        proxy=app.config.get("PROXY"),
    )
    app.pixivision: ClientSession = ClientSession(
        "https://www.pixivision.net",
        headers=header_common,
        connector_owner=False,
        cookie_jar=DummyCookieJar(),
        proxy=app.config.get("PROXY"),
    )

    log.debug("HTTP client sessions initialized.")


async def credential_init(app: Quart):
    if len(app.config["TOKEN"]) == 0 or app.config["DEBUG"]:
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
                    r: ClientResponse = await app.pixiv.head(
                        "", allow_redirects=True, server_hostname="www.pixiv.net"
                    )
                else:
                    r: ClientResponse = await app.pixiv.head("", allow_redirects=True)
                r.raise_for_status()
                if phpsessid := r.cookies.get("PHPSESSID"):
                    log.info("Got initial PHPSESSID: %s", phpsessid.value)
                    t_res = phpsessid.value
                else:
                    log.warn("Failed to get PHPSESSID from pixiv. Using random.")
                    t_res = "".join([chr(random.randint(97, 122)) for _ in range(33)])
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
            t: str
            log.debug("Initializing token %s", t)
            try:
                if app.config["PIXIV_DIRECT_CONNECTION"]:
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

            log.info("Initialized user %s", t.split("_")[0])

        if len(app.tokens) == 0:
            raise RuntimeError("No tokens to use.")


async def bootstrap(app: Quart):
    init_logger(app)
    await init_clientsession(app)
    await credential_init(app)
    init_msg(app)
