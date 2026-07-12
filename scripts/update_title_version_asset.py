#!/usr/bin/env python3
"""Regenerate the title-screen build label as a BC7 DDS asset.

This is a maintainer tool, not part of the normal release build.  The release
build consumes the committed binary asset and fails closed when its VERSION
marker differs from the repository VERSION.
"""

from __future__ import annotations

import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as error:  # pragma: no cover - maintainer environment guard
    raise SystemExit("Pillow is required to regenerate the title texture.") from error


ROOT = Path(__file__).resolve().parents[1]
ASSET_ROOT = ROOT / "assets/title_version"
BASE_ASSET = ASSET_ROOT / "ui_title_copyright_01.base.img"
OUTPUT_ASSET = ASSET_ROOT / "ui_title_copyright_01.img"
PREVIEW = ASSET_ROOT / "ui_title_copyright_01.preview.png"
ASSET_VERSION = ASSET_ROOT / "VERSION"
RELEASE_VERSION = ROOT / "VERSION"
FONT = Path(os.environ.get("DSTS_TITLE_FONT", r"C:\Windows\Fonts\arialbd.ttf"))

WIDTH = 2048
HEIGHT = 32
DDS_HEADER_SIZE = 148
BLOCK_BYTES = 16
BLOCKS_X = WIDTH // 4
BLOCKS_Y = HEIGHT // 4
FIRST_CHANGED_BLOCK_X = 133  # x=532
LAST_CHANGED_BLOCK_X = 170  # x=683


def resolve_texconv() -> Path:
    candidates = [
        os.environ.get("TEXCONV_EXE", ""),
        shutil.which("texconv.exe") or "",
        r"C:\Program Files (x86)\Steam\steamapps\common\Virtual Desktop\texconv.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    raise SystemExit("texconv.exe was not found. Set TEXCONV_EXE to DirectXTex texconv.")


def metadata(data: bytes) -> tuple[bytes, int, int, int, int, int, int]:
    if len(data) != 65_684:
        raise SystemExit(f"Unexpected DDS size: {len(data)}")
    return (
        data[:4],
        struct.unpack_from("<I", data, 12)[0],
        struct.unpack_from("<I", data, 16)[0],
        struct.unpack_from("<I", data, 28)[0],
        struct.unpack_from("<I", data, 128)[0],
        struct.unpack_from("<I", data, 132)[0],
        struct.unpack_from("<I", data, 140)[0],
    )


def main() -> None:
    version = RELEASE_VERSION.read_text(encoding="utf-8-sig").strip()
    label = f"DSTS RU v{version}"
    base = BASE_ASSET.read_bytes()
    expected_metadata = (b"DDS ", HEIGHT, WIDTH, 1, 98, 3, 1)
    if metadata(base) != expected_metadata:
        raise SystemExit(f"Unexpected base DDS metadata: {metadata(base)!r}")
    if not FONT.is_file():
        raise SystemExit(f"Title font not found: {FONT}")

    with tempfile.TemporaryDirectory(prefix="dsts-title-version-") as temporary:
        work = Path(temporary)
        composite_png = work / "ui_title_copyright_01.png"
        image = Image.open(BASE_ASSET).convert("RGBA")
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(str(FONT), 18)
        x, y = 536, 4
        bbox = draw.textbbox((x, y), label, font=font, stroke_width=1)
        if bbox[2] > 681 or bbox[3] > 24:
            raise SystemExit(f"Version label exceeds its reserved area: {bbox!r}")
        draw.text(
            (x + 1, y + 1),
            label,
            font=font,
            fill=(0, 0, 0, 160),
            stroke_width=1,
            stroke_fill=(0, 0, 0, 160),
        )
        draw.text(
            (x, y),
            label,
            font=font,
            fill=(238, 242, 247, 255),
            stroke_width=1,
            stroke_fill=(35, 42, 52, 255),
        )
        image.save(composite_png)

        texconv = resolve_texconv()
        result = subprocess.run(
            [
                str(texconv),
                "-f",
                "BC7_UNORM",
                "-m",
                "1",
                "-nogpu",
                "-singleproc",
                "-y",
                "-o",
                str(work),
                str(composite_png),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode:
            raise SystemExit(result.stdout + "\n" + result.stderr)
        encoded = (work / "ui_title_copyright_01.DDS").read_bytes()
        if metadata(encoded) != expected_metadata:
            raise SystemExit(f"Unexpected encoded DDS metadata: {metadata(encoded)!r}")

    # Keep the original header and every BC7 block outside the version label.
    # This preserves the official copyright artwork bit-for-bit.
    output = bytearray(base)
    for block_y in range(BLOCKS_Y):
        for block_x in range(FIRST_CHANGED_BLOCK_X, LAST_CHANGED_BLOCK_X + 1):
            offset = DDS_HEADER_SIZE + (block_y * BLOCKS_X + block_x) * BLOCK_BYTES
            output[offset : offset + BLOCK_BYTES] = encoded[offset : offset + BLOCK_BYTES]
    OUTPUT_ASSET.write_bytes(output)

    for block_y in range(BLOCKS_Y):
        for block_x in range(BLOCKS_X):
            if FIRST_CHANGED_BLOCK_X <= block_x <= LAST_CHANGED_BLOCK_X:
                continue
            offset = DDS_HEADER_SIZE + (block_y * BLOCKS_X + block_x) * BLOCK_BYTES
            assert output[offset : offset + BLOCK_BYTES] == base[offset : offset + BLOCK_BYTES]

    Image.open(OUTPUT_ASSET).save(PREVIEW)
    ASSET_VERSION.write_text(version, encoding="ascii")
    print(f"Generated {OUTPUT_ASSET.relative_to(ROOT)} for v{version}")
    print(f"label_bbox={bbox}")
    print(f"dds_metadata={metadata(output)!r}")


if __name__ == "__main__":
    main()
