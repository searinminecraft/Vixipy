from quart import (
    Blueprint,
    render_template,
)
from ..api import pixiv_request
from ..converters import proxy, convert_pixiv_link
from ..decorators import require_login

from datetime import datetime

bp = Blueprint("notifications", __name__)

class Notification:
    def __init__(self, d):
        self.type: str = d["type"]
        self.notified_at: datetime = datetime.fromisoformat(d["notifiedAt"])
        self.link: str = convert_pixiv_link(d["linkUrl"])
        self.icon: str = proxy(d["iconUrl"])
        self.target_blank: bool = d["targetBlank"]
        self.content: str = d["content"]

@bp.route("/self/notifications")
@require_login
async def main():
    data = await pixiv_request("/ajax/notification")
    res = [Notification(x) for x in data["items"]]
    return await render_template("notifications.html", data=res)