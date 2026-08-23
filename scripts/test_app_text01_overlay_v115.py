#!/usr/bin/env python3
"""Targeted tests for the guarded app_text01 overlay."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import apply_app_text01_overlay_v115 as overlay


def write_csv(path: Path, rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle, lineterminator="\n").writerows(rows)


def read_csv(path: Path) -> list[list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.reader(handle))


def digest(value: str) -> str:
    return hashlib.sha256(overlay.canonical_value(value).encode("utf-8")).hexdigest()


class OverlayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.app = self.root / "app"
        self.patch = self.root / "patch"
        self.manifest = self.root / "manifest.json"
        self.relative = Path("text/example.mbe/000_Sheet1.csv")
        self.old_shared = "Восстанавливает HP на {d0}."
        self.new_shared = "Восстанавливает ОЗ на {d0}."
        self.old_only = "Макс. SP +"
        self.new_only = "Макс. ОС +"
        app_rows = [
            ["string2 0", "string 1", "reserved"],
            ["shared", self.old_shared, "keep-a"],
            ["app-only", self.old_only, "keep-b"],
            ["untouched", "Не менять", "keep-c"],
        ]
        patch_rows = [
            ["string2 0", "string 1", "reserved"],
            ["shared", self.new_shared, "patch-reserved"],
            ["untouched", "Другая строка патча", "patch-only"],
        ]
        write_csv(self.app / self.relative, app_rows)
        write_csv(self.patch / self.relative, patch_rows)
        raw = {
            "schema": 1,
            "forbidden_terms": ["HP", "SP"],
            "shared": [
                {
                    "section": "text",
                    "table": "example.mbe/000_Sheet1.csv",
                    "row_id": "shared",
                    "column": 1,
                    "old_sha256": digest(self.old_shared),
                }
            ],
            "app_only": [
                {
                    "section": "text",
                    "table": "example.mbe/000_Sheet1.csv",
                    "row_id": "app-only",
                    "column": 1,
                    "old_sha256": digest(self.old_only),
                    "target": self.new_only,
                }
            ],
        }
        guard = overlay.compute_table_guard(
            app_rows,
            "text",
            "example.mbe/000_Sheet1.csv",
            {("shared", 1), ("app-only", 1)},
        )
        raw["table_guards"] = [
            {
                "section": guard.section,
                "table": guard.table,
                "row_count": guard.row_count,
                "structure_sha256": guard.structure_sha256,
                "untargeted_sha256": guard.untargeted_sha256,
            }
        ]
        self.manifest.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_apply_is_narrow_and_idempotent(self) -> None:
        before = read_csv(self.app / self.relative)
        result = overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)
        after = read_csv(self.app / self.relative)
        self.assertEqual(result["changed"], 2)
        self.assertEqual(result["already_target"], 0)
        self.assertEqual(after[1], ["shared", self.new_shared, "keep-a"])
        self.assertEqual(after[2], ["app-only", self.new_only, "keep-b"])
        self.assertEqual(after[0], before[0])
        self.assertEqual(after[3], before[3])
        self.assertEqual(len(after), len(before))

        second = overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)
        self.assertEqual(second["changed"], 0)
        self.assertEqual(second["already_target"], 2)
        self.assertEqual(read_csv(self.app / self.relative), after)

    def test_dry_run_does_not_write(self) -> None:
        before = (self.app / self.relative).read_bytes()
        result = overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=True)
        self.assertEqual(result["changed"], 2)
        self.assertEqual((self.app / self.relative).read_bytes(), before)

    def test_unexpected_third_value_fails_closed(self) -> None:
        rows = read_csv(self.app / self.relative)
        rows[1][1] = "Неожиданное значение"
        write_csv(self.app / self.relative, rows)
        with self.assertRaisesRegex(RuntimeError, "unexpected third value"):
            overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)

    def test_late_failure_does_not_partially_write(self) -> None:
        late_relative = Path("text/z-last.mbe/000_Sheet1.csv")
        late_rows = [
            ["string2 0", "string 1"],
            ["late", "Неожиданное значение"],
        ]
        write_csv(self.app / late_relative, late_rows)
        write_csv(
            self.patch / late_relative,
            [["string2 0", "string 1"], ["late", "Целевое значение"]],
        )
        raw = json.loads(self.manifest.read_text(encoding="utf-8"))
        raw["shared"].append(
            {
                "section": "text",
                "table": "z-last.mbe/000_Sheet1.csv",
                "row_id": "late",
                "column": 1,
                "old_sha256": digest("Другое допустимое старое значение"),
            }
        )
        guard = overlay.compute_table_guard(
            late_rows,
            "text",
            "z-last.mbe/000_Sheet1.csv",
            {("late", 1)},
        )
        raw["table_guards"].append(
            {
                "section": guard.section,
                "table": guard.table,
                "row_count": guard.row_count,
                "structure_sha256": guard.structure_sha256,
                "untargeted_sha256": guard.untargeted_sha256,
            }
        )
        self.manifest.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")

        before = read_csv(self.app / self.relative)
        with self.assertRaisesRegex(RuntimeError, "unexpected third value"):
            overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)
        self.assertEqual(read_csv(self.app / self.relative), before)

    def test_missing_table_guards_are_rejected(self) -> None:
        raw = json.loads(self.manifest.read_text(encoding="utf-8"))
        raw.pop("table_guards")
        self.manifest.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "table_guards must be a non-empty array"):
            overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)

    def test_untargeted_value_fails_complete_table_guard(self) -> None:
        rows = read_csv(self.app / self.relative)
        rows[3][1] = "Неожиданно изменённая строка"
        write_csv(self.app / self.relative, rows)
        with self.assertRaisesRegex(RuntimeError, "table guard mismatch"):
            overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)

    def test_unguarded_table_fails_complete_coverage(self) -> None:
        write_csv(
            self.app / "text/extra.mbe/000_Sheet1.csv",
            [["string2 0", "string 1"], ["extra", "Не менять"]],
        )
        with self.assertRaisesRegex(RuntimeError, "table guard coverage mismatch"):
            overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)

    def test_changed_table_without_entries_fails_guard(self) -> None:
        extra_relative = Path("text/extra.mbe/000_Sheet1.csv")
        extra_rows = [["string2 0", "string 1"], ["extra", "Не менять"]]
        write_csv(self.app / extra_relative, extra_rows)
        raw = json.loads(self.manifest.read_text(encoding="utf-8"))
        guard = overlay.compute_table_guard(
            extra_rows,
            "text",
            "extra.mbe/000_Sheet1.csv",
            set(),
        )
        raw["table_guards"].append(
            {
                "section": guard.section,
                "table": guard.table,
                "row_count": guard.row_count,
                "structure_sha256": guard.structure_sha256,
                "untargeted_sha256": guard.untargeted_sha256,
            }
        )
        self.manifest.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        extra_rows[1][1] = "Скрыто изменилось"
        write_csv(self.app / extra_relative, extra_rows)
        with self.assertRaisesRegex(RuntimeError, "table guard mismatch"):
            overlay.apply_overlay(self.app, self.patch, self.manifest, dry_run=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
