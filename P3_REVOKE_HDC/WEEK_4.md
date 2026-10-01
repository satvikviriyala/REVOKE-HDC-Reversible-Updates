# P3 REVOKE-HDC: Week 4 — Add admission and restoration engine

This week completes the commit/restore controller so that admission, refusal and exact reverse-order restoration are enforced in hardware, not just in the Week 2 software model.

Read before you start: `README.md` "### Week 4: Add admission and restoration engine" and `PROJECT_PLAN.md` "3.3 Controller states and transition conditions". Record the Friday review in `EVALUATION.md` "Week 4 evaluation".

## Goal

**Goal** (`README.md`): "complete commit, refusal and exact reverse-order restoration." Concretely, this week wires the admission controller (two-modality agreement, margin thresholds, capacity check) and completes the commit/restore controller's full state machine, with every `REFUSE` exit named by outcome code. By Friday, a restoration request that targets anything but the current head of its class's chain must refuse, never overwrite.

## Controller states this engine completes

Reproduced from `PROJECT_PLAN.md` Section 3.3 — every transition this week's state machine must implement:

| From | To | Condition |
|---|---|---|
| `IDLE` | `PARSE` | `pkt_valid` asserted |
| `PARSE` | `ADMIT_CHECK` | packet fully framed, length and checksum pass, no duplicate dimension index |
| `PARSE` | `REFUSE` | checksum/length fails (`refused_checksum`), or a dimension index repeats (`refused_duplicate`) |
| `ADMIT_CHECK` | `JOURNAL_WRITE` | `hA=hB`, `mA>=theta_A`, `mB>=theta_B`, `j_req<=j_free`, and every entry's recomputed `old_bit` matches the stored prototype bit |
| `ADMIT_CHECK` | `REFUSE` | agreement/margin fails or `j_req>j_free` (`refused_capacity`); alphabet exceeded (`refused_residue`); or `old_bit` mismatch (`refused_stale`) |
| `JOURNAL_WRITE` | `COMMIT` | record fully written and checksummed, index-table slot marked `active`; `wr_en_out` held low throughout |
| `COMMIT` | `IDLE` | every entry's `new_bit` written into the prototype word; outcome posted as `accepted` |
| `IDLE` | `RESTORE_LOOKUP` | `restore_req` asserted |
| `RESTORE_LOOKUP` | `RESTORE_ORDER_CHECK` | a record matching class ID and update ID is found and its state is not `retired` |
| `RESTORE_LOOKUP` | `REFUSE` | no matching record (`refused_ordering`), or already `retired` (`already_retired`, no bit change) |
| `RESTORE_ORDER_CHECK` | `RESTORE_BITCHECK` | the requested record is the current head of its class's chain |
| `RESTORE_ORDER_CHECK` | `REFUSE` | a newer record exists for the same class (`refused_ordering`) |
| `RESTORE_BITCHECK` | `RESTORE_APPLY` | every entry's stored bit equals the record's expected post-update bit; slot state moves `active -> restoring` |
| `RESTORE_BITCHECK` | `REFUSE` | any entry's stored bit differs from expected (`refused_bit_state`) |
| `RESTORE_APPLY` | `RETIRE` | every listed dimension's prior bit, recomputed as `sign_threshold(residue)`, is written back exactly once |
| `RETIRE` | `IDLE` | slot state moves `restoring -> retired`; class head pointer moves to `prev_slot`; outcome posted as `restored` |

## Every correctness invariant this controller must hold

Reproduced from `PROJECT_PLAN.md` Section 5 in full — this is the week that first makes all twelve checkable in hardware, even though some were previewed in software in Week 2:

