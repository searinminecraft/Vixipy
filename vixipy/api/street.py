from __future__ import annotations

from ..abc.street import StreetData
from .handler import pixiv_request

import logging
from typing import Optional


log = logging.getLogger(__name__)


async def get_data(
    *,
    k: Optional[int] = None,
    vhc: Optional[list[str]] = None,
    vhi: Optional[list[str]] = None,
    vhm: Optional[list[str]] = None,
    vhn: Optional[list[str]] = None,
    page: Optional[int] = None,
    content_index_prev: Optional[int] = None,
):

    vhis = ','.join(vhi) if vhi else None
    vhms = ','.join(vhm) if vhm else None
    vhns = ','.join(vhn) if vhn else None
    vhcs = ','.join(vhc) if vhc else None

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
            "params": {"page": page, "content_index_prev": content_index_prev},
        }

    log.debug(payload)
    data = await pixiv_request(method="post", endpoint="/ajax/street/v2/main", json_payload=payload, headers={"Referer": "https://www.pixiv.net"}, ignore_language=True, ignore_cache=True)
    return StreetData(data)
