from __future__ import annotations

from PIL import Image
from materialyoucolor.utils.color_utils import argb_from_rgba
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.scheme.scheme_content import SchemeContent
from materialyoucolor.scheme.scheme_expressive import SchemeExpressive
from materialyoucolor.scheme.scheme_fidelity import SchemeFidelity
from materialyoucolor.scheme.scheme_fruit_salad import SchemeFruitSalad
from materialyoucolor.scheme.scheme_monochrome import SchemeMonochrome
from materialyoucolor.scheme.scheme_neutral import SchemeNeutral
from materialyoucolor.scheme.scheme_rainbow import SchemeRainbow
from materialyoucolor.scheme.scheme_vibrant import SchemeVibrant
from materialyoucolor.score.score import Score
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct import Hct
from io import BytesIO
import logging
from quart import current_app
import time
from typing import TYPE_CHECKING
import asyncio
from ..util import add_server_timing_metric

if TYPE_CHECKING:
    from aiohttp import ClientResponse

log = logging.getLogger("vixipy.lib.monet")
rgba_to_hex = lambda rgba: "#{:02X}{:02X}{:02X}{:02X}".format(*map(round, rgba))
SCMAPPING = {
    "tonal_spot": SchemeTonalSpot,
    "content": SchemeContent,
    "expressive": SchemeExpressive,
    "fidelity": SchemeFidelity,
    "fruit_salad": SchemeFruitSalad,
    "monochrome": SchemeMonochrome,
    "neutral": SchemeNeutral,
    "rainbow": SchemeRainbow,
    "vibrant": SchemeVibrant,
}
CMAPPING = {
    "background": "background",
    "on-background": "onBackground",
    "surface": "surface",
    "surface-dim": "surfaceDim",
    "surface-bright": "surfaceBright",
    "surface-container-lowest": "surfaceContainerLowest",
    "surface-container-low": "surfaceContainerLow",
    "surface-container": "surfaceContainer",
    "surface-container-high": "surfaceContainerHigh",
    "surface-container-highest": "surfaceContainerHighest",
    "on-surface": "onSurface",
    "surface-variant": "surfaceVariant",
    "on-surface-variant": "onSurfaceVariant",
    "inverse-surface": "inverseSurface",
    "inverse-on-surface": "inverseOnSurface",
    "outline": "outline",
    "outline-variant": "outlineVariant",
    "shadow": "shadow",
    "scrim": "scrim",
    "surface-tint": "surfaceTint",
    "primary": "primary",
    "on-primary": "onPrimary",
    "primary-container": "primaryContainer",
    "on-primary-container": "onPrimaryContainer",
    "inverse-primary": "inversePrimary",
    "secondary": "secondary",
    "on-secondary": "onSecondary",
    "secondary-container": "secondaryContainer",
    "on-secondary-container": "onSecondaryContainer",
    "tertiary": "tertiary",
    "on-tertiary": "onTertiary",
    "tertiary-container": "tertiaryContainer",
    "on-tertiary-container": "onTertiaryContainer",
    "error": "error",
    "on-error": "onError",
    "error-container": "errorContainer",
    "on-error-container": "onErrorContainer",
    "primary-fixed": "primaryFixed",
    "primary-fixed-dim": "primaryFixedDim",
    "on-primary-fixed": "onPrimaryFixed",
    "on-primary-fixed-variant": "onPrimaryFixedVariant",
    "secondary-fixed": "secondaryFixed",
    "secondary-fixed-dim": "secondaryFixedDim",
    "on-secondary-fixed": "onSecondaryFixed",
    "on-secondary-fixed-variant": "onSecondaryFixedVariant",
    "tertiary-fixed": "tertiaryFixed",
    "tertiary-fixed-dim": "tertiaryFixedDim",
    "on-tertiary-fixed": "onTertiaryFixed",
    "on-tertiary-fixed-variant": "onTertiaryFixedVariant",
}


def get(p: str, s: SchemeTonalSpot):
    pr = getattr(MaterialDynamicColors, p)
    res = pr.get_hct(s).to_rgba()
    return rgba_to_hex(res)


def get_scheme(data: bytes, scheme: str = "tonal_spot"):
    data = BytesIO(data)
    image = Image.open(data)
    log.debug("Image successfully opened")
    pixels = image.width * image.height
    log.debug("Image pixels: %d", pixels)
    image_data = image.getdata()
    pixel_array = [image_data[x] for x in range(0, pixels, 10)]

    start = time.perf_counter()

    res = QuantizeCelebi(pixel_array, 128)

    score = Score.score(res)

    light = SCMAPPING[scheme](Hct.from_int(score[0]), False, 0.0)
    dark = SCMAPPING[scheme](Hct.from_int(score[0]), True, 0.0)

    end = start = time.perf_counter()

    log.debug("Color generation took %dms", (end - start) * 1000)

    return {
        "dark": {x: get(y, dark) for x, y in CMAPPING.items()},
        "light": {x: get(y, light) for x, y in CMAPPING.items()},
    }


def get_scheme_from_color(color: str, scheme: str = "tonal_spot"):
    color = int("0xff" + color.replace("#", ""), 16)

    light = SCMAPPING[scheme](Hct.from_int(color), False, 0.0)
    dark = SCMAPPING[scheme](Hct.from_int(color), True, 0.0)

    return {
        "dark": {x: get(y, dark) for x, y in CMAPPING.items()},
        "light": {x: get(y, light) for x, y in CMAPPING.items()},
    }


def get_scheme_css(data: bytes, scheme: str = "tonal_spot"):
    res = get_scheme(data, scheme)

    res_d = ""
    res_l = ""
    for x, y in res["dark"].items():
        res_d += f"  --md-sys-color-{x}: {y};\n"
    for x, y in res["light"].items():
        res_l += f"  --md-sys-color-{x}: {y};\n"

    return (
        ":root {\n" + res_l + "}\n"
        "\n"
        "@media (prefers-color-scheme: dark) {\n"
        ":root {\n" + res_d + "}\n"
        "\n"
    )


async def scheme_from_url(url: str, css=True, scheme: str = "tonal_spot"):
    """Generates a color scheme from an image URL"""

    log.debug("Generate color scheme from URL: %s", url)

    start = time.perf_counter()
    r: ClientResponse = await current_app.content_proxy.get(url)
    r.raise_for_status()

    data = await r.read()
    r.close()
    end = time.perf_counter()

    log.debug("Image retrieval took %dms", (end - start) * 1000)
    add_server_timing_metric("monet_img_download", (end - start) * 1000)

    fn = get_scheme_css if css else get_scheme

    proc_start = time.perf_counter()
    res = await asyncio.get_running_loop().run_in_executor(None, fn, data, scheme)
    proc_end = time.perf_counter()
    add_server_timing_metric("monet_process_img", (proc_end - proc_start) * 1000)
    return res
