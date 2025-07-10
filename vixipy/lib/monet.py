from PIL import Image
from materialyoucolor.utils.color_utils import argb_from_rgba
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.score.score import Score
from materialyoucolor.dynamiccolor.material_dynamic_colors import MaterialDynamicColors
from materialyoucolor.hct import Hct
from io import BytesIO

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
    pixels = image.width * image.height
    image_data = image.getdata()
    pixel_array = [image_data[x] for x in range(0, pixels, 10)]

    res = QuantizeCelebi(pixel_array, 128)

    score = Score.score(res)

    light = SchemeTonalSpot(Hct.from_int(score[0]), False, 0.0)
    dark = SchemeTonalSpot(Hct.from_int(score[0]), True, 0.0)

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

