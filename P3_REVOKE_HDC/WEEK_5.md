# P3 REVOKE-HDC: Week 5 — Board integration with injected bad updates

This week brings the complete controller up on the KV260 #2 board and demonstrates, on hardware, one accepted update, one deliberately bad update, and its exact bit-identical restoration.

Read before you start: `README.md` "### Week 5: Board integration with injected bad updates" and `PROJECT_PLAN.md` "8. Final demonstration script". Record the Friday review in `EVALUATION.md` "Week 5 evaluation".

## Goal

**Goal** (`README.md`): "show complete update, classification change and restoration on hardware." Concretely, this week runs `PROJECT_PLAN.md` Section 8's demonstration script on the KV260 #2 board (the device assigned to P3 REVOKE-HDC in the root `README.md` team table) — baseline checksums, an accepted update, a controlled bad update, a refused out-of-order restoration attempt, and the correct-order restoration that brings the prototype checksum back to exactly its pre-bad-update value. Software already proved exactness in Week 2 and Week 4's regression proved it in RTL simulation; this week's job is proving the same result through the real AXI-Lite register path on real silicon.

## Section 8 script, step by step

Reproduced from `PROJECT_PLAN.md` Section 8.1-8.5 as a literal execution checklist:

| Step | Action | Expected result |
|---:|---|---|
| 1 | Load bitstream; record hash and board serial | manifest entries recorded |
| 2 | Assert `soft_reset`; read `PROTOTYPE_CHECKSUM` for classes 0-3 | `checksum_baseline[0..3]` recorded |
| 3 | Run the frozen test set once | `acc_baseline` recorded |
| 4 | Send the accepted-path packet (`update_id=1001`) | packet framed and admitted |
| 5 | Read `LAST_OUTCOME_CODE`, `UPDATE_COUNTER`, `PROTOTYPE_CHECKSUM[0]` | code `0`; counter `+1`; `checksum_after_good` |
| 6 | Run the frozen test set again | `acc_after_good` recorded |
| 7 | Send the bad-update packet (`update_id=1002`) | packet framed and admitted |
| 8 | Read `LAST_OUTCOME_CODE`, `PROTOTYPE_CHECKSUM[0]` | code `0`; `checksum_after_bad` |
| 9 | Run the frozen test set again | `acc_after_bad` measurably worse than `acc_after_good` |
| 10 | Request restoration of `update_id=1001` | request issued out of order |
| 11 | Read `LAST_OUTCOME_CODE`, `PROTOTYPE_CHECKSUM[0]`, `RESTORE_COUNTER` | code `7`; checksum unchanged; counter unchanged |
| 12 | Request restoration of `update_id=1002` | request issued in order |
| 13 | Read `LAST_OUTCOME_CODE`, `PROTOTYPE_CHECKSUM[0]`, `RESTORE_COUNTER` | code `9`; checksum returns to `checksum_after_good`; counter `+1` |
| 14 | Run the frozen test set again | `acc_after_restore` equals `acc_after_good` |
| 15 | Optionally restore `update_id=1001` | checksum returns to `checksum_baseline[0]`; accuracy returns to `acc_baseline` |

## The full register map this week reads

Reproduced from `PROJECT_PLAN.md` Section 4.6 — every field the demonstration script and the Friday review draw from is one of these fourteen registers:

| Offset | Name | Access | Meaning |
|---|---|---|---|
| `0x00` | `CTRL` | RW | `enable`, `soft_reset`, `class_select` |
| `0x04` | `STATUS` | RO | `busy`, `last_outcome_valid` |
| `0x08` | `LAST_OUTCOME_CODE` | RO | 4-bit code, Section 4.5 |
| `0x0C` | `LAST_UPDATE_ID` | RO | identifier of the most recently processed request |
| `0x10` | `JOURNAL_FREE_BYTES` | RO | current `free_bytes` counter |
| `0x14` | `JOURNAL_HEAD_OFFSET` | RO | ring head pointer |
| `0x18` | `JOURNAL_TAIL_OFFSET` | RO | ring tail pointer |
| `0x1C` | `CLASS_HEAD_SLOT` | RO | head record slot for `CTRL.class_select` |
| `0x20` | `UPDATE_COUNTER` | RO | accepted-update count |
| `0x24` | `RESTORE_COUNTER` | RO | successful-restoration count |
| `0x28` | `REFUSED_COUNTER` | RO | refused/quarantined count |
| `0x2C` | `PROTOTYPE_CHECKSUM` | RO | CRC-32 of `CTRL.class_select`'s packed prototype, latched on read |
| `0x30` | `TRACE_POP` | RO | pops one 8-byte trace record (two 32-bit reads) |
| `0x34` | `TRACE_COUNT` | RO | trace records currently buffered |

