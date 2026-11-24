# Backlog

This directory holds the approved requirements text of every backlog slot (57 slots: 47 original IDs and 10 Phase 2 siblings). It is authoritative for scope, acceptance criteria, tests and dependencies, before and after any GitHub issue is published. GitHub issues carry workflow state only (see `docs/04-implementation-playbook.md`, section 11.6).

* `INDEX.md`: one row per slot: rank, ID and title, phase, wave, cell, class, hours, Blocked by, Blocks. Rank order never changes.
* `shared-blocks.md`: the FOOT, SAFE, PREP and DK10 text appended to issue bodies according to each slot's `appends` list.
* `phase-1/`, `phase-2/`, `later/`: one file per slot, named `<ID>.md`.
* `validate_backlog.py`: a read-only check of this directory. Run it from the repository root:

```bash
python backlog/validate_backlog.py
```

It exits with status 0 only if every check passes. Post its complete output, including the `edges-digest` line, whenever you change this directory. **Never edit a file only to make the validator pass; if it fails, find out which source is wrong.** To confirm nothing changed silently, run it with `--expect-digest <the digest recorded earlier>`.

## Slot file format

```text
---
id: B-23-P2
rank: 42
phase: 2
wave: 5
class: SC
effort_h: 1.0
blocked_by: B-23, B-22-P2, B-03-P2, B-26
blocks: B-32a-P2
appends: FOOT, PREP, SAFE
tests_owned: AS-04, AS-05, AT-09-P, AT-10-P, AT-16, AT-18, AT-31-B, SP-03, SP-13-M, SP-09-S
retires: none
provenance: sibling
---
# [domain] SearchGuard: delay consent and missed-connection plan (B-23-P2)

<body: scope, files, acceptance criteria, tests you own, references>
```

Test tokens are `BASE[-PART][@SUBSET]`. A frozen test ID with parts passes only when every part passes, and every part has exactly one owner. Subsets (`@approval`, `@search`, `@rebooking`, `@offer`, `@consent`) distinguish the three IDs that appear in two slots.

## Changing this directory

A change is a pull request that touches only `backlog/` (never together with the implementation it describes), approved by someone other than its author; a safety slot's file needs a safety reviewer. A change that edits a frozen requirement, weakens a safety test, renumbers a slot or changes the rank order is not made here: it goes to the project owner.
