# Project status

**Advisory only.** The repository and GitHub are the truth; where this file differs, they win. **Everything below defaults to `unverified` or `not-created`.** Never write `verified` for your own work.

- Last updated: ____ (date) by ____ (GitHub user), based on `main` at commit ____
- `pytest` baseline on a clean checkout of `main` (Python 3.13): ____ passed / ____ failed
- Authority: `docs/01` to `docs/03` (frozen), `backlog/`, `docs/04-implementation-playbook.md`. Decisions: playbook Appendix C (not copied here).

## 1. Environment and housekeeping verification

| Item | State (`unverified` / `verified`) | Evidence (link or output) | Checked by | Date |
|---|---|---|---|---|
| GitHub access for the person updating | unverified | | | |
| Labels exist (`blocked`, `prep-ok`, `safety-critical`, `p1`, `phase-1`, `phase-2`) | **partly: `phase-1`, `safety-critical`, `blocked`, `prep-ok` created and verified; `p1` and `phase-2` not created (not needed for Wave 1)** | `gh label list` | publisher | 2026-11-25 |
| Milestones exist (M2, M3, M3j, freeze) | **partly: `M2 minimum safety` created and verified; the others not created** | `gh api repos/.../milestones` | publisher | 2026-11-25 |
| Pinned Backlog issue exists | **yes: #1, pinned (verified via GraphQL)** | https://github.com/aswinpmadhu/flight-disruption-agent/issues/1 | publisher | 2026-11-25 |
| Branch protection on `main` (PR required; one approval from someone other than the author; stale approvals dismissed; force-push and deletion blocked; bypass list) | unverified | **owner's posted evidence** | owner | |
| B-00a merged (PR approved by a non-author) | not done | PR link | | |
| B-00b merged (dependency lines approved first) | not done / blocked until approved | PR link, install-check output | | |
| B-00c (README) | undecided | PR link or recorded exception | | |
| "Claims open" stated on the pinned issue | **no** | issue #1 says claims are not open yet | | |
| Publication method: manual GitHub web UI by one designated developer | **method approved (the Wave 1 issues #2 to #14 and the pinned issue #1 were published with the GitHub CLI by an authorised session); the designated developer is not recorded** | the developer's own statement on the pinned issue | | |
| Backlog validator (`python backlog/validate_backlog.py`) exits 0 on `main` | **not run** | the exact output and the `edges-digest` line | | |

## 2. Roster and capacity (each developer writes only their own line)

| Developer | GitHub user | Hours (number) | Windows | Safety implementer (y/n) | Safety reviewer (y/n) | Attestation date | Review response time | Python 3.13 env OK | Sign-off willing |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |
| 2 | | | | | | | | | |
| 3 | | | | | | | | | |
| 4 | | | | | | | | | |

Minimum for the Phase 1 safety chain: three implementers and three reviewers. Phase 2 capacity confirmed: no (date, by whom ____).

## 3. Issue ledger (one row per slot; 57 rows)

**States:** `not-created`, `created`, `blocked`, `in-progress`, `awaiting-review`, `merged`, `verified`. **Proposed by** the implementer or claimant (PR editing only this file, with evidence). **`verified` is set only by a different eligible developer** (not an author or co-author of any PR of the slot), who re-ran the slot's tests on a clean checkout of `main`; **for CT, SC and SA-N slots the verifier must meet the Safety Reviewer Roster rules. If no eligible verifier exists the state stays `merged`.**

| Rank | ID | Phase | Issue # | State | Assignee | PR(s) | Merge commit | Tests present and passing on `main` (y/n/not checked) | Safety audit (author / approver / eligible) | Verified by | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | B-01a | 1 | #2 | created | | | | | | | |
| 2 | B-21 | 1 | #3 | created | | | | | | | |
| 3 | B-12 | 1 | #4 | created | | | | | | | |
| 4 | B-18 | 1 | #5 | created | | | | | | | |
| 5 | B-17a | 1 | #6 | blocked | | | | | | | |
| 6 | B-01b | 1 | #7 | blocked | | | | | | | |
| 7 | B-14 | 1 | #8 | blocked | | | | | | | |
| 8 | B-22 | 1 | #9 | blocked | | | | | | | |
| 9 | B-01c | 1 | #10 | blocked | | | | | | | |
| 10 | B-04 | 1 | #11 | blocked | | | | | | | |
| 11 | B-06 | 1 | #12 | blocked | | | | | | | |
| 12 | B-24 | 1 | #13 | blocked | | | | | | | |
| 13 | B-25 | 1 | #14 | blocked | | | | | | | |
| 14 | B-03 | 1 | | not-created | | | | | | | |
| 15 | B-23 | 1 | | not-created | | | | | | | |
| 16 | B-02 | 1 | | not-created | | | | | | | |
| 17 | B-08a | 1 | | not-created | | | | | | | |
| 18 | B-26 | 1 | | not-created | | | | | | | |
| 19 | B-07 | 1 | | not-created | | | | | | | |
| 20 | B-16a | 1 | | not-created | | | | | | | |
| 21 | B-36 | 1 | | not-created | | | | | | | |
| 22 | B-29a | 1 | | not-created | | | | | | | |
| 23 | B-16b | 1 | | not-created | | | | | | | |
| 24 | B-05 | 1 | | not-created | | | | | | | |
| 25 | B-32a | 1 | | not-created | | | | | | | |
| 26 | B-10 | 1 | | not-created | | | | | | | |
| 27 | B-09 | 1 | | not-created | | | | | | | |
| 28 | B-11a | 1 | | not-created | | | | | | | |
| 29 | B-11b | 1 | | not-created | | | | | | | |
| 30 | B-17b | 1 | | not-created | | | | | | | |
| 31 | B-19 | 1 | | not-created | | | | | | | |
| 32 | B-20 | 1 | | not-created | | | | | | | |
| 33 | B-37 | 1 | | not-created | | | | | | | |
| 34 | B-32b | 1 | | not-created | | | | | | | |
| 35 | B-13 | 1 | | not-created | | | | | | | |
| 36 | B-15 | 1 | | not-created | | | | | | | |
| 37 | B-33 | 1 | | not-created | | | | | | | |
| 38 | B-35 | 1 | | not-created | | | | | | | |
| 39 | B-03-P2 | 2 | | not-created | | | | | | | |
| 40 | B-22-P2 | 2 | | not-created | | | | | | | |
| 41 | B-25-P2 | 2 | | not-created | | | | | | | |
| 42 | B-23-P2 | 2 | | not-created | | | | | | | |
| 43 | B-29b | 2 | | not-created | | | | | | | |
| 44 | B-05-P2 | 2 | | not-created | | | | | | | |
| 45 | B-32a-P2 | 2 | | not-created | | | | | | | |
| 46 | B-09-P2 | 2 | | not-created | | | | | | | |
| 47 | B-15-P2 | 2 | | not-created | | | | | | | |
| 48 | B-32b-P2 | 2 | | not-created | | | | | | | |
| 49 | B-33-P2 | 2 | | not-created | | | | | | | |
| 50 | B-08b | Later | | not-created | | | | | | | |
| 51 | B-27 | Later | | not-created | | | | | | | |
| 52 | B-29c | Later | | not-created | | | | | | | |
| 53 | B-30a | Later | | not-created | | | | | | | |
| 54 | B-30b | Later | | not-created | | | | | | | |
| 55 | B-28 | Later | | not-created | | | | | | | |
| 56 | B-31a | Later | | not-created | | | | | | | |
| 57 | B-31b | Later | | not-created | | | | | | | |

## 4. Technical milestones and product gates (kept separate)

| Name | Definition | Parts | State | Evidence (commit, test run, links) |
|---|---|---|---|---|
| M2 | rebooking-approval gate proven | ranks 1 to 13 | not reached | |
| M3 | every frozen safety test passes | Phase 1 part (14 to 22) and Phase 2 part (39 to 43), **both required** | not reached | |
| M3j | deterministic journey through registry and handlers | Phase 1 part (23 to 25) and Phase 2 part (44, 45), **both required** | not reached | |
| PG1 | Phase 1 MVP delivered (playbook §8) | ranks 1 to 38 | not reached | |
| PG2 | Phase 2 MVP delivered (playbook §9) | ranks 1 to 49 | not reached | |

Phase statements (a milestone's single part) may be recorded here as "the Phase 1 part of <milestone>: reached on <commit>"; **never as the milestone itself.**

## 5. Test registers

| Register | Required IDs (see playbook Appendix A) | Last run (date, commit) | Result | Failing or missing IDs |
|---|---|---|---|---|
| Phase 1 | | | | |
| Phase 2 | | | | |

## 6. Scope exceptions and deferrals (requirement IDs, reason, approved by)

| Requirement | Exception | Approved by | Closes when |
|---|---|---|---|
| **FR-07** (and the `accept_search` part of FR-23) | **Documented Phase 1 scope exception (QD-12), not full compliance.** The eight-tool architecture is retained; Phase 1 registers and advertises seven active tools; `accept_search` is dormant; B-21 raises `NotImplementedError` for it. FR-07 must not be recorded as satisfied. | Project owner (decision QD-12) | B-25-P2 merged and eight tools advertised on the evidence commit |

Other rows are added here with their requirement IDs, reason and approver; none is added on anyone's behalf.

## 7. Open blockers and risks

## 8. Takeover and stale-claim log (slot, claimant, time of claim, last push, action, `[takeover]` PR)

## 9. Safety merge audit (every safety PR: author, approver, approver on the reviewer roster, approved after last push)

## 10. Hackathon submission statement (not a gate) and optional tag

The hackathon submission is **not** a product gate. Fill this in only from evidence, using the vocabulary of playbook section 10.1.

- Commit submitted: ____
- Highest product gate passed on that commit: none / PG1 / PG2 (evidence links: ____)
- Milestone **parts** reached: ____ (for example "Phase 1 part of M3j"; never the milestone name alone unless both its parts are merged)
- Statement as published (copy it here): "Submitted commit ____. Highest product gate passed: ____. Reached: ____. Not delivered: ____."
- A partial cancellation journey is described as a partial journey. It is described as "Phase 1 MVP complete" only if PG1 is recorded as passed above.
- Optional tag (nothing depends on it): not created / created at commit ____.

## 11. Next action

Next eligible slot: ____. Evidence: each Blocked-by merged on `main` (list), tests passing on `main` (command, result), within roster role and cap: ____.
