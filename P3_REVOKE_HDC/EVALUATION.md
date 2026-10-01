# P3 REVOKE-HDC: Eight-Week Evaluation Workbook

Project brief: `README.md` | Shared metrics guide: `../METRICS_GUIDE.md` | Friday CSV: `../friday_metrics.csv`

This workbook belongs to P3 only. Complete one table after each weekly review. Week 0 reading and setup are prerequisites, so the eight evaluated weeks are Weeks 1 through 8.

Do not erase a failed result. Record its run ID, explain what happened and state the smallest next test.

## Eight-week overview

| Week | Core goal | Student verdict | Faculty verdict |
|---:|---|---|---|
| 1 | Freeze update alphabet, residue, record and restoration-order contract. | Green | ____ |
| 2 | Prove exact restoration for the supported software core. | Green | ____ |
| 3 | Complete packed prototype and journal memories. | ____ | ____ |
| 4 | Integrate admission, commit and supported-order restoration. | ____ | ____ |
| 5 | Demonstrate hardware update, classification effect and exact restoration. | ____ | ____ |
| 6 | Complete the four-arm memory and recovery campaign. | ____ | ____ |
| 7 | Pass journal wrap, ordering, corruption, reset and endurance tests. | ____ | ____ |
| 8 | Freeze the encoder, packet flow, hardware and handover. | ____ | ____ |

---

## Week 1 evaluation

| Field | Entry |
|---|---|
| Week goal | Freeze update alphabet, residue, record and restoration-order contract. |
| Evidence that must be shown | Dimension/word layout; residue/contribution range; packet validation; header/entry/checksum; agreement thresholds; ring allocation; record-size table; at least 30 vectors. |
| Numeric result | Maximum supported record: 208 bytes |
| Main run ID(s) | P3_20261001_1000_w1-freeze |
| Source commit/build ID | 36bce1840989c67e864618c0cf96179b9a903e48 |
| Reference match | y / n / bounded: y |
| What did not work this week? | Conceptual contribution +8 in \|u\|<=8 specification was discovered to be unencodable in signed 4-bit two's complement (-8..+7). An explicit refusal check and retained failure vector V037 were added rather than silently truncating or wrapping. |
| Student comments, interesting discovery or possible new course of action | Proved that padding to ring end on wrap uses less than 0.08% of BRAM capacity while eliminating split-record handling logic. Sizing confirms sparse journaling saves 81.3% memory at F=40 (96B vs 512B) and remains beneficial for all F < 248. |
| Why is that new course worth testing? | Avoids complex multi-cycle split-record recombination across BRAM physical boundaries in RTL and prevents race conditions during ring wrap. |
| Cross-check performed by | A. Sharma (must not be the artefact author) |
| Team verdict | Green / Amber / Red: Green |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: Run one hand-built 2-entry packet and restore it in the software reference model
- Owner: Reference Owner
- Expected completion date: 2026-10-08

---

## Week 2 evaluation

| Field | Entry |
|---|---|
| Week goal | Prove exact restoration for the supported software core. |
| Evidence that must be shown | At least 1,000 generated updates; bit-identical pre/restore comparison; stale/corrupt/duplicate/full cases; flip-count mean, p95 and maximum; snapshot break-even frequency. |
| Numeric result | Restoration mismatches: 0 (target 0) |
| Main run ID(s) | P3_20261001_1100_w2-exact-core |
| Source commit/build ID | 36bce1840989c67e864618c0cf96179b9a903e48 |
| Reference match | y / n / bounded: y |
| What did not work this week? | Generator sequence desynchronized from the index table when packets were intentionally refused in negative tests. Fixed by synchronizing packet sequence from engine index table so admission sequence ordering remains strict. |
| Student comments, interesting discovery or possible new course of action | Over 1,000 continuous updates, flip density distribution measured mean F = 40.62, median F = 40, p95 F = 65, max F = 91. 100.0% of updates were below F=248 break-even. Word write-mask combining safely coalesced multiple flips in the same 64-bit word into a single operation with zero bit collision issues. |
| Why is that new course worth testing? | Validates that masked word writes eliminate BRAM read-modify-write hazards in software, paving the way for simple single-cycle RAM writes in Week 3 RTL. |
| Cross-check performed by | R. Patel (must not be the artefact author) |
| Team verdict | Green / Amber / Red: Green |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: Commit one accepted update whose entries all map to a single 64-bit word and confirm it matches the software model
- Owner: Hardware Owner
- Expected completion date: 2026-10-15

---

## Week 3 evaluation

| Field | Entry |
|---|---|
| Week goal | Complete packed prototype and journal memories. |
| Evidence that must be shown | Hamming-result comparison; packed-word read-modify-write traces; record allocation/head/tail audit; commit-requires-valid-record assertions; timing/resource report. |
| Numeric result | Packed inference mismatches: ____ / ____ |
| Main run ID(s) | ______________________________________________________________ |
| Source commit/build ID | ______________________________________________________________ |
| Reference match | y / n / bounded: __________ |
| What did not work this week? | ______________________________________________________________ |
| Student comments, interesting discovery or possible new course of action | ______________________________________________________________ |
| Why is that new course worth testing? | ______________________________________________________________ |
| Cross-check performed by | ____________________ (must not be the artefact author) |
| Team verdict | Green / Amber / Red: __________ |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: ____________________________________________________________
- Owner: ____________________
- Expected completion date: ____________________

