from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


CYRILLIC = set(range(0x0410, 0x0450)) | {0x0401, 0x0451}
DOT_PUNCT = {ord("."), ord(","), ord(":"), ord(";")}

PROFILES = {
    "common": {
        "letter": (48, 56),
        "overrides": {
            "В": (60, 58),
            "З": (54, 70),
            "П": (48, 72),
            "Р": (60, 62),
            "Ы": (60, 72),
            "в": (60, 60),
            "з": (54, 70),
            "п": (48, 70),
            "р": (60, 62),
            "ы": (60, 72),
        },
        "dot_punct": (78, 76),
        "bang": (72, 78),
        "question": (68, 78),
        "dash": (62, 62),
        "ellipsis": (64, 64),
    },
    "event": {
        "letter": (45, 55),
        "overrides": {
            "В": (58, 58),
            "З": (52, 68),
            "П": (45, 70),
            "Р": (58, 60),
            "Ы": (58, 70),
            "в": (58, 58),
            "з": (52, 68),
            "п": (45, 68),
            "р": (58, 60),
            "ы": (58, 70),
        },
        "dot_punct": (75, 75),
        "bang": (70, 75),
        "question": (65, 75),
        "dash": (60, 60),
        "ellipsis": (60, 60),
    },
}


def glyph_bounds(glyph_set, glyph_name: str) -> tuple[float, float, float, float]:
    pen = BoundsPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    if pen.bounds is None:
        return (0.0, 0.0, 0.0, 0.0)
    return pen.bounds


def desired_bearings(codepoint: int, profile: dict[str, tuple[int, int]]) -> tuple[int, int] | None:
    overrides = profile.get("overrides", {})
    override = overrides.get(chr(codepoint))
    if override is not None:
        return override
    if codepoint in CYRILLIC:
        return profile["letter"]
    if codepoint in DOT_PUNCT:
        return profile["dot_punct"]
    if codepoint == ord("!"):
        return profile["bang"]
    if codepoint == ord("?"):
        return profile["question"]
    if codepoint == ord("-"):
        return profile["dash"]
    if codepoint == 0x2026:
        return profile["ellipsis"]
    return None


def patch_font(input_path: Path, output_path: Path, profile_name: str) -> None:
    profile = PROFILES[profile_name]
    font = TTFont(input_path)
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"]
    top_dict = font["CFF "].cff.topDictIndex[0]

    patched = 0
    seen_glyphs: set[str] = set()

    for codepoint, glyph_name in sorted(cmap.items()):
        if glyph_name in seen_glyphs:
            continue

        bearings = desired_bearings(codepoint, profile)
        if bearings is None:
            continue

        left_bearing, right_bearing = bearings
        x_min, _y_min, x_max, _y_max = glyph_bounds(glyph_set, glyph_name)
        contour_width = x_max - x_min
        new_advance = int(round(contour_width + left_bearing + right_bearing))
        new_lsb = int(left_bearing)

        old_advance, old_lsb = hmtx[glyph_name]
        if old_advance == new_advance and old_lsb == new_lsb and int(x_min) == new_lsb:
            seen_glyphs.add(glyph_name)
            continue

        old_charstring = top_dict.CharStrings[glyph_name]
        char_pen = T2CharStringPen(width=new_advance, glyphSet=glyph_set)
        transform_pen = TransformPen(char_pen, (1, 0, 0, 1, new_lsb - x_min, 0))
        glyph_set[glyph_name].draw(transform_pen)
        top_dict.CharStrings[glyph_name] = char_pen.getCharString(
            private=old_charstring.private,
            globalSubrs=old_charstring.globalSubrs,
        )
        hmtx[glyph_name] = (new_advance, new_lsb)

        patched += 1
        seen_glyphs.add(glyph_name)

    # Keep no-break spaces visually blank in UI strings that use NBSP as an empty value.
    for table in font["cmap"].tables:
        if table.isUnicode() and 0x20 in table.cmap:
            table.cmap[0x00A0] = table.cmap[0x20]

    font["hhea"].advanceWidthMax = max(width for width, _lsb in hmtx.metrics.values())

    output_path.parent.mkdir(parents=True, exist_ok=True)
    font.save(output_path)
    print(f"{input_path} -> {output_path}: patched {patched} glyphs")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--common-in", type=Path, required=True)
    parser.add_argument("--common-out", type=Path, required=True)
    parser.add_argument("--event-in", type=Path, required=True)
    parser.add_argument("--event-out", type=Path, required=True)
    args = parser.parse_args()

    patch_font(args.common_in, args.common_out, "common")
    patch_font(args.event_in, args.event_out, "event")


if __name__ == "__main__":
    main()
