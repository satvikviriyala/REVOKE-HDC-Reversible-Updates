# P3 REVOKE-HDC: Week 6 — Four-arm memory and recovery campaign

This week runs the frozen four-arm comparison — full signed counts, packed-binary-only, full-snapshot and the sparse-journal design — under one shared workload and measurement boundary, and states the exact `F` range where the sparse journal beats a full snapshot.

Read before you start: `README.md` "### Week 6: Four-arm memory and recovery campaign" and `PROJECT_PLAN.md` "6. Comparison arms A-D: metrics, boundary, and success/negative results". Record the Friday review in `EVALUATION.md` "Week 6 evaluation".

## Goal

**Goal** (`README.md`): "map memory, latency and recovery quality over realistic flip densities." Concretely, this week is the one point in the schedule where all four arms run side by side under identical conditions, so every later claim about the sparse journal's advantage is backed by a real sweep rather than the single worked `F=96` example. The team must state, with the plotted break-even curve as evidence, the precise `F` range where Arm D's `16 + 2F`-byte record beats Arm C's fixed 512-byte snapshot while still restoring exactly.

## The four arms and the fairness rule

Per `README.md` "Required comparison arms" and `PROJECT_PLAN.md` Section 6, the four arms are:

| Arm | Stored model/update state | Behaviour |
|---|---|---|
| A | Full signed counts | Update and subtract using complete numeric state; the counter-based exact reference the other three arms are checked against, not a memory-competitive design in its own right. |
| B | Packed binary prototype only | No restoration support; establishes the accuracy floor with no recovery mechanism at all. |
| C | Full packed-prototype snapshot per accepted update | Exact but memory-heavy restoration, fixed at `512` bytes/class/update. |
| D | Packed prototype plus sparse residue record | The proposed compact exact core: `16 + 2F` bytes/update, restoring the packed bit, never the hidden signed count. |

The root README's fairness rule applies without exception: "All four arms in a project must use the same workload, clock, arithmetic rules and measurement boundary." Concretely, per `PROJECT_PLAN.md` Section 6.2, all four arms replay the same encoded sample stream, the same update order, the same source labels and the same restoration requests under the same random seed; cycle counts start when the request signal first asserts and end when `outcome_code` is posted, with host-side packet construction and software accuracy scoring timed separately, outside that boundary. A result is only entered on the Week 6 four-arm table if it was produced inside this boundary with the frozen seed.

## Metrics collected identically across all four arms

Reproduced from `PROJECT_PLAN.md` Section 6.1:

| Metric | How it is measured |
|---|---|
| Exact restoration | Word-for-word compare of the full `D`-bit prototype after restoration against a saved pre-update reference (Arms A, C, D) |
| Bytes per update | A: fixed at `D * counter_width` (all dimensions, always); B: `0`; C: fixed `512` bytes; D: `16 + 2F` bytes, variable with `F` |
| Journal/record capacity | Total BRAM bytes committed to the recovery mechanism, plus measured occupancy over time for Arms C and D |
| Update/restoration cycles | Clock cycles from the request asserting (`pkt_valid`/`restore_req`) to `outcome_code` being posted |
| Refused updates | Count and outcome-code breakdown per 1,000 requests |
| Flip density | Distribution of `F` (mean, p95, maximum) over the frozen workload |
| Classification accuracy | Measured before the bad update commits, immediately after it commits, and after its restoration completes |

## Bytes-per-update reference: Arm C against Arm D

Pure arithmetic from the frozen formulas (`PROJECT_PLAN.md` Section 4.2, Section 6), so the sweep result can be checked against a known curve before it is trusted:

| `F` | Arm C bytes (fixed) | Arm D bytes (`16+2F`) | Arm D smaller? |
|---:|---:|---:|---|
| 0 | 512 | 16 | yes |
| 50 | 512 | 116 | yes |
| 96 | 512 | 208 | yes (frozen maximum `F`) |
| 150 | 512 | 316 | yes |
| 200 | 512 | 416 | yes |
| 247 | 512 | 510 | yes (last byte below break-even) |
| 248 | 512 | 512 | no — equal, not strictly smaller |
| 300 | 512 | 616 | no — Arm D now costs more |

## Accuracy measurement points, per arm

The same four points from `PROJECT_PLAN.md` Section 8, applied identically to every arm capable of restoration:

| Point | When measured | Expected relation |
|---|---|---|
| `acc_baseline` | before any update in the run | reference starting point |
| `acc_after_good` | immediately after the legitimate update commits | at or above `acc_baseline` |
| `acc_after_bad` | immediately after the injected bad update commits | measurably below `acc_after_good` |
| `acc_after_restore` | after the bad update's restoration completes | equal to `acc_after_good` for Arms A, C and D; Arm B has no restore step |

## What must exist by Friday

1. Frozen encoded samples, update order and bad-source schedule in `configs/`, shared by all four arms.
2. Arm A (full signed counts) and Arm B (packed-binary-only, no restoration) implementations in `sim/`, run under the Section 6.2 boundary.
3. A results table in `results/processed/` covering every metric in the metrics table above, collected identically for all four arms.
4. Sweep scripts in `scripts/` and raw data in `results/raw/` covering dimension, flip count, journal size and update rate, recording `F` as mean, p95 and maximum at each sweep point.
5. The bytes-per-update-versus-`F` plot in `results/figures/` (Fig.6, `PROJECT_PLAN.md` Section 9), with the 512-byte snapshot line and the `F=248` break-even point marked, matching the reference table above.
6. Classification accuracy at the four measurement points above, recorded per arm.
7. A refused-updates and journal-occupancy-over-time report in `results/processed/`.
8. All four arms' `run_id`s tagged with `arm` in the Friday metrics CSV, per `METRICS_GUIDE.md` submission rule 3 ("from Week 6, every final comparison row needs an arm").

