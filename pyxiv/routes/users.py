from flask import Blueprint, render_template

from ..core.user import getUser
from ..classes import User

users = Blueprint("users", __name__, url_prefix="/users")


@users.route("/<int:_id>")
def userPage(_id: int):

    if _id == 0:
        user = User({
            "userId": 0,
            "name": "-----",
            "comment": "This user is hard coded on Vixipy to take place of deleted/unknown users",
            "image": "https://s.pximg.net/common/images/no_profile_s.png",
            "imageBig": "https://s.pximg.net/common/images/no_profile.png",
            "premium": False,
            "background": None,
            "following": 0,
            "mypixivCount": 0,
            "official": True
        })
    else:
        user = getUser(_id)

    return render_template("user.html", user=user)
