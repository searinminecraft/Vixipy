from flask import Blueprint, render_template

from ..core.user import getUser

users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/<int:_id>")
def userPage(_id: int):

    user = getUser(_id)

    return render_template("user.html", user=user)
