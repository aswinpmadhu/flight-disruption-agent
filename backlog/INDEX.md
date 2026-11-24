# Backlog index (57 slots)

Authoritative for dependencies and metadata. Each slot's requirements are in its file under `backlog/phase-1/`, `backlog/phase-2/` or `backlog/later/`; shared text is in `backlog/shared-blocks.md`. **This table is machine-parsed by `backlog/validate_backlog.py`: keep exactly nine columns and one row per slot, with the rank in the first column.** **Do not restate requirements elsewhere.** Rank order never changes; prerequisites always have lower ranks; no Phase 1 slot is blocked by a Phase 2 slot. Every issue is created **unassigned**, priority P0 except the eight Later slots (P1, label `p1`).

**Labels at creation:** `phase-1` or `phase-2`; `safety-critical` for class CT, SC and SA-N; `blocked` for every slot with a Blocked-by; `p1` for Later; `prep-ok` only where the provider has posted an interface (for the Wave 1 slots B-17a, B-01b, B-14, B-01c, B-04 the interface is in the text, so they carry it at creation). **Milestones:** "M2 minimum safety", "M3 complete safety scope", "M3j deterministic journey (stretch)"; Wave 4 and later slots carry the milestone named in their cell, or none (Later). **Classes:** CT contract, SC safety-critical, SA-N claimable by anyone with a named non-author safety reviewer, `-` none. Efforts are planning estimates; a claimant replaces them at the claim comment.

