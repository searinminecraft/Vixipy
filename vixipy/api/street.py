from __future__ import annotations

from ..abc.street import StreetData
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

    vhcs: Optional[str] = ",".join(vhc) if vhc else None
    vhis: Optional[str] = ",".join(vhi) if vhi else None
    vhms: Optional[str] = ",".join(vhm) if vhm else None
    vhns: Optional[str] = ",".join(vhn) if vhn else None

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

    data = await pixiv_request(method="post", endpoint="/ajax/street/v2/main", json_payload=payload, headers={"Referer": "https://www.pixiv.net"}, ignore_language=True, ignore_cache=True)
    return StreetData(data)