Every field is reachable over AXI-Lite without a logic analyser (`PROJECT_PLAN.md` Section 4.7); a Vivado ILA on `wr_en_out`, `state` and `record_durable` is a bring-up aid only, not part of the frozen interface.

## Section 8 evidence files

Reproduced from `PROJECT_PLAN.md` Section 8.6, the evidence set this week's demonstration must produce:

| File | Location | Content |
|---|---|---|
| Board manifest | `manifests/week5_board_manifest.json` | bitstream hash, board serial, build/commit ID, clock configuration |
| Checksum table | `results/raw/checksums.csv` | `checksum_baseline`, `checksum_after_good`, `checksum_after_bad`, restored checksums, for all 4 classes |
| Classification table | `results/raw/classification.csv` | `acc_baseline`, `acc_after_good`, `acc_after_bad`, `acc_after_restore` |
| Annotated trace | `results/processed/update_restore_trace.csv` | `TRACE_POP` dump covering steps 4-15, one row per Section 4.4 trace record |
| Register read log | `results/raw/register_log.csv` | timestamped read of every register above at each numbered step |
| Mismatch summary | `results/processed/mismatch_summary.md` | states the 0-mismatch result required by the Week 5 checkpoint, or the failing case if not yet met |

## What must exist by Friday

1. The board manifest, checksum table, classification table, annotated trace, register read log and mismatch summary from the table above, each in its named location.
2. Baseline checksums: `checksum_baseline[0..3]` read from `PROTOTYPE_CHECKSUM` for all 4 classes after `soft_reset` (`PROJECT_PLAN.md` Section 8.1).
3. The accepted-path run (Section 8.2): update packet `source_id=1`, `update_id=1001`, `class_id=0`, `hA=hB=2`, `mA=180`, `mB=165`, `F=52`, confirmed by `LAST_OUTCOME_CODE=0` and `PROTOTYPE_CHECKSUM[0]` changing to `checksum_after_good`.
4. The controlled-bad-update run (Section 8.3): update packet `source_id=2`, `update_id=1002`, `class_id=0`, `hA=hB=2`, `mA=140`, `mB=150`, `F=60`, confirmed accepted with `PROTOTYPE_CHECKSUM[0]` changing to `checksum_after_bad`, and `acc_after_bad` measurably worse than `acc_after_good`.
5. The refused out-of-order restoration attempt (Section 8.4): requesting restoration of `update_id=1001` before `1002`, confirmed as `LAST_OUTCOME_CODE=7` (`refused_ordering`) with `PROTOTYPE_CHECKSUM[0]` unchanged and `RESTORE_COUNTER` not incrementing.
6. The correct-order restoration (Section 8.5): restoring `update_id=1002`, confirmed as `LAST_OUTCOME_CODE=9` (`restored`), `PROTOTYPE_CHECKSUM[0]` returning to exactly `checksum_after_good`, and `acc_after_restore` equal to `acc_after_good`.
7. At least 1,000 deterministic update/restoration operations replayed on hardware, with the mismatch summary recorded.

## Day by day

| Day | What this means for Week 5 |
|---|---|
| Monday | Freeze the week's question — "does the board reproduce the exact pre-update checksum after restoration?" — name the hardware owner as lead (`PROJECT_PLAN.md` Section 7, W5), pass condition: `checksum_baseline` recovered exactly after the bad-update-then-restore sequence. |
| Tuesday | Bring up the bitstream on the KV260 #2, and verify `soft_reset` and the baseline checksum/accuracy read path alone (Section 8.1) before sending any update packet. |
| Wednesday | Integrate the accepted-path and bad-update steps (Section 8.2-8.3); retain the first mismatch between the expected and observed `LAST_OUTCOME_CODE` or checksum before it is fixed. |
| Thursday | Run the frozen Section 8.4-8.5 refused-then-restore sequence and the 1,000-operation replay; prepare the register read log and annotated trace as evidence. |
| Friday | 12-minute evaluation against `EVALUATION.md` "Week 5 evaluation": restored prototype Hamming error (target 0 bits), the manifest and the hardware/software match. |