| Rank | ID and title | Phase | Wave | Cell | Class | h | Blocked by | Blocks |
|---|---|---|---|---|---|---|---|---|
| 1 | B-01a `[domain] Shared models and enums (B-01a)` | 1 | 1 | M2 | CT | 1.0 | none | B-17a, B-01b, B-04, B-06, B-03, B-02, B-27 |
| 2 | B-21 `[approval] Reply filter: approval path (B-21)` | 1 | 1 | M2 | SC | 1.25 | none | B-22, B-22-P2 |
| 3 | B-12 `[agent] LLM client interface, ScriptedLLM and AdversarialLLM (B-12)` | 1 | 1 | M2 | - | 1.5 | none | B-25, B-26, B-19, B-32b, B-13, B-31a |
| 4 | B-18 `[session] TraceRecorder (B-18)` | 1 | 1 | M2 | - | 0.75 | none | B-17a, B-14, B-29a, B-19 |
| 5 | B-17a `[session] Session models (B-17a)` | 1 | 1 | M2 | - | 0.75 | B-01a, B-18 | B-22, B-25, B-23, B-16a, B-16b, B-29a, B-17b |
| 6 | B-01b `[domain] Error codes, result envelope and result types (B-01b)` | 1 | 1 | M2 | CT | 1.0 | B-01a | B-14, B-01c, B-29a |
| 7 | B-14 `[agent] Tool input models, registry, trace recording, hooks (B-14)` | 1 | 1 | M2 | SC | 2.75 | B-01b, B-18 | B-25, B-26, B-16a, B-16b, B-19, B-37, B-15, B-25-P2 |
| 8 | B-22 `[approval] Approval store and manager (B-22)` | 1 | 1 | M2 | SC | 1.5 | B-17a, B-21 | B-24, B-25, B-26, B-37, B-22-P2 |
| 9 | B-01c `[services] Service Protocols (B-01c)` | 1 | 1 | M2 | CT | 0.75 | B-01b | B-24, B-08a, B-26, B-07, B-16b, B-11b |
| 10 | B-04 `[services] Fixture schema, loader and validator (B-04)` | 1 | 1 | M2 | - | 1.1 | B-01a | B-06, B-05, B-05-P2 |
| 11 | B-06 `[services] MockWorld (B-06)` | 1 | 1 | M2 | - | 1.25 | B-01a, B-04 | B-24, B-08a, B-07, B-29a, B-37, B-30a |
| 12 | B-24 `[services] RebookingService (B-24)` | 1 | 1 | M2 | SC | 1.75 | B-06, B-22, B-01c | B-25, B-37 |
| 13 | B-25 `[agent] Approval-flow handlers, card and hooks (B-25)` | 1 | 1 | M2 | SC | 1.7 | B-12, B-14, B-17a, B-22, B-24 | B-32a, B-37, B-25-P2 |
| 14 | B-03 `[domain] Disruption classifier: cancellation (B-03)` | 1 | 2 | M3 (P1) | - | 0.25 | B-01a | B-23, B-16a, B-03-P2 |
| 15 | B-23 `[domain] SearchPlanner and SearchGuard: cancellation (B-23)` | 1 | 2 | M3 (P1) | SC | 1.0 | B-03, B-17a | B-26, B-16a, B-23-P2 |
| 16 | B-02 `[domain] Itinerary ranker (B-02)` | 1 | 2 | M3 (P1) | - | 0.6 | B-01a | B-08a, B-29a |
| 17 | B-08a `[services] Alternative search, single segment (B-08a)` | 1 | 2 | M3 (P1) | - | 1.25 | B-06, B-02, B-01c | B-26, B-37, B-08b |
| 18 | B-26 `[agent] search_alternatives handler (B-26)` | 1 | 2 | M3 (P1) | SA-N | 1.25 | B-08a, B-12, B-14, B-23, B-01c, B-22 | B-32a, B-37, B-23-P2 |
| 19 | B-07 `[services] Booking and flight-status services (B-07)` | 1 | 2 | M3 (P1) | - | 0.75 | B-06, B-01c | B-16a, B-37 |
| 20 | B-16a `[agent] get_booking and get_flight_status handlers (B-16a)` | 1 | 2 | M3 (P1) | - | 0.75 | B-03, B-07, B-14, B-17a, B-23 | B-32a, B-37, B-03-P2 |
| 21 | B-36 `[config] Settings schema: model, retrieval thresholds, refund phrases (B-36)` | 1 | 2 | M3 (P1) | - | 0.75 | none | B-29a, B-11b, B-13, B-33, B-37 |
| 22 | B-29a `[eval] Common checks D-01 to D-07, D-09 (B-29a)` | 1 | 2 | M3 (P1) | - | 1.5 | B-01b, B-02, B-06, B-17a, B-18, B-36 | B-32a, B-29b, B-29c, B-30b |
| 23 | B-16b `[agent] search_policy handler (B-16b)` | 1 | 3 | M3j (P1) | - | 0.5 | B-01c, B-14, B-17a | B-32a, B-37 |
| 24 | B-05 `[services] Author fixture data for EVAL-01 (B-05)` | 1 | 3 | M3j (P1) | - | 0.75 | B-04 | B-32a, B-05-P2, B-28 |
| 25 | B-32a `[eval] Deterministic cancellation journey at registry level (B-32a)` | 1 | 3 | M3j (P1) | - | 1.75 | B-05, B-16a, B-16b, B-25, B-26, B-29a | B-32b, B-32a-P2 |
| 26 | B-10 `[rag] Policy loader and chunker (B-10)` | 1 | 4 | M4 | - | 1.25 | none | B-11a |
| 27 | B-09 `[rag] Author the synthetic policy corpus: cancellation (B-09)` | 1 | 4 | M4 | - | 1.25 | none | B-11b, B-09-P2, B-28 |
| 28 | B-11a `[rag] BM25 ranking (B-11a)` | 1 | 4 | M4 | - | 0.75 | B-10 (housekeeping B-00b merged) | B-11b |
| 29 | B-11b `[rag] Relevance threshold, PolicyRetriever implementation, no-relevant-policy signal (B-11b)` | 1 | 4 | M4 | - | 1.0 | B-11a, B-09, B-01c, B-36 | B-37, B-09-P2 |
| 30 | B-17b `[session] SessionManager (B-17b)` | 1 | 4 | M5 | - | 1.25 | B-17a | B-19, B-20, B-37 |
| 31 | B-19 `[agent] AgentRunner loop (B-19)` | 1 | 4 | M5 | - | 2.75 | B-12, B-14, B-17b, B-18 | B-20, B-37, B-32b, B-30a |
| 32 | B-20 `[api] /v1/chat and error classes (B-20)` | 1 | 4 | M5 | - | 1.5 | B-17b, B-19 | B-37, B-32b |
| 33 | B-37 `[app] Composition root, wiring and fault-injection tests (B-37)` | 1 | 4 | M5 | - | 1.25 | B-06, B-07, B-08a, B-11b, B-14, B-16a, B-16b, B-17b, B-19, B-20, B-22, B-24, B-25, B-26, B-36 | B-32b, B-13, B-33, B-32b-P2 |
| 34 | B-32b `[eval] Cancellation journey through the API and recorded scripted run (B-32b)` | 1 | 4 | M5e | - | 1.25 | B-32a, B-12, B-19, B-20, B-37 | B-33, B-32b-P2 |
| 35 | B-13 `[agent] ClaudeClient adapter (B-13)` | 1 | 4 | M6 | - | 1.25 | B-12, B-36, B-37 (housekeeping B-00b merged) | B-33, B-31b |
| 36 | B-15 `[agent] System prompt: cancellation workflow (B-15)` | 1 | 4 | M6 | - | 0.8 | B-14 | B-33, B-15-P2 |
| 37 | B-33 `[eval] Live Claude run: cancellation (B-33)` | 1 | 4 | M7 | - | 0.75 | B-13, B-15, B-32b, B-36, B-37 | B-35, B-31b, B-33-P2 |
| 38 | B-35 `[eval] Freeze and submission checklist (B-35)` | 1 | 4 | M8 | - | 1.0 | B-33 | none |
| 39 | B-03-P2 `[domain] Disruption classifier and connection rule: delay and missed connection (B-03-P2)` | 2 | 5 | M3 (P2) | - | 0.75 | B-03, B-16a | B-23-P2, B-32a-P2 |
| 40 | B-22-P2 `[approval] Search consent: filter kind rules, consent record and manager (B-22-P2)` | 2 | 5 | M3 (P2) | SC | 1.25 | B-22, B-21 | B-25-P2, B-23-P2, B-29b, B-32a-P2 |
| 41 | B-25-P2 `[agent] Search offer handler and SEARCH_OFFER card (B-25-P2)` | 2 | 5 | M3 (P2) | SC | 0.8 | B-22-P2, B-25, B-14 | B-32a-P2, B-15-P2 |
| 42 | B-23-P2 `[domain] SearchGuard: delay consent and missed-connection plan (B-23-P2)` | 2 | 5 | M3 (P2) | SC | 1.0 | B-23, B-22-P2, B-03-P2, B-26 | B-32a-P2 |
| 43 | B-29b `[eval] Delay checks D-08a to D-08f (B-29b)` | 2 | 5 | M3 (P2) | - | 0.75 | B-22-P2, B-29a | B-32a-P2, B-30a |
| 44 | B-05-P2 `[services] Author fixture data for EVAL-02, EVAL-03, EVAL-11 and MCT validation (B-05-P2)` | 2 | 5 | M3j (P2) | - | 1.3 | B-05, B-04 | B-32a-P2 |
| 45 | B-32a-P2 `[eval] Deterministic delay and missed-connection journeys at registry level (B-32a-P2)` | 2 | 5 | M3j (P2) | - | 1.5 | B-32a, B-05-P2, B-03-P2, B-22-P2, B-25-P2, B-23-P2, B-29b | B-32b-P2 |
| 46 | B-09-P2 `[rag] Author the delay and missed-connection policy documents (B-09-P2)` | 2 | 5 | M4 (P2) | - | 0.75 | B-09, B-11b | B-32b-P2 |
| 47 | B-15-P2 `[agent] System prompt: delay and missed-connection workflow (B-15-P2)` | 2 | 5 | M6 (P2) | - | 0.3 | B-15, B-25-P2 | B-33-P2 |
| 48 | B-32b-P2 `[eval] Delay and missed-connection scenarios through the API (B-32b-P2)` | 2 | 5 | M5e (P2) | - | 0.5 | B-32b, B-32a-P2, B-09-P2, B-37 | B-33-P2 |
| 49 | B-33-P2 `[eval] Live Claude run: delay and missed connection (B-33-P2)` | 2 | 5 | M7 (P2) | - | 0.75 | B-33, B-32b-P2, B-15-P2 | none |
| 50 | B-08b `[services] Alternative search, connecting itineraries (B-08b)` | Later (classification open, QD-6) | 6 | none | - | 1.25 | B-08a | none |
| 51 | B-27 `[eval] Scenario schema and loader (B-27)` | Later | 6 | none | - | 0.75 | B-01a | B-29c, B-30a, B-30b, B-28, B-31a |
| 52 | B-29c `[eval] Scenario-specific checks (B-29c)` | Later | 6 | none | - | 0.75 | B-29a, B-27 | B-30a |
| 53 | B-30a `[eval] Harness (Tier 1 runner) (B-30a)` | Later | 6 | none | - | 1.25 | B-19, B-27, B-29c, B-06, B-29b | none |
| 54 | B-30b `[eval] Report writer (B-30b)` | Later | 6 | none | - | 0.75 | B-27, B-29a | B-31b |
| 55 | B-28 `[eval] Author EVAL-01 to EVAL-11 scenario files (B-28)` | Later | 6 | none | - | 1.5 | B-27, B-05, B-09 | none |
| 56 | B-31a `[eval] LLM judge: rubric, prompt, score parsing and storage (B-31a)` | Later | 6 | none | - | 1.5 | B-12, B-27 | B-31b |
| 57 | B-31b `[eval] LLM judge live wiring (B-31b)` | Later | 6 | none | - | 1.0 | B-13, B-30b, B-31a, B-33 | none |

**Totals:** Phase 1 (ranks 1 to 38) 44.2 h; Phase 2 (39 to 49) 9.65 h; Later 8.75 h. **Cells:** M2 = ranks 1 to 13; M3 Phase 1 part = 14 to 22, Phase 2 part = 39 to 43; M3j Phase 1 part = 23 to 25, Phase 2 part = 44 and 45. A milestone is reached only when both its parts are merged; a part may be reported only as "the Phase 1 part of <milestone>".
