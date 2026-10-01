# Live-State FPGA Studio

## Student handover pack for the eight-week project

This repository is the complete active handover for team P3. Begin here, then use the README inside `P3_REVOKE_HDC/` for project-specific work. Each team works in its own private repository.

Week 0 is deliberately group-local. Open the `WEEK_0.md` file in your assigned folder; it contains exactly three papers for that team and no common reading is required.

> Do not start from a project name or a slide. Read the full project README once, read its Week 6 comparison a second time, and complete its First 48 hours list before writing large RTL or HLS blocks.

## Start in this order

1. Find your assignment in the table below.
2. Read your project README completely.
3. Complete the `WEEK_0.md` file inside your assigned project folder.
4. Open `EVALUATION.md` inside your own project folder.
5. Create the project repository structure shown below.
6. Complete the First 48 hours list in your project README.
7. Record the first evaluated run using the Friday Metrics Guide: `METRICS_GUIDE.md`, even if the run fails.
8. Follow CONTRIBUTING.md: `CONTRIBUTING.md` for branches, pull requests and shared-file changes.
9. Read the "Frozen configuration for this cohort" section at the end of your project README; it fixes the parameters that the rest of the README leaves open.
10. Read `PROJECT_PLAN.md` in your project folder. It is the cohort's concrete build plan: named modules and signal widths, record layouts and register map, invariants as assertions, the four comparison arms, the week-by-week acceptance criteria, and the final demonstration script. Where the README offers options, `PROJECT_PLAN.md` states the one this cohort builds.

## Your assignment

Board numbers are separate from team numbers.

| Team | Active project | Primary device | Central engineering challenge |
|---|---|---|---|
| P3 | REVOKE-HDC: `P3_REVOKE_HDC/README.md` | KV260 #2 | restore compact binary HDC prototypes from sparse update records |

If the instructor changes a physical board assignment, update the run manifest and Friday row. Never infer board identity from the team number.

## Active folder map

```text
repository root
|-- README.md
|-- CONTRIBUTING.md
|-- METRICS_GUIDE.md
|-- friday_metrics.csv
|-- .gitignore
|-- .github/
`-- P3_REVOKE_HDC/
    |-- README.md
    |-- PROJECT_PLAN.md
    |-- WEEK_0.md
    `-- EVALUATION.md
```

## Repository contract for your project folder

Create this structure inside your assigned project folder. Git does not retain empty folders, so add a short placeholder README when needed.

```text
P#_PROJECT_NAME/
|-- README.md              # living run instructions and project decisions
|-- src/                   # synthesizable RTL/HLS and host source
|-- sim/                   # bit-true reference and testbench
|-- tests/                 # deterministic unit, property and regression tests
|-- configs/               # versioned parameters and mode tables
|-- constraints/           # clocks, pins and timing constraints
|-- scripts/               # one-command build, run and figure generation
|-- manifests/             # one machine-readable manifest per retained run
|-- results/
|   |-- raw/               # immutable measurements and traces
|   |-- processed/         # generated summaries
|   `-- figures/           # generated plots
`-- docs/                  # decisions, diagrams and weekly evidence packets
```

By the end of Week 1, the project README must show exact commands for:

```text
setup -> software reference -> tests -> simulation -> synthesis -> board run -> figures
```

If a stage is not ready, include the intended command and mark it clearly as pending. Do not keep required steps only in chat history, a private notebook or a GUI setting.

## Common working rules

### Freeze before measuring

Before a retained experiment, record:

- source state and whether the working tree is clean;
- toolchain/image version;
- device and physical board ID;
- bitstream or build checksum;
- clock and power configuration;
- input/model/event checksum;
- deterministic seed or vector ID;
- comparison arm and configuration;
- reset and warm-up procedure;
- raw output and trace paths.

### Keep failed runs

A failed or refused run is still evidence. Keep its manifest, raw output and short failure reason. Do not silently rerun with changed parameters and replace the earlier result.

### Make internal decisions visible

Every project has a controller whose correctness depends on hidden-looking state: epoch, progress, ownership, journal status or merge key. Expose enough trace/status data to reconstruct one accepted path and one refused or failed path on the board.

### Compare one mechanism at a time

All four arms in a project must use the same workload, clock, arithmetic rules and measurement boundary. If the model, event order, array size or memory budget changes too, the result no longer isolates the intended mechanism.

### Reproduce across authors

Every week, one student who did not create an artefact must reproduce it. By Week 8, a student outside the team must run one smoke test from the README without verbal help. The reproducer also countersigns that week's dated notebook entries.

### Keep the work inside the course

Do not post, present, upload or submit project material outside this repository (public repositories, social media, competitions, external reports, talks) without the instructor's written approval. This applies for the whole eight weeks and until the instructor releases the cohort's material.

## Weekly rhythm

| Day | Team activity |
|---|---|
| Monday | freeze the week's question, owners, pass condition and smallest test |
| Tuesday | build and verify one component in software or simulation |
| Wednesday | integrate, retain the first failure and update the decision log |
| Thursday | run the frozen checkpoint and prepare evidence; the reproducer countersigns the week's notebook entries |
| Friday | 12-minute evaluation: explanation, live evidence, failure path and next step |

Each Friday packet contains:

1. one-page progress summary;
2. commands and configuration used;
3. one architecture/state diagram updated to current reality;
4. one passing trace and one relevant failing/refused trace;
5. raw result link and generated summary/figure;
6. checkpoint status with evidence;
7. one reproduced artefact and reproducer name;
8. next week's smallest test and owner.

## Team roles

Rotate these roles weekly so that every student understands the full system.

| Role | Responsibility |
|---|---|
| system owner | interfaces, configuration and milestone integration |
| reference owner | bit-true model, deterministic vectors and mismatch reports |
| hardware owner | RTL/HLS, timing and on-board observability |
| verification owner | assertions, fault injection and regression |
| red-team reviewer | tries to break the stated invariant and reproduces another member's artefact |

For smaller teams, combine roles but still name the responsibilities.

## Common completion standard

A project is complete only when:

- the engineering contract is explicit;
- the reduced system matches its reference;
- the live controller path is demonstrated, not only a boundary case;
- accepted and refused/failure paths are observable;
- all four comparison arms have been run fairly;
- limits and negative results are stated;
- final figures regenerate from raw data;
- an independent student completes the documented smoke test.

## Evaluation and run records

Use the `EVALUATION.md` file inside your assigned project folder for the eight weekly reviews. It contains only the checkpoints and evidence for that project. For shared run-row definitions, use METRICS_GUIDE.md: `METRICS_GUIDE.md`.