## Acceptance criteria

- [ ] The restored prototype checksum equals the exact pre-update checksum (`EVALUATION.md` Week 5 evaluation, "target 0" Hamming error; `PROJECT_PLAN.md` Section 7, W5).
- [ ] The packet path is observable end to end through the full register map above during the run (`PROJECT_PLAN.md` Section 7, W5).
- [ ] The Section 8 demonstration script's accepted-path step alone produces `LAST_OUTCOME_CODE=0` and the expected checksum change (`PROJECT_PLAN.md` Section 7, W5 smallest test).
- [ ] The refused out-of-order restoration attempt produces `LAST_OUTCOME_CODE=7` with `PROTOTYPE_CHECKSUM[0]` unchanged and `RESTORE_COUNTER` not incrementing (`PROJECT_PLAN.md` Section 8.4).
- [ ] At least 1,000 deterministic update/restoration operations are replayed with all build and board identifiers recorded (`README.md` Week 5 required evidence; `PROJECT_PLAN.md` Section 7, W5).
- [ ] `acc_after_restore` equals `acc_after_good` exactly (`PROJECT_PLAN.md` Section 8.5, step 14).
- [ ] All six evidence files in the table above exist at their named locations before Friday's review.

## Evidence to retain

From this week, `board_serial` is required on every recorded row (`METRICS_GUIDE.md` "Required identifiers"). Record `run_id`, `date_utc`, `team=P3`, `project=REVOKE_HDC`, `device=kv260`, `board_serial`, `source_commit`, `dirty_tree` and `bitstream_sha` in `manifests/week5_board_manifest.json`, and the six evidence files named above. Use `inst_queue_depth` for journal bytes or records used and `inst_coalesced` for affected dimensions, per the P3 row in `METRICS_GUIDE.md`. A refused run (the Section 8.4 out-of-order attempt) is retained with its own row and raw trace, not overwritten by the successful restoration that follows it (root README "Keep failed runs").

## Friday review

- [ ] Numeric result recorded: restored prototype Hamming error in bits, target 0 (`EVALUATION.md` Week 5 evaluation).
- [ ] Main run ID(s) recorded for the accepted-path, bad-update, refused and restoration steps.
- [ ] Source commit/build ID recorded, matching `bitstream_sha` in the board manifest.
- [ ] Reference match stated (y/n/bounded) against the Week 4 simulation result.
- [ ] What did not work this week recorded, including any register read that needed a retry or a timing margin issue.
- [ ] Cross-check performed by someone who did not run the board demonstration, confirmed and named.
- [ ] Team verdict (Green/Amber/Red) recorded against the README Week 5 checkpoint language.
- [ ] Next smallest test and owner agreed: reproduce the `F=96 -> 208`-byte point from the Week 6 swept data (`PROJECT_PLAN.md` Section 7, W6 smallest test).

## Where this usually goes wrong

- Only software restoring state while hardware reloads a complete saved prototype instead of walking the journal — the README's own Week 5 Red checkpoint, and precisely the shortcut this project exists to avoid.
- Exact bits restoring but outcome or record metadata staying incomplete (a missing `UPDATE_COUNTER`/`RESTORE_COUNTER` increment, or a trace gap) — the README's own Week 5 Amber checkpoint.
- Treating the bad update's syntactic acceptance as a bug: `mA=140`, `mB=150` both clear `theta_A=theta_B=128`, so `LAST_OUTCOME_CODE=0` on step 8 is correct — admission checks agreement and margins, not semantic correctness, and the whole point of Section 8.3 is that a bad update can still be syntactically valid.
- Forgetting that `board_serial` and `bitstream_sha` are now required on every row (`METRICS_GUIDE.md`), and discovering the gap only when assembling the Week 8 evidence index.

## Hand-off into Week 6

Week 6 reuses this week's KV260 #2 board bring-up and bitstream, and the exact same accepted/bad/restore packet fields, as one of the four comparison arms (Arm D) in the campaign; the checksum-based exactness proof from this week becomes the "exact restoration" metric Week 6 measures identically across Arms A, C and D. The 1,000-operation replay's flip-density data also seeds the `F` sweep Week 6 extends to the full break-even curve.
