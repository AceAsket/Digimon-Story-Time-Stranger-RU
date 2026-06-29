from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


MENU_LABELS = {
    "ui_digivice_menu_text_000.img": "ДИГИМОНЫ",
    "ui_digivice_menu_text_001.img": "АГЕНТ",
    "ui_digivice_menu_text_002.img": "ПРЕДМЕТЫ",
    "ui_digivice_menu_text_003.img": "СИСТЕМА",
    "ui_digivice_menu_text_004.img": "ДИГИЛАЙН",
    "ui_digivice_menu_text_005.img": "МИССИИ",
}

MEMBER_LABELS = {
    "ui_digivice_member_btl_index.img": ("БОЕВОЙ", "СОСТАВ"),
    "ui_digivice_member_rsv_index.img": ("РЕЗЕРВ", ""),
}

WHITE = (232, 242, 252, 255)
GOLD = (255, 190, 38, 255)
SHADOW = (20, 27, 34, 210)
GRID = (122, 160, 190, 44)


def alignment_text(text: str) -> str:
    return (
        text.replace("Й", "И")
        .replace("й", "и")
        .replace("Ё", "Е")
        .replace("ё", "е")
    )


def make_font(font_path: Path, size: int, variation: str | None) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(font_path), size=size)
    if variation and hasattr(font, "set_variation_by_name"):
        try:
            font.set_variation_by_name(variation.encode("ascii"))
        except OSError:
            pass
    return font


def fit_font(
    font_path: Path,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    variation: str | None,
) -> ImageFont.FreeTypeFont:
    for size in range(start_size, 24, -2):
        font = make_font(font_path, size, variation)
        bbox = ImageDraw.Draw(Image.new("RGBA", (1, 1))).textbbox((0, 0), text, font=font, stroke_width=3)
        if bbox[2] - bbox[0] <= max_width and bbox[3] - bbox[1] <= max_height:
            return font
    return make_font(font_path, 24, variation)


def draw_dotted_backdrop(draw: ImageDraw.ImageDraw, width: int, height: int, x_max: int) -> None:
    for y in range(18, min(height - 18, 190), 8):
        for x in range(2, min(width, x_max), 8):
            draw.rectangle((x, y, x + 2, y + 2), fill=GRID)


def draw_shadowed_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int] = WHITE,
    stroke: int = 3,
) -> None:
    x, y = xy
    draw.text((x + 5, y + 5), text, font=font, fill=SHADOW, stroke_width=stroke, stroke_fill=SHADOW)
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(47, 57, 68, 230))


def draw_highlight_overlay(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    prefix: str,
    highlight: str,
    stroke: int = 3,
) -> None:
    x, y = xy
    highlight_x = int(round(x + draw.textlength(prefix, font=font)))
    draw.text(
        (highlight_x, y),
        highlight,
        font=font,
        fill=GOLD,
        stroke_width=stroke,
        stroke_fill=(47, 57, 68, 230),
    )


def draw_menu_label(path: Path, text: str, font_path: Path, variation: str | None) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    image = Image.new("RGBA", source.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    font = fit_font(font_path, text, max_width=900, max_height=116, start_size=118, variation=variation)
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=3)
    align_bbox = draw.textbbox((0, 0), alignment_text(text), font=font, stroke_width=3)
    text_width = bbox[2] - bbox[0]

    x = 6
    y = 74 - align_bbox[1]
    line_end = max(520, min(980, x + text_width + 72))
    draw.line((0, 42, line_end, 42), fill=GOLD, width=4)
    draw.line((0, 50, line_end - 30, 50), fill=(168, 126, 42, 120), width=2)
    draw_dotted_backdrop(draw, image.width, image.height, line_end + 90)
    draw_shadowed_text(draw, (x, y), text, font)

    return image


def draw_member_label(path: Path, parts: tuple[str, str], font_path: Path, variation: str | None) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    image = Image.new("RGBA", source.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    full_text = " ".join(part for part in parts if part)
    font = fit_font(font_path, full_text, max_width=930, max_height=100, start_size=92, variation=variation)
    bbox = draw.textbbox((0, 0), full_text, font=font, stroke_width=3)
    align_bbox = draw.textbbox((0, 0), alignment_text(full_text), font=font, stroke_width=3)
    text_height = align_bbox[3] - align_bbox[1]

    draw_dotted_backdrop(draw, image.width, image.height, min(image.width, bbox[2] - bbox[0] + 120))
    x = 20
    y = 83 + (76 - text_height) // 2 - align_bbox[1]

    first, second = parts
    if not second:
        draw_shadowed_text(draw, (x, y), first, font)
        draw_highlight_overlay(draw, (x, y), first, font, "", first[0])
        return image

    draw_shadowed_text(draw, (x, y), full_text, font)
    draw_highlight_overlay(draw, (x, y), full_text, font, f"{first} ", second[0])
    return image


def convert_png_to_bc7(texconv: Path, png_path: Path, output_dir: Path) -> Path:
    subprocess.run(
        [
            str(texconv),
            "-y",
            "-nologo",
            "-f",
            "BC7_UNORM",
            "-m",
            "1",
            "-o",
            str(output_dir),
            str(png_path),
        ],
        check=True,
    )
    return output_dir / f"{png_path.stem}.DDS"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--texconv", type=Path, required=True)
    parser.add_argument("--font", type=Path, default=Path(r"C:\Windows\Fonts\bahnschrift.ttf"))
    parser.add_argument("--font-variation", default="Bold Condensed")
    args = parser.parse_args()

    png_dir = args.work_dir / "png"
    dds_dir = args.work_dir / "dds"
    png_dir.mkdir(parents=True, exist_ok=True)
    dds_dir.mkdir(parents=True, exist_ok=True)

    generated: list[str] = []
    for file_name, text in MENU_LABELS.items():
        image = draw_menu_label(args.images_dir / file_name, text, args.font, args.font_variation)
        png_path = png_dir / f"{Path(file_name).stem}.png"
        image.save(png_path)
        dds_path = convert_png_to_bc7(args.texconv, png_path, dds_dir)
        (args.images_dir / file_name).write_bytes(dds_path.read_bytes())
        generated.append(file_name)

    for file_name, parts in MEMBER_LABELS.items():
        image = draw_member_label(args.images_dir / file_name, parts, args.font, args.font_variation)
        png_path = png_dir / f"{Path(file_name).stem}.png"
        image.save(png_path)
        dds_path = convert_png_to_bc7(args.texconv, png_path, dds_dir)
        (args.images_dir / file_name).write_bytes(dds_path.read_bytes())
        generated.append(file_name)

    print("Patched textures:")
    for item in generated:
        print(f"- {item}")


if __name__ == "__main__":
    main()
