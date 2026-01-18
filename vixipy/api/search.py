from __future__ import annotations

from typing import Union
from urllib.parse import quote

from .handler import pixiv_request
from ..abc.search import (
    SearchResultsIllust,
    SearchResultsManga,
    SearchResultsNovel,
    SearchResultsTop,
    TagInfo,
)


async def search(
    type_: Union["illust", "manga", "novels", "top"], query: str, **kwargs
):
    _params = []
    for k, v in kwargs.items():
        _params.append((k, v))

    data = await pixiv_request(
        f"/ajax/search/{type_}/{quote(query, safe='')}", params=_params
    )

    mapping = {
        "top": SearchResultsTop,
        "illustrations": SearchResultsIllust,
        "manga": SearchResultsManga,
        "novels": SearchResultsNovel,
    }

    if type_ not in mapping:
        raise ValueError("Invalid search type")

    return mapping[type_](data)


async def get_tag_info(tag: str):
    data = await pixiv_request(f"/ajax/search/tags/{quote(tag, safe='')}")
    return TagInfo(data)
