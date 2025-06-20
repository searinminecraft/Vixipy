from quart import current_app, g, redirect, request, url_for
from functools import wraps


def tokenless_require_login(v):
    @wraps(v)
    async def wrapped(**kwargs):
        if current_app.no_token:
            if not g.authorized:
                return redirect(
                    url_for("login.login_page", return_to=request.path), code=303
                )

        return await v(**kwargs)

    return wrapped


def require_login(v):
    @wraps(v)
    async def wrapped(**kwargs):
        if not g.authorized:
            return redirect(
                url_for("login.login_page", return_to=request.path), code=303
            )

        return await v(**kwargs)

    return wrapped