---

## Week 4 evaluation

| Field | Entry |
|---|---|
| Week goal | Integrate admission, commit and supported-order restoration. |
| Evidence that must be shown | Accepted/quarantined/refused/restored traces; per-class order enforcement; repeated/stale handling; exactly-once bit changes; journal-full behaviour. |
| Numeric result | Unrecorded bit changes: ____ (target 0) |
| Main run ID(s) | ______________________________________________________________ |
| Source commit/build ID | ______________________________________________________________ |
| Reference match | y / n / bounded: __________ |
| What did not work this week? | ______________________________________________________________ |
| Student comments, interesting discovery or possible new course of action | ______________________________________________________________ |
| Why is that new course worth testing? | ______________________________________________________________ |
| Cross-check performed by | ____________________ (must not be the artefact author) |
| Team verdict | Green / Amber / Red: __________ |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: ____________________________________________________________
- Owner: ____________________
- Expected completion date: ____________________

---

## Week 5 evaluation

| Field | Entry |
|---|---|
| Week goal | Demonstrate hardware update, classification effect and exact restoration. |
| Evidence that must be shown | Manifest; initial/updated/restored checksums; 1,000 deterministic operations; controlled bad update; journal metadata; hardware/software match. |
| Numeric result | Restored prototype Hamming error: ____ bits (target 0) |
| Main run ID(s) | ______________________________________________________________ |
| Source commit/build ID | ______________________________________________________________ |
| Reference match | y / n / bounded: __________ |
| What did not work this week? | ______________________________________________________________ |
| Student comments, interesting discovery or possible new course of action | ______________________________________________________________ |
| Why is that new course worth testing? | ______________________________________________________________ |
| Cross-check performed by | ____________________ (must not be the artefact author) |
| Team verdict | Green / Amber / Red: __________ |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: ____________________________________________________________
- Owner: ____________________
- Expected completion date: ____________________

---

## Week 6 evaluation

| Field | Entry |
|---|---|
| Week goal | Complete the four-arm memory and recovery campaign. |
| Evidence that must be shown | Identical encoded streams for Arms A to D; bytes/update, capacity and latency; flip-density distribution; snapshot break-even; accuracy and prototype distance before/after/restore. |
| Numeric result | p95 affected dimensions: ____ |
| Main run ID(s) | ______________________________________________________________ |
| Source commit/build ID | ______________________________________________________________ |
| Reference match | y / n / bounded: __________ |
| What did not work this week? | ______________________________________________________________ |
| Student comments, interesting discovery or possible new course of action | ______________________________________________________________ |
| Why is that new course worth testing? | ______________________________________________________________ |
| Cross-check performed by | ____________________ (must not be the artefact author) |
| Team verdict | Green / Amber / Red: __________ |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: ____________________________________________________________
- Owner: ____________________
- Expected completion date: ____________________

---

## Week 7 evaluation

| Field | Entry |
|---|---|
| Week goal | Pass journal wrap, ordering, corruption, reset and endurance tests. |
| Evidence that must be shown | Full/wrap/retire cycles; duplicate/stale/corrupt/out-of-order requests; reset and stalls; mixed-class long run; live-record audit; cross-team reproduction. |
| Numeric result | Active-record overwrite events: ____ (target 0) |
| Main run ID(s) | ______________________________________________________________ |
| Source commit/build ID | ______________________________________________________________ |
| Reference match | y / n / bounded: __________ |
| What did not work this week? | ______________________________________________________________ |
| Student comments, interesting discovery or possible new course of action | ______________________________________________________________ |
| Why is that new course worth testing? | ______________________________________________________________ |
| Cross-check performed by | ____________________ (must not be the artefact author) |
| Team verdict | Green / Amber / Red: __________ |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: ____________________________________________________________
- Owner: ____________________
- Expected completion date: ____________________

---

## Week 8 evaluation

| Field | Entry |
|---|---|
| Week goal | Freeze the encoder, packet flow, hardware and handover. |
| Evidence that must be shown | Tagged source; dataset split, seed and checksum; supported order and limits; one-command flows; annotated trace; evidence index; external exact restoration. |
| Numeric result | External restoration error: ____ bits |
| Main run ID(s) | ______________________________________________________________ |
| Source commit/build ID | ______________________________________________________________ |
| Reference match | y / n / bounded: __________ |
| What did not work this week? | ______________________________________________________________ |
| Student comments, interesting discovery or possible new course of action | ______________________________________________________________ |
| Why is that new course worth testing? | ______________________________________________________________ |
| Cross-check performed by | ____________________ (must not be the artefact author) |
| Team verdict | Green / Amber / Red: __________ |
| Faculty verdict | Green / Amber / Red: __________ |
| Faculty initials and date | Initials: __________ Date: __________ |

### Next-week action agreed at the review

- Smallest next test: ____________________________________________________________
- Owner: ____________________
- Expected completion date: ____________________

---

## Week 8 close-out

- [ ] Every run ID written above exists.
- [ ] Final figures regenerate from retained raw data.
- [ ] The main accepted path and one refusal/failure path are reproducible.
- [ ] Limits and unsupported conditions are stated in the project README.
- [ ] A student outside the team has completed the documented smoke test.
- [ ] Student discoveries that changed the design are linked to their confirming experiments.
