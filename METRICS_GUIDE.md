# Friday Metrics Guide

Student handover: `README.md` | Blank CSV template: `friday_metrics.csv`

Use `friday_metrics.csv` as an append-only summary with one row per evaluated configuration. Keep detailed traces in `results/raw/<run_id>/` and the matching manifest in `manifests/<run_id>.yaml`.

## Required identifiers

| Column | Rule |
|---|---|
| `run_id` | unique across CSV, manifest and raw-data folder; use `P#_YYYYMMDD_HHMM_short-arm` |
| `date_utc` | ISO-8601 UTC time |
| `team` | `P1` to `P5` |
| `project` | `ATOMIC_SCALE`, `MODEL_SPLICE`, `LANE_EVAC`, `REVOKE_HDC` or `VOXEL_FOLD` |
| `device` | platform family, such as `kv260` |
| `board_serial` | physical device identifier, required from Week 5 |
| `source_commit` | full source commit hash |
| `dirty_tree` | `false` for final retained comparisons; keep but label dirty diagnostic runs |
| `bitstream_sha` | SHA-256 or approved build identifier |
| `toolchain_id` | frozen lab image/toolchain identifier |

## Experiment and outcome fields

| Column | Rule |
|---|---|
| `mode` | operating mode, active mask, journal policy or table policy |
| `task` | workload/scenario name |
| `arm` | A, B, C or D from the project README |
| `status` | `completed`, `refused`, `failed`, `timeout` or `invalid` |
| `failure_reason` | `none` for completed runs; otherwise a short machine-readable reason |
| `metric_name`, `metric_value` | primary metric and value, with unit in the name where needed |
| `golden_match` | `y`, `n` or `bounded`; exact-core accepted runs normally require `y` |
| `notes` | short context only; technical details belong in the manifest |

## Timing and environment fields

- Record median and p95 for timed campaigns.
- Use `latency_ms_p99999` only when enough samples support it; do not fill it from a tiny run.
- Report energy over the complete declared workload interval.
- Use the same rail boundary for active and idle power.
- Record ambient start/end temperature from Week 5.
- State warm-up and timed iteration counts.
- Keep batch at 1 unless batch size is an explicit experiment variable.

## Implementation fields

Record post-implementation `lut`, `ff`, `dsp`, `bram36`, `uram`, `fmax_mhz` and `wns_ns` where available. Leave a genuinely non-applicable value empty. Do not enter zero when the value is unknown.

## Shared instrumentation columns

The existing `inst_*` names are intentionally general. Interpret them as follows and describe any extra project counters in the raw manifest.

| Team | Required interpretation |
|---|---|
| P1 LANE-EVAC | `inst_refusals`: contraction refusals; `inst_queue_depth`: live owned tiles; `inst_coalesced`: transferred ownership entries |
| P2 MODEL-SPLICE | `inst_refusals`: delayed/refused update packets; `inst_queue_depth`: patch entries used; `inst_coalesced`: corrected prefix entries |
| P3 REVOKE-HDC | `inst_refusals`: quarantined/refused updates; `inst_queue_depth`: journal bytes or records used; `inst_coalesced`: affected dimensions |
| P4 ATOMIC-SCALE | `inst_refusals`: transition refusals; `inst_queue_depth`: affected-accumulator count; `inst_max_age`: available slack or selected bound, named in notes |
| P5 VOXEL-FOLD | `inst_queue_depth`: peak raw/table occupancy; `inst_coalesced`: merged events; `inst_dropped`: declared drops; `inst_refusals`: events refused by a bounded policy |

## Example row

This is documentation only. Do not paste it unchanged.

```csv
P4_20260904_1430_live,2026-09-04T14:30:00Z,P4,ATOMIC_SCALE,kv260,K26-03,0123456789abcdef,false,sha256-example,lab-2026.1,M0_to_M3,small_tensor,D,completed,none,transition_cycles,68,0.00034,0.00036,,,,,25.0,25.3,20,1000,1,12000,18000,34,18,2,200.0,0.12,75,24,24,0,0,y,,,example_only
```

## Submission rules

1. Failed, refused, invalid and timed-out runs still receive rows.
2. Never replace an unknown value with zero.
3. From Week 6, every final comparison row needs an arm.
4. Validate that every CSV row has the header's column count.
5. A plot must be regenerated from retained raw data, not manually edited values.
6. If `golden_match=n`, keep the row as a diagnostic failure and do not present its performance as a correct result.