| # | Invariant |
|---:|---|
| 1 | The prototype write-enable never asserts before a request reaches `COMMIT` or `RESTORE_APPLY`. |
| 2 | A journal record becomes valid strictly before the first prototype write of the same request. |
| 3 | Restoration proceeds only against the current head-of-chain record for that class (reverse commit order). |
| 4 | Each record's state visits `active -> restoring -> retired` exactly once and never revisits `active` or skips `restoring`. |
| 5 | A repeated restoration request against a `retired` slot returns `already_retired` and flips no bit. |
| 6 | Restoration writes back only when every listed dimension's current bit equals the record's expected post-update bit. |
| 7 | A refused or quarantined request changes neither the prototype word nor the journal `free_bytes` counter. |
| 8 | No byte range belonging to a live record is overwritten by a later `JOURNAL_WRITE`. |
| 9 | An accepted update followed immediately by its own restoration reproduces the pre-update prototype word for word. |
| 10 | No dimension is written twice within a single commit or a single restoration. |
| 11 | A restoration request locates a record only when class ID, update ID and stored source ID all match; any mismatch is `refused_ordering`. |
| 12 | Every request produces exactly one outcome-log entry and increments exactly one counter. |

## Registers this controller drives

From `PROJECT_PLAN.md` Section 4.6 — the control/status registers this week's state machine is the sole author of:

| Offset | Name | Meaning |
|---|---|---|
| `0x00` | `CTRL` | `enable`, `soft_reset`, `class_select` |
| `0x04` | `STATUS` | `busy`, `last_outcome_valid` |
| `0x08` | `LAST_OUTCOME_CODE` | 4-bit code, Section 4.5 |
| `0x0C` | `LAST_UPDATE_ID` | identifier of the most recently processed request |
| `0x1C` | `CLASS_HEAD_SLOT` | head record slot for `CTRL.class_select` |
| `0x20` | `UPDATE_COUNTER` | accepted-update count |
| `0x24` | `RESTORE_COUNTER` | successful-restoration count |
| `0x28` | `REFUSED_COUNTER` | refused/quarantined count |

## What must exist by Friday

1. The admission controller in `src/`, implementing `admit = (hA=hB) AND (mA>=theta_A) AND (mB>=theta_B) AND (Jreq<=Jfree) AND packet_valid`, with capacity reserved before a packet is accepted.
2. The full commit/restore controller state machine in `src/`, covering every row in the states table above.
3. ID-based record lookup in `src/`, locating a record by source ID, update ID and class ID together, refusing with `refused_ordering` on any mismatch rather than a silent no-op.
4. Reverse-order enforcement per class in `src/`: a restoration request is compared against `class_head_slot[class_id]` and refused if it does not match (Invariant 3).
5. The `active -> restoring -> retired` state transition in `src/` for every record slot, restoring each listed dimension's prior bit — recomputed as `sign_threshold(residue)`, not read from any stored signed count — exactly once, before retirement.
6. Repeat, stale and out-of-order outcome handling in `src/`, returning `already_retired` (code 10) on a repeat request rather than flipping a bit a second time (Invariant 5).
7. The eight registers listed above, driven from the controller and readable over AXI-Lite.
8. A zero-mismatch regression and capacity-state trace in `tests/` and `results/raw/`, covering directed and randomised sequences across all 4 classes, checking all twelve invariants.

## Day by day

| Day | What this means for Week 4 |
|---|---|
| Monday | Freeze the week's question — "does restoration ever change a bit under invalid ordering?" — name the verification owner as lead (`PROJECT_PLAN.md` Section 7, W4), pass condition: zero invariant violations under directed and randomised regression. |
| Tuesday | Build and verify the admission controller alone (agreement, margin and capacity checks) against the Week 1 calibrated thresholds and the Week 2 software admission logic. |
| Wednesday | Integrate the full commit/restore state machine across all 4 classes; retain the first case where a restoration request targets a non-head record and confirm it produces `refused_ordering` rather than a wrong restore. |
| Thursday | Run the frozen directed-plus-randomised regression checking all twelve invariants; prepare the update/quarantine/refusal/restoration waveforms and the capacity-state trace as evidence. |
| Friday | 12-minute evaluation against `EVALUATION.md` "Week 4 evaluation": unrecorded bit changes (target 0), per-class order enforcement and the capacity-state trace. |

## Acceptance criteria

