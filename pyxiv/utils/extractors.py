from quart import current_app
import re
import logging

log = logging.getLogger("vixipy.utils.extractors")


async def extract_p_ab_d_id(phpsessid: str = None):
    headers = {}

    log.info("Acquire p_ab_d_id")

    if phpsessid:
        headers["Cookie"]: f"PHPSESSID={phpsessid}"
    # Praying for you, O great Mita
    req = await current_app.pixivApi.get("/en/artworks/126421105", headers=headers)
    req.close()
    if req.status != 200:
        log.warning("Unable to get p_ab_d_id, status %d", req.status)
        return ""

    try:
        if c := req.cookies.get("p_ab_d_id"):
            res = c.value
    except Exception:
        log.warning("Unable to extract p_ab_d_id")
        return ""

    log.debug("Successfully obtained p_ab_d_id: %s", res)
    return res
