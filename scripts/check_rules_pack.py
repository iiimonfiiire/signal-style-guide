"""Check that signal.rules.toml stays in step with SIGNAL.md.

Fails when a rule cites a section that SIGNAL.md does not have, when the pack
version differs from the guide's "Last revision" date, or when the pack carries
an author line. Plain Python 3.11, no dependencies.
"""

from __future__ import annotations

import re
import sys
import tomllib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "SIGNAL.md"
PACK = ROOT / "signal.rules.toml"
SEVERITIES = {"error", "warning", "suggestion"}


def revision_date(guide: str) -> str:
    m = re.search(r"^\s*[-*]\s+\*\*Last revision:?\*\*:?\s*(.+?)\s*$", guide, re.M)
    if not m:
        raise ValueError("SIGNAL.md has no 'Last revision' line")
    raw = m.group(1).lstrip("– ").strip()
    for fmt in ("%d %b %Y", "%d %B %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"cannot parse the revision date {raw!r}")


def sections(guide: str) -> tuple[set[str], set[str]]:
    top = {m.group(1).strip() for m in re.finditer(r"^## (.+)$", guide, re.M)}
    sub = {m.group(1).strip() for m in re.finditer(r"^### (.+)$", guide, re.M)}
    sub |= {m.group(1).strip() for m in re.finditer(r"^\s*[-*]\s+\*\*([^*]+?)\*\*", guide, re.M)}
    return top, sub


def all_rules(pack: dict) -> list[dict]:
    rules = list(pack.get("rules", []))
    for table in pack.get("content_types", {}).values():
        rules += table.get("requirements", [])
    return rules


def check(guide_text: str, pack_text: str) -> list[str]:
    problems = []
    pack = tomllib.loads(pack_text)
    meta = pack.get("guide", {})
    expected = revision_date(guide_text)
    if meta.get("version") != expected:
        problems.append(f"pack version {meta.get('version')!r} differs from the SIGNAL.md revision date {expected!r}")
    if re.search(r"(?im)^\s*author\b|\bauthor\s*=", pack_text):
        problems.append("the pack carries an author line")
    top, sub = sections(guide_text)
    groups = [pack.get("rules", [])] + [t.get("requirements", []) for t in pack.get("content_types", {}).values()]
    for group in groups:
        ids = [r.get("id") for r in group]
        problems += [f"{i}: duplicate rule ID" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for rule in all_rules(pack):
        rid = rule.get("id", "<no id>")
        if rule.get("severity", "warning") not in SEVERITIES:
            problems.append(f"{rid}: unknown severity {rule.get('severity')!r}")
        parts = [p.strip() for p in rule.get("section", "").split(">")]
        if parts[0] not in top:
            problems.append(f"{rid}: cites {parts[0]!r}, which is not a SIGNAL.md section")
        elif len(parts) > 1 and parts[1] not in sub:
            problems.append(f"{rid}: cites {parts[1]!r}, which is not a heading or lead-in in SIGNAL.md")
    return problems


def main() -> int:
    problems = check(GUIDE.read_text(encoding="utf-8"), PACK.read_text(encoding="utf-8"))
    for p in problems:
        print(f"error: {p}")
    if not problems:
        print(f"ok: {PACK.name} matches {GUIDE.name}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
