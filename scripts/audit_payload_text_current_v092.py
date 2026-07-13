#!/usr/bin/env python3
"""Run the source-linked untranslated-text audit against the current payload."""

from __future__ import annotations

import os
from pathlib import Path

import audit_game_text01_against_translation_v030 as audit


ROOT = Path(__file__).resolve().parents[1]


def find_game_data() -> Path:
    candidates = []
    configured = os.environ.get("DSTS_GAME_DATA")
    if configured:
        candidates.append(Path(configured))
    candidates.extend(
        [
            Path(r"D:\steam\steamapps\common\Digimon Story Time Stranger\gamedata"),
            Path(r"D:\SteamLibrary\steamapps\common\Digimon Story Time Stranger\gamedata"),
        ]
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise SystemExit("Game data folder was not found; set DSTS_GAME_DATA.")


def main() -> None:
    work = ROOT / "analysis/payload_text_audit_v092"
    audit.GAME_DATA = find_game_data()
    audit.WORK_ROOT = work
    audit.ORIGINAL_CSV_ROOT = work / "original_csv"
    audit.PAYLOAD_CSV_ROOT = work / "payload_csv"
    audit.OUT_CSV = ROOT / "exports/payload_text_audit_v092.csv"
    audit.OUT_SUMMARY = ROOT / "exports/payload_text_audit_v092_summary.txt"
    audit.REPORT_LABEL = "Current game text01 vs RU payload audit v092"
    audit.PREEXTRACTED_ORIGINAL_ROOT = ROOT / "verify/game_build_23514637/text_original"
    audit.MVGL_TOOL = ROOT / ".tools/MVGLTools-v2.2.0-fixed/MVGLToolsCLI.exe"
    audit.main()


if __name__ == "__main__":
    main()
