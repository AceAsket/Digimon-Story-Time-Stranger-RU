from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSV_ROOT = ROOT / "csv"
APP_ROOT = ROOT / "csv" / "app_text01"
OUT_CSV = ROOT / "exports" / "translation_quality_audit_v023.csv"
OUT_JSON = ROOT / "exports" / "translation_quality_audit_v023.json"


ALLOW_LATIN = {
    "ADAMAS",
    "HP",
    "SP",
    "ATK",
    "DEF",
    "INT",
    "CRT",
    "SPD",
    "EXP",
    "SDGP",
    "PlayStation",
    "Microsoft",
    "Store",
    "Nintendo",
    "eShop",
    "DLC",
    "DigiFarm",
    "DigiLine",
}


MACHINE_PATTERNS: list[tuple[str, str, int]] = [
    (r"\bна данный момент\b", "machine_phrase: на данный момент", 2),
    (r"\bданн(ый|ая|ое|ые)\b", "machine_phrase: данный/данные", 1),
    (r"\bтот факт\b|\bфакт, что\b", "machine_phrase: тот факт", 3),
    (r"\bс вашей стороны\b|\bс твоей стороны\b", "machine_phrase: с вашей/твоей стороны", 3),
    (r"\bприсутстви[яеи]\b", "machine_phrase: присутствие", 2),
    (r"\bболее важн", "machine_phrase: более важная проблема", 3),
    (r"\bОсновываясь\b|\bосновываясь\b", "machine_phrase: основываясь", 3),
    (r"\bвизуальн(ые|ых|ым|ого) эффект", "machine_phrase: визуальные эффекты", 4),
    (r"\bУказанные ниже\b|\bуказанн", "machine_phrase: указанн*", 2),
    (r"\bв полевых условиях\b", "machine_phrase: в полевых условиях", 2),
    (r"\bв процессе обучения\b", "machine_phrase: в процессе обучения", 2),
]

MOJIBAKE_RE = re.compile(
    r"вЂ|В«|В»|Р|Рџ|РЎ|Рќ|Р“|Р”|Рљ|Рњ|Рћ|Р§|Рђ|Р‘|Р’|Р—|Р™|Р°|Рµ|Рё|Рѕ|Р°"
)
LATIN_RE = re.compile(r"[A-Za-z]{3,}")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
CONTROL_RE = re.compile(r"\{[^}]*\}|\[[^\]]*\]|%[sd]|\\n")

GENDER_RISK_RE = re.compile(
    r"\bты\s+\w*(лся|лся\b|ал\b|ил\b|ел\b|ёл\b|ен\b|готов\b|достиг\b|убрал\b|понял\b|смог\b|попытался\b)"
    r"|\bты был\b|\bтебя перенёс\b",
    re.IGNORECASE,
)


def text_column(relative: Path, row: list[str]) -> int | None:
    if relative.parts and relative.parts[0] == "message":
        return 2 if len(row) > 2 else None
    return 1 if len(row) > 1 else None


def source_text(package: str, relative: Path, key: str) -> str:
    candidates = [
        ROOT / "csv_before_fixes" / package / relative,
        ROOT / "csv_before_remaining_translation" / package / relative,
        ROOT / "csv_before_ru_quality_pass" / relative,
        APP_ROOT / relative,
    ]
    index = text_column(relative, ["", "", ""] if relative.parts[0] == "message" else ["", ""])
    if index is None:
        return ""
    for path in candidates:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.reader(f):
                if row and row[0] == key and len(row) > index:
                    return row[index]
    return ""


def is_header(row: list[str]) -> bool:
    return bool(row and row[0].startswith("string"))


def normalized_for_latin(text: str) -> str:
    cleaned = CONTROL_RE.sub(" ", text)
    for token in ALLOW_LATIN:
        cleaned = re.sub(rf"\b{re.escape(token)}\b", " ", cleaned)
    return cleaned


def english_score(text: str) -> tuple[int, str]:
    cleaned = normalized_for_latin(text)
    words = LATIN_RE.findall(cleaned)
    if not words:
        return 0, ""
    latin_chars = sum(len(w) for w in words)
    cyr = len(CYRILLIC_RE.findall(cleaned))
    if latin_chars >= 18 and latin_chars > cyr:
        return 5, "english_sentence"
    if latin_chars >= 12:
        return 3, "latin_fragment"
    return 1, "latin_token"


def add_candidate(
    rows: list[dict[str, str | int]],
    *,
    package: str,
    relative: Path,
    key: str,
    speaker: str,
    current: str,
    category: str,
    reason: str,
    severity: int,
) -> None:
    rows.append(
        {
            "severity": severity,
            "category": category,
            "reason": reason,
            "package": package,
            "file": str(relative).replace("\\", "/"),
            "key": key,
            "speaker": speaker,
            "current_ru": current,
            "source_en": source_text(package, relative, key),
            "suggested_action": "",
        }
    )


def audit() -> list[dict[str, str | int]]:
    candidates: list[dict[str, str | int]] = []
    seen: set[tuple[str, str, str, str]] = set()
    scan_roots = [
        path
        for path in sorted(CSV_ROOT.iterdir())
        if path.is_dir() and ((path / "message").exists() or (path / "text").exists())
    ]

    for package_root in scan_roots:
        package = package_root.name
        for path in sorted(package_root.rglob("*.csv")):
            relative = path.relative_to(package_root)
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                for row in csv.reader(f):
                    if is_header(row):
                        continue
                    index = text_column(relative, row)
                    if index is None or len(row) <= index:
                        continue
                    key = row[0] if row else ""
                    speaker = row[1] if relative.parts[0] == "message" and len(row) > 1 else ""
                    text = row[index].strip()
                    if not text:
                        continue

                    checks: list[tuple[str, str, int]] = []
                    latin_sev, latin_reason = english_score(text)
                    if latin_sev >= 3:
                        checks.append(("untranslated", latin_reason, latin_sev))
                    if MOJIBAKE_RE.search(text):
                        checks.append(("encoding", "mojibake", 5))
                    for pattern, reason, sev in MACHINE_PATTERNS:
                        if re.search(pattern, text, flags=re.IGNORECASE):
                            checks.append(("machine", reason, sev))
                    if ("_M" in (row[-1] if row else "") and "_F" in (row[-1] if row else "")) or speaker == "char_PLAYER_M":
                        if GENDER_RISK_RE.search(text):
                            checks.append(("gender", "gender_risk_in_shared_or_player_line", 4))

                    for category, reason, severity in checks:
                        marker = (package, str(relative), key, reason)
                        if marker in seen:
                            continue
                        seen.add(marker)
                        add_candidate(
                            candidates,
                            package=package,
                            relative=relative,
                            key=key,
                            speaker=speaker,
                            current=text,
                            category=category,
                            reason=reason,
                            severity=severity,
                        )

    candidates.sort(
        key=lambda r: (
            -int(r["severity"]),
            str(r["category"]),
            str(r["package"]),
            str(r["file"]),
            str(r["key"]),
        )
    )
    return candidates


def main() -> None:
    rows = audit()
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "severity",
        "category",
        "reason",
        "package",
        "file",
        "key",
        "speaker",
        "current_ru",
        "source_en",
        "suggested_action",
    ]
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    with OUT_JSON.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"wrote={OUT_CSV}")
    print(f"wrote={OUT_JSON}")
    print(f"candidates={len(rows)}")
    by_category: dict[str, int] = {}
    for row in rows:
        by_category[str(row["category"])] = by_category.get(str(row["category"]), 0) + 1
    for category, count in sorted(by_category.items()):
        print(f"{category}={count}")


if __name__ == "__main__":
    main()
