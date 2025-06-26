from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from quart import Quart


def convert_config(app: Quart):
    """
    Convert configuration values to more appropriate ones
    (example when using environmental variables)
    """
    try:
        app.config["PIXIV_DIRECT_CONNECTION"] = bool(
            int(app.config["PIXIV_DIRECT_CONNECTION"])
        )
    except Exception:
        app.config["PIXIV_DIRECT_CONNECTION"] = False

    try:
        app.config["ACQUIRE_SESSION"] = bool(int(app.config["ACQUIRE_SESSION"]))
    except Exception:
        app.config["ACQUIRE_SESSION"] = True

    try:
        app.config["LOG_PIXIV"] = bool(int(app.config["LOG_PIXIV"]))
    except Exception:
        app.config["LOG_PIXIV"] = False

    try:
        app.config["LOG_HTTP"] = bool(int(app.config["LOG_HTTP"]))
    except Exception:
        app.config["LOG_HTTP"] = False

    try:
        app.config["CACHE_PIXIV_REQUESTS"] = bool(
            int(app.config["CACHE_PIXIV_REQUESTS"])
        )
    except Exception:
        app.config["CACHE_PIXIV_REQUESTS"] = False

    try:
        app.config["NO_R18"] = bool(int(app.config["NO_R18"]))
    except Exception:
        app.config["NO_R18"] = False

    try:
        app.config["NO_SENSITIVE"] = bool(int(app.config["NO_SENSITIVE"]))
    except Exception:
        app.config["NO_SENSITIVE"] = False

    if not isinstance(app.config["TOKEN"], (list, tuple, set)):
        app.config["TOKEN"] = app.config["TOKEN"].split(",")
        if app.config["TOKEN"][0] == "":
            app.config["TOKEN"] = []

    if not isinstance(app.config["BLACKLISTED_TAGS"], (list, tuple, set)):
        app.config["BLACKLISTED_TAGS"] = app.config["BLACKLISTED_TAGS"].split(",")
        if app.config["BLACKLISTED_TAGS"][0] == "":
            app.config["BLACKLISTED_TAGS"] = []


