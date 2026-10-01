# P3 REVOKE-HDC: Week 7 — Endurance, ordering and corruption stress

This week drives the journal to its capacity limits and its ring wrap point, and confirms that duplicate, stale, corrupt and out-of-order requests, plus resets mid-operation, never silently change a prototype bit.

Read before you start: `README.md` "### Week 7: Endurance, ordering and corruption stress" and `PROJECT_PLAN.md` "5. Correctness invariants as testable assertions". Record the Friday review in `EVALUATION.md` "Week 7 evaluation".

## Goal

**Goal** (`README.md`): "verify that record pressure and repeated requests never silently damage prototypes." Concretely, every mechanism proved correct under cooperative conditions in Weeks 2-6, on the same KV260 #2 board/bitstream configuration, is now driven past its comfort zone — the journal is filled, wrapped and retired repeatedly, malformed and out-of-order requests are issued deliberately, and the system is reset mid-write, mid-commit and mid-restoration. Every one of these cases must end in an explicit, named outcome; Invariant 8 (no live record is ever overwritten by ring wrap) is the invariant this week exists to stress hardest.

## Registers this suite reads continuously

Reproduced from `PROJECT_PLAN.md` Section 4.6 — the endurance suite's fault matrix and live-record audit depend on every one of these fourteen registers staying consistent under pressure, not only the pair Week 5 exercised:

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
| `0x2C` | `PROTOTYPE_CHECKSUM` | RO | CRC-32 of the selected class's packed prototype |
| `0x30` | `TRACE_POP` | RO | pops one 8-byte trace record |
| `0x34` | `TRACE_COUNT` | RO | trace records currently buffered |

## What a reset must never leave behind

| Reset point | What must not have happened | Invariant protecting it |
|---|---|---|
| During record write (`JOURNAL_WRITE`) | The index-table slot is marked `active` before the record is fully checksummed | Invariant 2 |
| During prototype commit (`COMMIT`) | Any entry's `new_bit` is applied without the rest of the same request's entries | Invariant 1 |
| During restoration (`RESTORE_APPLY`) | Any dimension is left between its old and new bit, or the slot is left between `restoring` and `retired` | Invariant 4, 6 |

## Outcome codes this suite exercises

Every stress case must resolve to a code from `PROJECT_PLAN.md` Section 4.5; this week is the first time all eleven are driven deliberately, not just the accepted/restored pair from Week 5:

| Case injected | Expected code | Invariant checked |
|---|---:|---|
| Journal filled to exact capacity, one further request | `refused_capacity` (2) | 7 |
| Corrupt or mismatched checksum | `refused_checksum` (3) | — (parser gate) |
| Contribution exceeds `\|u\|_max<=8`, or stale residue | `refused_residue` (4) | — (parser gate) |
| Stale `old_bit` against current stored bit | `refused_stale` (5) | — (ADMIT_CHECK gate) |
| Duplicate dimension index within one packet | `refused_duplicate` (6) | 10 |
| Restoration request out of reverse-commit order | `refused_ordering` (7) | 3 |
| Restoration where current bits do not match expected post-update state | `refused_bit_state` (8) | 6 |
| Repeat restoration of a `retired` record | `already_retired` (10) | 5 |
| Reset injected mid-write, mid-commit or mid-restoration | deterministic post-reset state, no partial commit | 1, 2 |
| Ring wrap while a record is still `active`/`restoring` | allocator refuses rather than overwrites | 8 |

## Every correctness invariant this suite re-verifies

Reproduced in full from `PROJECT_PLAN.md` Section 5 — the endurance suite is the one point in the schedule where every invariant is exercised together, under adversarial rather than cooperative input:

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

## What must exist by Friday

1. A journal fill/wrap/retire endurance run, driven from `scripts/` and logged in `results/raw/`, cycling the ring buffer repeatedly until wrap behaviour has been exercised many times over.
2. Test vectors in `tests/` for every row of the outcome-code table above, each checked against its correct code and invariant.
3. Reset-injection tests in `tests/` covering three points: during record write, during prototype commit and during restoration, with the post-reset state confirmed deterministic.
4. Interface-stall tests in `tests/` for the prototype and outcome interfaces.
5. A long mixed-class update stream run in `results/raw/`, exercising all 4 classes' journals concurrently.
6. An independent reproduction: a second student (not the original author) reproduces one full-journal refusal and one exact restoration, recorded in `docs/` as the independent reproduction note.
7. A live-record audit in `results/processed/`, cross-checking every currently active/restoring record against its class's commit history.
8. A fault matrix and assertion report in `docs/` and `results/processed/`, covering every row of both tables above.

## Day by day

