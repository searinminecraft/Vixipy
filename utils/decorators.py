from flask import g, render_template

def authRequired(f):
    def inner(*args, **kwargs):
        if not g.userPxSession and not g.userPxCSRF:
            return render_template("unauthorized.html"), 401

        return f(*args, **kwargs)
    return inner


