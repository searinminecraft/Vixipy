from quart import (
    Quart,
    g,
    request,
)
from quart_babel import Babel

from aiohttp import ClientSession, DummyCookieJar
import logging
import os
from time import perf_counter


def create_app():
    app = Quart(__name__, instance_relative_config=True)
    app.config.from_mapping(
        VIXIPY_VERSION="3",
        ACCEPT_LANGUAGE="en_US;en,q=0.9",
        SECRET_KEY="Vyxie",
        INSTANCE_NAME="Vixipy",
        LANGUAGES=[],
        LOG_HTTP="true",
    )
    app.config.from_prefixed_env("VIXIPY_")

    fmt = logging.Formatter("")
    logging.basicConfig(style="%")

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    def get_user_language():
        if lang := request.cookies.get("Vixipy-Language"):
            return lang

        return request.accept_languages.best_match(app.config["LANGUAGES"])

    babel = Babel(app, locale_selector=get_user_language)

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
            headers={**header_common, "Referer": "https://www.pixiv.net/"},
            connector_owner=False,
            cookie_jar=DummyCookieJar(),
        )

    @app.after_serving
    async def close_clientsession():
        await app.pixiv.close()
        await app.content_proxy.close()

    # =================================
    if app.config["LOG_HTTP"] == "true":
        @app.before_request
        async def record_begin_time():
            g.req_start = perf_counter()

        @app.after_request
        async def log_req(r):
            g.req_end = perf_counter()
            g.time_taken = (g.req_end - g.req_start) * 1000

            app.logger.info(
                "%s %s - %s %dms", request.method, request.url, r.status, g.time_taken
            )
            return r
    # =================================

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
