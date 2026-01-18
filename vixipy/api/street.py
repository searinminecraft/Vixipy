from __future__ import annotations

from .handler import pixiv_request

from typing import Optional


async def get_data(
    *,
    k: Optional[int] = None,
    vhc: Optional[list[int]] = None,
    vhi: Optional[list[int]] = None,
    vhm: Optional[list[int]] = None,
    vhn: Optional[list[int]] = None,
    page: Optional[int] = None,
    content_index_prev: Optional[int] = None,
):

    vhcs: Optional[str] = ",".join(vhc) or None
    vhis: Optional[str] = ",".join(vhi) or None
    vhms: Optional[str] = ",".join(vhm) or None
    vhns: Optional[str] = ",".join(vhn) or None

    payload = {
        "k": k,
        "vhc": vhcs,
        "vhi": vhis,
        "vhm": vhms,
        "vhn": vhns,
    }

    if page is not None and content_index_prev is not None:
        payload = {
            **payload,
            "params": {"p": page, "content_index_prev": content_index_prev},
        }

    data = await pixiv_request(json_payload=payload)