| Day | What this means for Week 7 |
|---|---|
| Monday | Freeze the week's question — "does any stress case ever produce an unrecorded bit change?" — name the red-team reviewer as lead (`PROJECT_PLAN.md` Section 7, W7), pass condition: zero unrecorded bit changes across every case. |
| Tuesday | Build and verify the fill/wrap/retire endurance harness alone, confirming the journal reaches and crosses its capacity boundary repeatedly without touching admission or restoration logic yet. |
| Wednesday | Integrate the duplicate/stale/corrupt/out-of-order request suite and the reset-injection tests; retain the first case where a reset leaves the journal or index table in an ambiguous state before deciding the discard rule for that phase. |
| Thursday | Run the frozen full endurance suite plus the mixed-class long run; prepare the ring-state plots, fault matrix and checksum audit as evidence; the second-student reproduction runs in parallel. |
| Friday | 12-minute evaluation against `EVALUATION.md` "Week 7 evaluation": active-record overwrite events (target 0), the fault matrix and the independent reproduction note. |

## Acceptance criteria

- [ ] Every stress case ends in an explicit outcome code with zero unrecorded bit changes (`PROJECT_PLAN.md` Section 7, W7; `README.md` Week 7 Green checkpoint).
- [ ] Ring wrap never overwrites a live record — Invariant 8 holds with zero violations across the endurance run (`PROJECT_PLAN.md` Section 5, Invariant 8; Section 7, W7).
- [ ] Every row in the outcome-code table above is exercised, not only the two paths Week 5's demonstration script already covered.
- [ ] All twelve invariants in the table above are re-checked under adversarial input, not only the subset directly tied to the case under test.
- [ ] The independent reproduction (one full-journal refusal, one exact restoration) succeeds without verbal help from the original author (`PROJECT_PLAN.md` Section 7, W7; root README "Reproduce across authors").
- [ ] Filling the journal to exactly its capacity and issuing one further request returns `refused_capacity` with `free_bytes` unchanged (`PROJECT_PLAN.md` Section 7, W7 smallest test).
- [ ] Numeric result for `EVALUATION.md` "Week 7 evaluation" — active-record overwrite events — is `0`.

## Evidence to retain

Continue `board_serial`, `bitstream_sha`, `source_commit` and `dirty_tree` on every manifest entry, since the endurance suite runs against the same frozen KV260 #2 board/bitstream configuration as Weeks 5-6. Record `status` (`completed`/`refused`/`failed`/`timeout`/`invalid`) and `failure_reason` for every stress case individually in `results/raw/`, per `METRICS_GUIDE.md` "Experiment and outcome fields" — a reset-during-write case that leaves an ambiguous state is a `failed` or `invalid` row with its reason named, not a discarded run. Use `inst_refusals` for the quarantined/refused-update count and `inst_queue_depth` for journal bytes/records used, per the P3 row in `METRICS_GUIDE.md`. Every stress case that first exposed a problem is retained in `results/raw/` alongside its corrected re-run, never overwriting it (root README "Keep failed runs").

## Friday review

- [ ] Numeric result recorded: active-record overwrite events, target 0 (`EVALUATION.md` Week 7 evaluation).
- [ ] Main run ID(s) recorded for the endurance suite, the negative-request suite and the mixed-class long run.
- [ ] Source commit/build ID recorded, matching the manifest `bitstream_sha`.
- [ ] Reference match stated (y/n/bounded) against the expected outcome code for every stress case.
- [ ] What did not work this week recorded, including any reset phase that required discarding the latest packet.
- [ ] Cross-check performed by the second student who independently reproduced the full-journal refusal and exact restoration, confirmed and named.
- [ ] Team verdict (Green/Amber/Red) recorded against the README Week 7 checkpoint language.
- [ ] Next smallest test and owner agreed: from a clean checkout, run the documented one-command sequence and confirm it reproduces the Section 8 demonstration's accepted-path checksum (`PROJECT_PLAN.md` Section 7, W8 smallest test).

## Where this usually goes wrong

- Ring wrap overwriting a record that remains active — the README's own Week 7 Red checkpoint, and the single case Invariant 8 exists to prevent; this is where the Week 1 wrap-behaviour decision either holds or is exposed as incomplete.
- Corruption being detected correctly everywhere except one reset phase, where the recovery rule quietly discards the latest packet without recording why — the README's own Week 7 Amber checkpoint.
- Storing only a flip flag instead of full residue/dependency state for the ordering contract, which is fine under Weeks 2-6's cooperative testing but breaks silently the first time this week's out-of-order or duplicate-request suite exercises it hard.
- Auditing live records only for the class under direct test, missing a cross-class interaction that the mixed-class long run is specifically designed to surface.
- Treating the independent reproduction as a formality rather than a real second attempt — if the second student needs verbal help, the reproduction has not actually passed.

## Hand-off into Week 8

Week 8 freezes exactly the configuration this week's endurance suite validated — the same encoder seed, bitstream and journal sizing — and requires that freeze to survive one more, harder reproduction: an outside student running the documented commands alone. The fault matrix and independent-reproduction note from this week become the evidence that the documented limits and refusal behaviour in the README are accurate, which Week 8's handover checklist depends on directly.
