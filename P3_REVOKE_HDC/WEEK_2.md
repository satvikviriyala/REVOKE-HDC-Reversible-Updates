# P3 REVOKE-HDC: Week 2 — Prove exact restoration in software

This week builds the software reference model that must restore every admitted packed-prototype update bit-for-bit before any hardware is built against it.

Read before you start: `README.md` "### Week 2: Prove exact restoration in software" and `PROJECT_PLAN.md` "5. Correctness invariants as testable assertions". Record the Friday review in `EVALUATION.md` "Week 2 evaluation".

## Goal

**Goal** (`README.md`): "establish the exact core before building packed hardware." Concretely, this week's software model is not a prototype of the RTL, it is the reference the RTL must match starting Week 3. It generates candidate transition packets from the Week 0/1 encoder, applies the admission rule frozen in Week 1, commits and reverses packed-bit updates in reverse commit order, and proves the restored prototype is bit-identical to a saved pre-update copy — not merely close in Hamming distance or classification accuracy. Restoration recovers each bit as `sign_threshold(residue)`; the software model must never read back a hidden signed count it does not actually keep.

## Worked example: the Week 2 smallest test

The `PROJECT_PLAN.md` Section 7 smallest test for this week is "one hand-built 2-entry packet updates then restores correctly in the software model." Worked by hand, using `sign_threshold(c) = 1 if c>=0 else 0`:

| Entry | `dimension_index` | `residue` | `contribution` | `old_bit` | `new_residue` | `new_bit` |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 100 | -3 | +5 | 0 | 2 | 1 |
| 2 | 200 | 2 | -5 | 1 | -3 | 0 |

This packet's record is `F=2`, so `16 + 2*2 = 20` bytes. Restoring it walks the same two entries and recomputes each old bit directly from the stored `residue` — `sign_threshold(-3)=0` for dimension 100, `sign_threshold(2)=1` for dimension 200 — writing both back without ever having stored or needing the original signed count.

## Negative-test outcome mapping

Each injected negative case must resolve to exactly one outcome code from `PROJECT_PLAN.md` Section 4.5; use this mapping to check the software model's refusal logic:

