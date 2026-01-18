from __future__ import annotations

from ..converters import proxy
from datetime import datetime
from typing import Optional


class CommentBase:
    def __init__(self, d):
        self.id: int = int(d["id"])
        self.user_id: int = int(d["userId"])
        self.username: str = d["userName"]
        self.img: str = proxy(d["img"])
        self.comment: str = d["comment"]
        self.stamp_id: Optional[int] = int(d["stampId"]) if d["stampId"] else None
        self.date: datetime = datetime.strptime(d["commentDate"], "%Y-%m-%d %H:%M")
        self.editable: bool = d["editable"]

    @property
    def stamp_image(self):
        return (
            f"/proxy/s.pximg.net/common/images/stamp/generated-stamps/{self.stamp_id}_s.jpg"
            if self.stamp_id
            else None
        )


class Comment(CommentBase):
    def __init__(self, d):
        super().__init__(d)
        self.is_deleted_user: bool = d["isDeletedUser"]
        self.has_replies: bool = d["hasReplies"]


class CommentBaseResponse:
    def __init__(self, comments: list[Comment], has_next: bool):
        self.comments: list[Comment] = comments
        self.has_next: bool = has_next
