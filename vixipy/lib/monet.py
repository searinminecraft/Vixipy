from __future__ import annotations

from PIL import Image
from materialyoucolor.utils.color_utils import argb_from_rgba
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.score.score import Score
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct import Hct
from io import BytesIO
import logging
from quart import current_app
import time
from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from aiohttp import ClientResponse

log = logging.getLogger("vixipy.lib.monet")
rgba_to_hex = lambda rgba: "#{:02X}{:02X}{:02X}{:02X}".format(*map(round, rgba))
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


def get_color_scheme(data: bytes):

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

    light = SchemeTonalSpot(Hct.from_int(score[0]), False, 0.0)
    dark = SchemeTonalSpot(Hct.from_int(score[0]), True, 0.0)

    end = start = time.perf_counter()

    log.debug("Color generation took %dms", (end-start)*1000)

    res_d = ""
    res_l = ""
    for x, y in CMAPPING.items():
        res_d += f"  --md-sys-color-{x}: {get(y, dark)};\n"
        res_l += f"  --md-sys-color-{x}: {get(y, light)};\n"

    return (
        ":root {\n"
        + res_l +
        "}\n"
        "\n"
        "@media (prefers-color-scheme: dark) {\n"
        ":root {\n"
        + res_d +
        "}\n"
        "\n"
    )


async def scheme_from_url(url: str):
    """Generates a color scheme from an image URL"""

    log.debug("Generate color scheme from URL: %s", url)

    start = time.perf_counter()
    r: ClientResponse = await current_app.content_proxy.get(url)
    r.raise_for_status()

    data = await r.read()
    r.close()
    end = time.perf_counter()

    log.debug("Image retrieval took %dms", (end-start)*1000)

    return await asyncio.get_running_loop().run_in_executor(
        None,
        get_color_scheme,
        data
    )