| Injected case | Expected outcome | Code |
|---|---|---|
| Stale `old_bit` (packet's expected bit no longer matches stored prototype bit) | `refused_stale` | 5 |
| Corrupt residue or contribution exceeding `\|u\|_max<=8` | `refused_residue` | 4 |
| Duplicate dimension index within one packet | `refused_duplicate` | 6 |
| Journal has insufficient free bytes for the packet (`Jreq > Jfree`) | `refused_capacity` | 2 |
| Corrupt or mismatched checksum | `refused_checksum` | 3 |
| Restoration of an already-retired record | `already_retired` | 10 |

## Record-size reference

`16 + F*2` bytes, from `PROJECT_PLAN.md` Section 4.2, worked out for the range the flip-density measurement below must cover; use this to sanity-check the measured distribution before trusting it:

| `F` | Record bytes | Smaller than the 512-byte snapshot? |
|---:|---:|---|
| 0 | 16 | yes |
| 10 | 36 | yes |
| 25 | 66 | yes |
| 40 | 96 | yes |
| 52 | 120 | yes (Week 5 accepted-path `F`) |
| 60 | 136 | yes (Week 5 bad-update `F`) |
| 96 | 208 | yes (frozen maximum `F`) |
| 150 | 316 | yes |
| 200 | 416 | yes |
| 247 | 510 | yes (last byte below break-even) |
| 248 | 512 | no (equal to the snapshot, not strictly smaller) |

## Invariants this week's software model must already satisfy

Even though the state names in `PROJECT_PLAN.md` Section 3.3 are RTL-specific, the underlying property is a software requirement first — these are the rows the software model is checked against before any RTL exists:

| # | Invariant |
|---:|---|
| 4 | Each record's state visits `active -> restoring -> retired` exactly once and never revisits `active` or skips `restoring`. |
| 5 | A repeated restoration request against a `retired` slot returns `already_retired` and flips no bit. |
| 6 | Restoration writes back only when every listed dimension's current bit equals the record's expected post-update bit. |
| 7 | A refused or quarantined request changes neither the prototype word nor the journal `free_bytes` counter. |
| 9 | An accepted update followed immediately by its own restoration reproduces the pre-update prototype word for word. |
| 10 | No dimension is written twice within a single commit or a single restoration. |
| 11 | A restoration request locates a record only when class ID, update ID and stored source ID all match; any mismatch is `refused_ordering`, never a silent no-op. |
| 12 | Every request produces exactly one outcome-log entry and increments exactly one counter. |

## What must exist by Friday

1. A packet generator in `sim/` producing valid candidate transition packets from the frozen encoder and dataset, using the Week 1 header/entry fields.
2. An admission implementation in `sim/` applying `admit = (hA=hB) AND (mA>=theta_A) AND (mB>=theta_B) AND (Jreq<=Jfree) AND packet_valid` from `README.md` "Update admission".
3. A commit-and-reverse implementation in `sim/` that writes packed-bit updates and reverses them in the Week 1 reverse-commit-order rule, recovering each restored bit as `sign_threshold(residue)` rather than any stored signed count.
4. A zero-mismatch regression in `tests/` comparing the restored prototype word-for-word against a saved pre-update reference, over at least 1,000 admitted updates.
5. Negative-test vectors in `tests/` for every row of the outcome mapping above, each checked against its correct refusal outcome code.
6. A flip-density measurement in `results/raw/` reporting mean, p95 and maximum `F` over the same 1,000+ updates, plus the sparse/snapshot break-even frequency computed from the measured distribution against the reference table above.
7. A reproducible command in `scripts/`, recorded in the project `README.md`'s command list, that regenerates this week's log from a fixed seed.

## Day by day

| Day | What this means for Week 2 |
|---|---|
| Monday | Freeze the week's question — "does the software core restore every admitted update exactly?" — name the reference owner as lead (`PROJECT_PLAN.md` Section 7, W2), pass condition: zero mismatches across at least 1,000 admitted restorations. |
| Tuesday | Build and verify the packet generator and admission check in isolation against the Week 1 hand vectors, confirming the software model agrees with all 30+ hand-checked cases before generating new ones. |
| Wednesday | Integrate commit and reverse-order restoration; retain the first mismatch or refusal that comes out wrong, and update the Week 1 decision log if it exposes an ambiguity (for example, an unhandled ring-wrap case). |
| Thursday | Run the frozen 1,000-update checkpoint plus the negative-test mapping table above; prepare the zero-mismatch log and flip-density distribution as evidence. |
| Friday | 12-minute evaluation against `EVALUATION.md` "Week 2 evaluation": restoration mismatch count (target 0), negative-test outcomes and the flip-density distribution. |

## Acceptance criteria

- [ ] Zero mismatches across at least 1,000 admitted software restorations (`PROJECT_PLAN.md` Section 7, W2; `EVALUATION.md` Week 2 evaluation, target 0).
- [ ] Every injected negative case in the mapping table above returns the correct outcome code and changes no simulated prototype bit (`PROJECT_PLAN.md` Section 7, W2).
- [ ] The measured `F` distribution is reported as mean, p95 and maximum, not mean alone (`README.md` "Sparse record sizing"; `PROJECT_PLAN.md` Section 7, W2).
- [ ] One hand-built 2-entry packet updates then restores correctly in the software model (`PROJECT_PLAN.md` Section 7, W2 smallest test).
- [ ] All eight invariants listed above hold with zero violations across the 1,000+-update regression (`PROJECT_PLAN.md` Section 5).
- [ ] A bounded approximate-restoration experiment, if attempted, is reported separately from the exact-core results, never mixed into the same table (`README.md` Week 2 exploration space; "Frozen configuration for this cohort," out-of-scope list).

## Evidence to retain

Open a `manifests/` entry per retained run recording `run_id`, `date_utc`, `team=P3`, `project=REVOKE_HDC`, `source_commit` and `dirty_tree`; `bitstream_sha` and `board_serial` still do not apply since no synthesis has run yet. Record `mode` (admission-rule variant), `task` (dataset/workload name), `status` (`completed`/`refused`/`failed`) and `metric_name`/`metric_value` for the mismatch count and the flip-density statistics in `results/raw/`. Per `METRICS_GUIDE.md`'s P3-specific column interpretation, use `inst_refusals` for quarantined/refused updates and `inst_coalesced` for affected dimensions when logging instrumentation counters. A refused or failed negative-test case is retained with its own row and raw trace, never silently rerun and overwritten (root README "Keep failed runs").

## Friday review

- [ ] Numeric result recorded: restoration mismatches, target 0 (`EVALUATION.md` Week 2 evaluation).
- [ ] Main run ID(s) recorded for the 1,000+-update regression and the negative-test suite.
- [ ] Source commit/build ID recorded for the software reference implementation.
- [ ] Reference match stated (y/n/bounded) against the saved pre-update prototype.
- [ ] What did not work this week recorded, including any negative-test case that needed a second pass.
- [ ] Cross-check performed by someone who did not build the reference model, confirmed and named.
- [ ] Team verdict (Green/Amber/Red) recorded against the README Week 2 checkpoint language.
- [ ] Next smallest test and owner agreed: commit one accepted update whose entries all map to a single 64-bit word and confirm it matches the software model (`PROJECT_PLAN.md` Section 7, W3 smallest test).

## Where this usually goes wrong

- Judging restoration by recovered classification accuracy while prototype bits still differ — the README's own Week 2 Red checkpoint. Accuracy recovering is not evidence of bit-identical restoration.
- Assuming majority thresholding can be undone with plain XOR of the update vector, which only works when the sign never crossed the threshold — exactly the failure mode `README.md` "Why thresholding loses information" demonstrates.
- Generating packets without documenting the generator's own assumptions (margin distribution, class balance), so a Green restoration result cannot be told apart from a workload that never exercises the hard cases.
- Reporting a bounded approximate mode's Hamming error alongside the exact core's mismatch count in the same table, which the frozen configuration explicitly rules out of scope.
- Treating the negative-test mapping table as six independent one-off checks instead of a regression that must keep passing every week after this one; a later week's refactor can silently reopen a Week 2 case.

## Hand-off into Week 3

Week 3's RTL prototype and journal memories are checked against this week's software reference, case for case — the 1,000-update regression becomes the comparison target for the "match the software reference for at least 10,000 cases" acceptance criterion. The calibrated admission thresholds and the confirmed ring-wrap rule from Week 1, now exercised in software, become the values Week 3 wires into hardware rather than re-deriving them.
