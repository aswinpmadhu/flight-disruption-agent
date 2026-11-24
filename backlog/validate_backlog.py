#!/usr/bin/env python3
"""Read-only validator for backlog/ (standard library only, Python 3.13).

    python backlog/validate_backlog.py [--expect-digest SHA256HEX]

Exit status 0 only if every check passes. It never writes, renames or deletes anything.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent  # backlog/
REPO = ROOT.parent

# Golden rank order: deliberately a second copy of INDEX.md. Changing an ID or a rank
# needs a reviewed edit of both, never one alone.
ORDER = (
    "B-01a", "B-21", "B-12", "B-18", "B-17a", "B-01b", "B-14", "B-22", "B-01c", "B-04",
    "B-06", "B-24", "B-25", "B-03", "B-23", "B-02", "B-08a", "B-26", "B-07", "B-16a",
    "B-36", "B-29a", "B-16b", "B-05", "B-32a", "B-10", "B-09", "B-11a", "B-11b", "B-17b",
    "B-19", "B-20", "B-37", "B-32b", "B-13", "B-15", "B-33", "B-35", "B-03-P2", "B-22-P2",
    "B-25-P2", "B-23-P2", "B-29b", "B-05-P2", "B-32a-P2", "B-09-P2", "B-15-P2", "B-32b-P2",
    "B-33-P2", "B-08b", "B-27", "B-29c", "B-30a", "B-30b", "B-28", "B-31a", "B-31b",
)
PHASE_DIR = {"1": "phase-1", "2": "phase-2", "later": "later"}
PHASE_ORDER = {"1": 1, "2": 2, "later": 3}
PHASE_COUNTS = {"1": 38, "2": 11, "later": 8}
CLASSES = {"CT", "SC", "SA-N", "-"}
# Original slots outside Wave 1 whose body is the original text plus approved replacements.
AMENDED = {"B-03", "B-23", "B-26", "B-16a", "B-05", "B-32a", "B-09", "B-11b",
           "B-32b", "B-15", "B-33", "B-35", "B-29b", "B-08b"}
DK10_SLOTS = {"B-01a", "B-04", "B-01c", "B-24", "B-07", "B-08a", "B-05", "B-05-P2", "B-08b"}
PROVENANCE_COUNTS = {"wave1-assembled": 13, "original-amended": 14,
                     "original-unchanged": 20, "sibling": 10}
FROZEN_TOP = {"AT": 31, "RF": 11, "AS": 12, "RC": 4, "D": 9}
REQUIRED_EVAL = {"EVAL-01", "EVAL-02", "EVAL-03", "EVAL-08", "EVAL-11"}
PLAN_PHASE2 = {"F-BI", "SP-03", "SP-09-S", "SP-13-M"}
PHASE2_SUBSETS = {"search", "offer", "consent"}
REQUIRED_KEYS = ("id", "rank", "phase", "wave", "class", "effort_h", "blocked_by",
                 "blocks", "appends", "tests_owned", "retires", "provenance")

ID_RE = re.compile(r"B-\d{2}[a-c]?(?:-P2)?")
FROZEN_TOKEN = re.compile(
    r"^((?:AT|RF|AS|RC|D|EVAL)-\d\d)([a-z]?(?:-[A-Za-z0-9]+)?)(?:@([a-z0-9]+))?$")
PLAN_TOKEN = re.compile(
    r"^(SP-\d\d(?:-[A-Z])?|S-\d|F-[A-Z]{2}|FR25-[MH]|FI-(?:L|H|T\d)|test_[a-z0-9_]+)"
    r"(?:@([a-z0-9]+))?$")
PLAN_ID_FIND = re.compile(
    r"SP-\d\d(?:-[A-Z])?|S-\d|F-[A-Z]{2}|FR25-[MH]|FI-(?:L|H|T\d)|test_[a-z0-9_]+")


def phase_of(rank: int) -> str:
    return "1" if rank <= 38 else "2" if rank <= 49 else "later"


def wave_of(rank: int) -> int:
    for limit, wave in ((13, 1), (22, 2), (25, 3), (38, 4), (49, 5), (57, 6)):
        if rank <= limit:
            return wave
    return 0


def split_list(value: str) -> list[str]:
    value = value.strip()
    if value.lower() in ("", "none"):
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def dep_ids(cell: str, slot: str, errors: list[str]) -> list[str]:
    cleaned = re.sub(r"\([^)]*\)", "", cell).strip()  # drop notes such as "(housekeeping B-00b merged)"
    if cleaned.lower() == "none":
        return []
    ids = ID_RE.findall(cleaned)
    leftover = ID_RE.sub("", cleaned).replace(",", "").strip()
    if not ids or leftover:
        errors.append(f"INDEX {slot}: cannot parse dependency cell {cell!r}")
    return ids


def is_phase2_base(base: str) -> bool:
    prefix, number = base.split("-")
    n = int(number)
    if prefix == "AT":
        return 9 <= n <= 18 or 26 <= n <= 31
    if prefix == "RF":
        return n in (1, 2, 3, 4, 5, 6, 9, 10)
    if prefix == "AS":
        return n in (4, 5)
    return base in ("D-08", "EVAL-02", "EVAL-03", "EVAL-11")


def expected_provenance(row: dict) -> str:
    if row["id"].endswith("-P2"):
        return "sibling"
    if row["rank"] <= 13:
        return "wave1-assembled"
    return "original-amended" if row["id"] in AMENDED else "original-unchanged"


def parse_index(errors: list[str]) -> list[dict]:
    path = ROOT / "INDEX.md"
    if not path.is_file():
        errors.append("backlog/INDEX.md is missing")
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 9 or not cells[0].isdigit():
            continue
        rank, ident, phase, wave, _cell, cls, hours, blocked_by, blocks = cells
        slot, _, title = ident.partition(" ")
        if not ID_RE.fullmatch(slot):
            errors.append(f"INDEX row {rank}: {slot!r} is not a slot ID")
            continue
        try:
            rows.append({
                "rank": int(rank), "id": slot, "title": title.strip("` "),
                "phase": "later" if phase.lower().startswith("later") else phase,
                "wave": int(wave), "cls": cls, "hours": float(hours),
                "blocked_by": dep_ids(blocked_by, slot, errors),
                "blocks": dep_ids(blocks, slot, errors),
            })
        except ValueError:
            errors.append(f"INDEX {slot}: rank, wave or hours is not a number")
    return rows


def check_index(rows: list[dict], errors: list[str]) -> None:
    ids = [r["id"] for r in rows]
    if len(rows) != len(ORDER):
        errors.append(f"INDEX has {len(rows)} rows; the approved backlog has {len(ORDER)} slots")
    for slot, n in Counter(ids).items():
        if n > 1:
            errors.append(f"INDEX repeats {slot}")
    if tuple(ids) != ORDER:
        errors.append("INDEX slot order differs from the approved rank order")
        for rank, (got, want) in enumerate(zip(ids, ORDER), start=1):
            if got != want:
                errors.append(f"  first difference at rank {rank}: INDEX has {got}, approved order has {want}")
                break
    titles = Counter(r["title"] for r in rows)
    for i, r in enumerate(rows, start=1):
        if r["rank"] != i:
            errors.append(f"INDEX {r['id']}: rank {r['rank']} but it is row {i}")
        if r["phase"] != phase_of(i):
            errors.append(f"INDEX {r['id']}: phase {r['phase']!r}, but rank {i} belongs to phase {phase_of(i)!r}")
        if r["wave"] != wave_of(i):
            errors.append(f"INDEX {r['id']}: wave {r['wave']}, but rank {i} belongs to wave {wave_of(i)}")
        if r["cls"] not in CLASSES:
            errors.append(f"INDEX {r['id']}: unknown class {r['cls']!r}")
        if not r["title"].endswith(f"({r['id']})"):
            errors.append(f"INDEX {r['id']}: title must end with ({r['id']})")
        if titles[r["title"]] > 1:
            errors.append(f"INDEX {r['id']}: title is not unique")
    counts = Counter(r["phase"] for r in rows)
    if dict(counts) != PHASE_COUNTS:
        errors.append(f"phase counts {dict(counts)} differ from the approved {PHASE_COUNTS}")


def check_graph(rows: list[dict], errors: list[str]) -> list[tuple[str, str]]:
    by_id = {r["id"]: r for r in rows}
    forward: set[tuple[str, str]] = set()  # (prerequisite, dependent) from Blocked by
    reverse: set[tuple[str, str]] = set()  # the same pair read from Blocks
    for r in rows:
        for y in r["blocked_by"]:
            if y not in by_id:
                errors.append(f"{r['id']} is blocked by unknown slot {y}")
                continue
            forward.add((y, r["id"]))
            if by_id[y]["rank"] >= r["rank"]:
                errors.append(f"{r['id']} (rank {r['rank']}) is blocked by {y} (rank {by_id[y]['rank']}): "
                              "a prerequisite must have a lower rank")
            if PHASE_ORDER[by_id[y]["phase"]] > PHASE_ORDER[r["phase"]]:
                errors.append(f"{r['id']} (phase {r['phase']}) is blocked by {y} (phase {by_id[y]['phase']}): "
                              "a slot may not depend on a later phase")
        for z in r["blocks"]:
            if z not in by_id:
                errors.append(f"{r['id']} blocks unknown slot {z}")
                continue
            reverse.add((r["id"], z))
    for y, x in sorted(forward - reverse):
        errors.append(f"{x} lists {y} under Blocked by, but {y} does not list {x} under Blocks")
    for y, x in sorted(reverse - forward):
        errors.append(f"{y} lists {x} under Blocks, but {x} does not list {y} under Blocked by")
    return sorted(forward)


def parse_file(path: Path, errors: list[str]) -> tuple[dict | None, str]:
    rel = path.relative_to(REPO)
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{rel}: front matter must start on line 1 with '---'")
        return None, ""
    end = text.find("\n---\n", 4)
    if end == -1:
        errors.append(f"{rel}: front matter is not closed with '---'")
        return None, ""
    fm: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            errors.append(f"{rel}: front matter line without ':' -> {line!r}")
            continue
        fm[key.strip()] = value.strip()
    for key in REQUIRED_KEYS:
        if key not in fm:
            errors.append(f"{rel}: front matter key {key!r} is missing")
    return fm, text[end + 5:]


def collect_files(errors: list[str]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for sub in PHASE_DIR.values():
        folder = ROOT / sub
        if not folder.is_dir():
            errors.append(f"directory backlog/{sub}/ is missing")
            continue
        for path in sorted(folder.iterdir()):
            if path.is_dir() or path.suffix != ".md":
                errors.append(f"unexpected entry {path.relative_to(REPO)}")
            elif path.stem in found:
                errors.append(f"{path.stem} exists twice: {found[path.stem].relative_to(REPO)} "
                              f"and {path.relative_to(REPO)}")
            else:
                found[path.stem] = path
    return found


def check_files(rows: list[dict], errors: list[str]) -> dict[str, dict]:
    found = collect_files(errors)
    wanted = {r["id"] for r in rows}
    for slot in sorted(wanted - set(found)):
        errors.append(f"missing backlog file for {slot}")
    for slot in sorted(set(found) - wanted):
        errors.append(f"unexpected backlog file {found[slot].relative_to(REPO)}")
    data: dict[str, dict] = {}
    for r in rows:
        path = found.get(r["id"])
        if path is None:
            continue
        rel = path.relative_to(REPO)
        if path.parent.name != PHASE_DIR[r["phase"]]:
            errors.append(f"{rel}: phase {r['phase']} files belong in backlog/{PHASE_DIR[r['phase']]}/")
        fm, body = parse_file(path, errors)
        if fm is None:
            continue
        data[r["id"]] = fm
        for key, want in (("id", r["id"]), ("rank", str(r["rank"])), ("phase", r["phase"]),
                          ("wave", str(r["wave"])), ("class", r["cls"])):
            if fm.get(key, "") != want:
                errors.append(f"{rel}: {key} is {fm.get(key)!r}, INDEX.md says {want!r}")
        try:
            effort = float(fm.get("effort_h", ""))
        except ValueError:
            effort = None
        if effort is None or abs(effort - r["hours"]) > 1e-9:
            errors.append(f"{rel}: effort_h is {fm.get('effort_h')!r}, INDEX.md says {r['hours']}")
        for key in ("blocked_by", "blocks"):
            if sorted(split_list(fm.get(key, ""))) != sorted(r[key]):
                errors.append(f"{rel}: {key} differs from INDEX.md")
        first = body.strip().splitlines()[0] if body.strip() else ""
        if first != f"# {r['title']}":
            errors.append(f"{rel}: first body line must be '# {r['title']}'")
    return data


def check_metadata(rows: list[dict], data: dict[str, dict], errors: list[str]) -> None:
    expected_counts: Counter = Counter()
    for r in rows:
        want_prov = expected_provenance(r)
        expected_counts[want_prov] += 1
        fm = data.get(r["id"])
        if fm is None:
            continue
        want = {"FOOT"}
        if r["blocked_by"]:
            want.add("PREP")
        if r["cls"] in ("CT", "SC", "SA-N"):
            want.add("SAFE")
        if r["id"] in DK10_SLOTS:
            want.add("DK10")
        got = set(split_list(fm.get("appends", "")))
        if got != want:
            errors.append(f"{r['id']}: appends is {sorted(got)}, the rules give {sorted(want)}")
        if fm.get("provenance") != want_prov:
            errors.append(f"{r['id']}: provenance is {fm.get('provenance')!r}, expected {want_prov!r}")
    if dict(expected_counts) != PROVENANCE_COUNTS:
        errors.append(f"provenance counts {dict(expected_counts)} differ from the approved {PROVENANCE_COUNTS}")


def check_shared_blocks(errors: list[str], notes: list[str]) -> None:
    path = ROOT / "shared-blocks.md"
    if not path.is_file():
        errors.append("backlog/shared-blocks.md is missing")
        return
    text = path.read_text(encoding="utf-8")
    sections = dict(re.findall(r"^## (FOOT|SAFE|PREP|DK10)[ \t]*$(.*?)(?=^## |\Z)", text, re.S | re.M))
    required = {
        "FOOT": ("Claims open",),
        "SAFE": ("90 minutes",),
        "PREP": ("every Blocked-by",),
        "DK10": ("the only production component that constructs a key", "test_dk10_single_producer"),
    }
    for name, phrases in required.items():
        if name not in sections:
            errors.append(f"shared-blocks.md has no '## {name}' section")
            continue
        for phrase in phrases:
            if phrase not in sections[name]:
                errors.append(f"shared-blocks.md section {name} lacks the required text {phrase!r}")
    if "[cap:" in sections.get("SAFE", ""):
        notes.append("INFO: the SAFE cap clause is still a placeholder (decision D-1 pending): safety issues are not claimable")
    else:
        notes.append("INFO: the SAFE cap clause has no placeholder: confirm that D-1 was decided")


def appendix_a_ids() -> set[str] | None:
    path = REPO / "docs" / "04-implementation-playbook.md"
    if not path.is_file():
        return None
    match = re.search(r"^## Appendix A\b(.*?)^## Appendix B\b", path.read_text(encoding="utf-8"), re.S | re.M)
    if not match:
        return None
    ids: set[str] = set()
    for line in match.group(1).splitlines():
        if line.startswith("|"):
            first_cell = line.strip().strip("|").split("|")[0]
            ids.update(PLAN_ID_FIND.findall(first_cell))
    return ids


def check_tests(rows: list[dict], data: dict[str, dict], errors: list[str], notes: list[str]) -> None:
    phase_of_slot = {r["id"]: r["phase"] for r in rows}
    owner: dict[str, str] = {}
    for r in rows:
        for token in split_list(data.get(r["id"], {}).get("tests_owned", "")):
            if token in owner:
                errors.append(f"test token {token} is owned by both {owner[token]} and {r['id']}")
            else:
                owner[token] = r["id"]
    covered: set[str] = set()
    plan_bases: set[str] = set()
    for token, slot in owner.items():
        match = FROZEN_TOKEN.match(token)
        if match:
            base, _part, subset = match.groups()
            covered.add(base)
            phase2 = is_phase2_base(base)
        else:
            match = PLAN_TOKEN.match(token)
            if not match:
                errors.append(f"{slot}: unrecognised test token {token!r}")
                continue
            base, subset = match.groups()
            plan_bases.add(base)
            phase2 = base in PLAN_PHASE2
        if subset in PHASE2_SUBSETS:
            phase2 = True
        if phase2 and phase_of_slot[slot] == "1":
            errors.append(f"{slot} is a Phase 1 slot but owns the Phase 2 test {token}")
    required = {f"{p}-{n:02d}" for p, top in FROZEN_TOP.items() for n in range(1, top + 1)} | REQUIRED_EVAL
    for base in sorted(required - covered):
        errors.append(f"no slot owns any part of the frozen test {base}")
    for r in rows:
        for token in split_list(data.get(r["id"], {}).get("retires", "")):
            if token not in owner:
                errors.append(f"{r['id']} retires {token}, which no slot owns")
            elif phase_of_slot[owner[token]] != "1" or r["phase"] != "2":
                errors.append(f"{r['id']} retires {token}: only a Phase 2 slot may retire a Phase 1 test")
    appendix = appendix_a_ids()
    if appendix is None:
        notes.append("SKIPPED: docs/04-implementation-playbook.md Appendix A not found; plan-level ID cross-check not run")
    else:
        for base in sorted(plan_bases - appendix):
            errors.append(f"plan-level ID {base} is owned by a slot but is not in playbook Appendix A")
        for base in sorted(appendix - plan_bases):
            errors.append(f"playbook Appendix A lists {base}, but no slot owns it")


def digest(rows: list[dict], edges: list[tuple[str, str]]) -> str:
    lines = [f"{r['rank']}|{r['id']}|{r['phase']}|{r['wave']}|{r['cls']}" for r in rows]
    lines += [f"{a}>{b}" for a, b in edges]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the backlog directory (read-only).")
    parser.add_argument("--expect-digest", help="fail unless the computed edges digest equals this value")
    args = parser.parse_args()
    errors: list[str] = []
    notes: list[str] = []
    rows = parse_index(errors)
    edges: list[tuple[str, str]] = []
    if rows:
        check_index(rows, errors)
        edges = check_graph(rows, errors)
        data = check_files(rows, errors)
        check_metadata(rows, data, errors)
        check_tests(rows, data, errors, notes)
    check_shared_blocks(errors, notes)
    if rows:
        value = digest(rows, edges)
        print(f"edges-digest: {value}")
        if args.expect_digest and args.expect_digest != value:
            errors.append(f"edges digest {value} differs from the expected {args.expect_digest}")
        print(f"{'rank':>4}  {'slot':<10} {'phase':<6} provenance")
        for r in rows:
            print(f"{r['rank']:>4}  {r['id']:<10} {r['phase']:<6} {expected_provenance(r)}")
    for line in notes:
        print(line)
    if errors:
        print(f"FAIL: {len(errors)} problem(s)")
        for message in errors:
            print("  - " + message)
        return 1
    print(f"PASS: {len(rows)} slots, every check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