- [ ] Accepted updates reverse exactly and no invalid-ordering request changes a bit (`PROJECT_PLAN.md` Section 7, W4; `README.md` Week 4 Green checkpoint).
- [ ] Invariants 3, 5 and 6 hold with zero violations under directed and randomised regression (`PROJECT_PLAN.md` Section 5 and Section 7, W4).
- [ ] A capacity-state trace is recorded for all 4 classes, not only the class under direct test (`PROJECT_PLAN.md` Section 7, W4).
- [ ] Every row in the controller-states table above is exercised at least once by a directed test, including every `REFUSE` exit.
- [ ] `UPDATE_COUNTER`, `RESTORE_COUNTER` and `REFUSED_COUNTER` each increment by exactly one per matching request, matching Invariant 12.
- [ ] Issuing a restoration request one commit out of order returns `refused_ordering` (outcome code 7) with the prototype unchanged (`PROJECT_PLAN.md` Section 7, W4 smallest test; Section 4.5).
- [ ] A repeated restoration request against a retired slot returns `already_retired` (outcome code 10) and flips no bit (`PROJECT_PLAN.md` Section 5, Invariant 5).
- [ ] Numeric result for `EVALUATION.md` "Week 4 evaluation" — unrecorded bit changes — is `0`.

## Evidence to retain

Continue one `manifests/` entry per retained regression run, with `run_id`, `date_utc`, `source_commit`, `dirty_tree` and `bitstream_sha` for the synthesised controller; `board_serial` still does not apply before Week 5. Record `status` (`completed`/`refused`) and `failure_reason` for every negative-test row — per `METRICS_GUIDE.md` submission rule 1, refused and failed runs still receive rows, never a silent rerun. Use `inst_refusals` for the quarantined/refused-update count per the P3 row in `METRICS_GUIDE.md`, broken down by outcome code in `results/processed/`. Keep the waveform or trace for any out-of-order or repeat-restoration case that first produced the wrong outcome code, alongside the corrected version.

## Friday review

- [ ] Numeric result recorded: unrecorded bit changes, target 0 (`EVALUATION.md` Week 4 evaluation).
- [ ] Main run ID(s) recorded for the directed and randomised regressions across all 4 classes.
- [ ] Source commit/build ID recorded, matching the manifest `bitstream_sha`.
- [ ] Reference match stated (y/n/bounded) against the Week 2 software model's admission and restoration decisions.
- [ ] What did not work this week recorded, including any class whose journal handling lagged the others.
- [ ] Cross-check performed by someone who did not write the controller, confirmed and named.
- [ ] Team verdict (Green/Amber/Red) recorded against the README Week 4 checkpoint language.
- [ ] Next smallest test and owner agreed: run the Section 8 demonstration script's accepted-path step alone and confirm `LAST_OUTCOME_CODE=0` and the expected checksum change (`PROJECT_PLAN.md` Section 7, W5 smallest test).

## Where this usually goes wrong

- Restoration overwriting bits even when the current prototype state does not match the record's expected post-update state — the README's own Week 4 Red checkpoint, and exactly what Invariant 6 and `refused_bit_state` exist to catch.
- Getting one class fully correct and leaving concurrent per-class journals incomplete — the README's own Week 4 Amber checkpoint; the regression must exercise all 4 classes, not just class 0.
- Restoring through a newer overlapping update: if a dimension was touched by a later commit, the older record's restoration must refuse, not partially apply.
- Treating `already_retired` as an error path instead of a defined, correct outcome — a second restoration request against the same record is expected traffic under Week 7's endurance testing, not a bug.
- Wiring `RESTORE_ORDER_CHECK` against a stale copy of `class_head_slot` instead of the live pointer, which lets a race between a new commit and an in-flight restoration slip past Invariant 3 undetected.

## Hand-off into Week 5

Week 5 takes this week's complete admission-through-restoration controller and runs it on the KV260 #2 board for the first time, using exactly the accepted-path and refused-path sequences this week's regression already exercises in simulation — `source_id`, `update_id`, `hA`/`hB`, `mA`/`mB` and `F` values from `PROJECT_PLAN.md` Section 8.2-8.4. The capacity-state trace and per-class order enforcement proven here become what Week 5's register-map reads must reproduce on hardware.
