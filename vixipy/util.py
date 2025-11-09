from quart import request


def is_consented():
    return request.cookies.get("Vixipy-Consented") == "1"
