from __future__ import annotations

from quart import (
    Blueprint,
    g,
    request,
    render_template,
    redirect,
    url_for,
)

from aiohttp import MultipartWriter
from datetime import datetime
import logging
import json
from typing import TYPE_CHECKING
from ..api import pixiv_request
from ..converters import proxy

if TYPE_CHECKING:
    from werkzeug.datastructures import FileStorage, ImmutableDict

bp = Blueprint("profile_edit", __name__)
log = logging.getLogger("vixipy.routes.profile_edit")


@bp.route("/self/edit_profile", methods=("GET", "POST"))
async def edit_profile():
    data = await pixiv_request("/ajax/my_profile", ignore_cache=True)
    if request.method == "POST":
        frm: ImmutableDict = await request.form
        files: ImmutableDict[str, FileStorage] = await request.files

        data["profileImage"] = None
        data["coverImage"] = None

        main_mp = MultipartWriter("form-data")

        if profile_image := files.get("profileImage"):
            d = profile_image.read()

            mp_verify = MultipartWriter("form-data")
            mp_verify.append(
                d, {"Content-Type": profile_image.content_type}
            ).set_content_disposition(
                "form-data", name="profile_image", filename=profile_image.name
            )

            log.debug("Validating profile image...")
            validate_res = await pixiv_request(
                "/ajax/my_profile/validate_profile_image",
                "post",
                headers={"Referer": "https://www.pixiv.net/settings/profile"},
                raw_payload=mp_verify,
            )

            log.debug("Profile image validated. data=%s", validate_res)

            main_mp.append(
                d, {"Content-Type": profile_image.content_type}
            ).set_content_disposition(
                "form-data", name="profile_image", filename=profile_image.name
            )

        if cover_image := files.get("coverImage"):
            d = cover_image.read()
            main_mp.append(
                d, {"Content-Type": cover_image.content_type}
            ).set_content_disposition(
                "form-data", name="cover_image", filename=cover_image.name
            )

        data["name"] = frm["name"]
        data["comment"] = frm["comment"]
        data["webpage"] = frm["website"]
        log.debug(data)
        data["externalService"]["twitter"] = frm["twitter"] if frm["twitter"] else None
        data["externalService"]["instagram"] = (
            frm["instagram"] if frm["instagram"] else None
        )
        data["externalService"]["tumblr"] = frm["tumblr"] if frm["tumblr"] else None
        data["externalService"]["facebook"] = (
            frm["facebook"] if frm["facebook"] else None
        )
        data["externalService"]["circlems"] = (
            frm["circlems"] if frm["circlems"] else None
        )
        data["gender"]["value"] = int(frm["gender"])
        data["gender"]["restriction"] = int(frm["gender_restrict"])

        birth = datetime.strptime(frm["birthday"], "%Y-%m-%d")

        data["birthYear"]["value"] = birth.year
        data["birthYear"]["restriction"] = int(frm["birthyear_restrict"])
        data["birthMonthAndDay"]["month"] = birth.month
        data["birthMonthAndDay"]["day"] = birth.day
        data["birthMonthAndDay"]["restriction"] = int(frm["birthday_restrict"])

        final = json.dumps(data)
        log.debug("Final payload: %s", final)

        main_mp.append(final).set_content_disposition("form-data", name="profile")
        log.debug("Submitting data...")
        await pixiv_request(
            "/ajax/my_profile/update",
            "post",
            headers={"Referer": "https://www.pixiv.net/settings/profile"},
            raw_payload=main_mp,
        )

        return redirect(url_for("users.user_profile", user=g.current_user.id))

    data["profileImage"] = proxy(data["profileImage"])
    data["coverImage"] = proxy(data["coverImage"])
    return await render_template("edit_profile.html", data=data)
