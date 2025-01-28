from quart import current_app
import re
import logging

log = logging.getLogger("vixipy.utils.extractors")
p_ab_regex = '\'p_ab_d_id\': "(\\d+)"'

async def extract_p_ab_d_id(phpsessid: str = None):
    headers = {}

    log.info("Acquire p_ab_d_id")

    if phpsessid:
        headers["Cookie"]: f"PHPSESSID={phpsessid}"
    # Praying for you, O great Mita
    req = await current_app.pixivApi.get("/en/artworks/126421105", headers=headers)
    if req.status != 200:
        log.warning("Unable to get p_ab_d_id, status %d", req.status)
        return ""

    try:
        res = re.search(p_ab_regex, await req.text()).group(1)
    except IndexError:
        log.warning("Unable to extract p_ab_d_id")
        return ""

    log.debug("Successfully obtained p_ab_d_id: %s", res)
    return res