## Day by day

| Day | What this means for Week 6 |
|---|---|
| Monday | Freeze the week's question — "over what `F` range does Arm D beat Arm C while staying exact?" — name the verification owner as lead (`PROJECT_PLAN.md` Section 7, W6), pass condition: a stated `F` range backed by the plotted curve. |
| Tuesday | Build and verify Arm A and Arm B in isolation under the Section 6.2 boundary — same encoded stream, same seed — reusing Arm D's KV260 #2 board/bitstream from Week 5 and treating Arm C's snapshot mechanism as a plain copy-back. |
| Wednesday | Integrate all four arms into one sweep harness; retain the first case where two arms disagree on classification accuracy at the same measurement point, since under the fairness rule they must not. |
| Thursday | Run the frozen sweep across dimension, flip count, journal size and update rate; prepare the four-arm table, flip-density plot, memory break-even curve, latency plot and recovery table as evidence (`README.md` Week 6 required evidence). |
| Friday | 12-minute evaluation against `EVALUATION.md` "Week 6 evaluation": p95 affected dimensions, the four-arm table and the break-even curve. |

## Acceptance criteria

- [ ] The team states the precise `F` range where Arm D beats Arm C's fixed 512-byte cost while keeping exact restoration, backed by the plotted curve (`PROJECT_PLAN.md` Section 7, W6; Section 6, Arm D success criterion).
- [ ] Every record-size statistic is reported as mean, p95 and maximum, not mean alone (`PROJECT_PLAN.md` Section 7, W6).
- [ ] The `F=96 -> 208`-byte point is reproduced from the swept data (`PROJECT_PLAN.md` Section 7, W6 smallest test; Section 4.2).
- [ ] All four arms are run under the identical Section 6.2 boundary — same stream, order, labels, requests and seed (`PROJECT_PLAN.md` Section 6.2; root README "Compare one mechanism at a time").
- [ ] Arm D shows bit-exact restoration at strictly less memory than Arm C for every observed `F < 248` (`PROJECT_PLAN.md` Section 6, Arm D success criterion).
- [ ] Every metric in the "Metrics collected" table above is present in the four-arm results table, not only exact restoration and bytes per update.
- [ ] Numeric result for `EVALUATION.md` "Week 6 evaluation" — p95 affected dimensions — is recorded from the sweep.

## Evidence to retain

Every Friday metrics row from this week carries `arm` (A, B, C or D), per `METRICS_GUIDE.md` submission rule 3, alongside `run_id`, `date_utc`, `device=kv260`, `board_serial`, `source_commit`, `bitstream_sha` (for arms exercised on the KV260 #2 board) and `golden_match`. Record `metric_name`/`metric_value` for bytes/update, cycles, refused-update count and flip density separately per arm in `results/raw/`, with `inst_refusals` (quarantined/refused updates), `inst_queue_depth` (journal bytes or records used) and `inst_coalesced` (affected dimensions) populated per the P3 row in `METRICS_GUIDE.md`. Regenerate the break-even plot (Fig.6) from this retained raw data, never from manually edited values (`METRICS_GUIDE.md` submission rule 5). Any arm's refused or failed sweep point is kept as its own row, not dropped from the plot.

## Friday review

- [ ] Numeric result recorded: p95 affected dimensions, from the sweep (`EVALUATION.md` Week 6 evaluation).
- [ ] Main run ID(s) recorded for all four arms across the full sweep.
- [ ] Source commit/build ID recorded for the sweep harness and each arm's implementation.
- [ ] Reference match stated (y/n/bounded) for Arms C and D's exact-restoration results.
- [ ] What did not work this week recorded, including any sweep point that produced a refusal or a boundary violation.
- [ ] Cross-check performed by someone who did not build the sweep harness, confirmed and named.
- [ ] Team verdict (Green/Amber/Red) recorded against the README Week 6 checkpoint language.
- [ ] Next smallest test and owner agreed: fill the journal to exactly its capacity and confirm one further request returns `refused_capacity` with `free_bytes` unchanged (`PROJECT_PLAN.md` Section 7, W7 smallest test).

## Where this usually goes wrong

- Reporting only mean record size while the maximum silently overflows the journal — the README's own Week 6 Red checkpoint.
- Letting workload generation drift between arms (different seed, different sample order) so the four-arm comparison no longer isolates the journal mechanism — a direct violation of "compare one mechanism at a time," and the README's own Week 6 Amber checkpoint if it is not yet reproducible.
- Comparing Arm D's cycle count against Arm C's without confirming both used the same start/end cycle definition from Section 6.2, which silently favours whichever arm's boundary is looser.
- Presenting the break-even point as a fixed number instead of the derived range: `F < 248` is the formula's answer, but the measured mean/p95/maximum `F` for the real workload is what Week 6 must actually report against it.
- Skipping the `arm` column on Friday metrics rows, which `METRICS_GUIDE.md` requires starting this exact week.

## Hand-off into Week 7

Week 7 takes the same journal design proven in this week's Arm D runs and subjects it to adversarial pressure — full/wrap/retire cycles, corruption and resets — rather than the cooperative sweep this week used. The measured `F` distribution and the confirmed journal capacity sizing from this week's sweep become the fill/wrap targets Week 7's endurance suite drives the journal to exactly.
