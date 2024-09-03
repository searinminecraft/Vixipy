from flask import Blueprint, render_template

devtest = Blueprint("devtest", __name__, url_prefix="/devtest")


@devtest.route("/error")
def error():
    return 1 / 0


@devtest.route("/tmplerr")
def tmplerr():
    return render_template("devtest/tmplerr.html")
