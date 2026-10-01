# Contributing to the Live-State FPGA Studio

Student handover: `README.md`

This repository belongs to team P3. Keep changes small, reproducible and limited to `P3_REVOKE_HDC/` unless you are deliberately updating one of the shared files listed below.

## Sharing outside the course

Do not fork this repository to a personal account, mirror it, or paste its contents into any public service, competition entry, external report or social-media post without the instructor's written approval. Pull requests that add links to external copies of project material are not merged until the instructor approves. Reference PDFs of third-party papers stay out of Git if their licence forbids redistribution.

## Branch and pull-request names

Use:

`p<group>/w<week>-<short-topic>`

Examples:

- `p1/w3-ownership-trace`
- `p4/w4-conversion-bitmap`

Open one pull request for one coherent change. Link the weekly checkpoint issue and state the exact verification command.

## Before committing

- run the deterministic software/reference tests;
- run the relevant simulation or assertion set;
- update commands or parameters in the project README;
- retain raw evidence under the documented run ID;
- complete the current table in the project's `EVALUATION.md`;
- ask a team member who did not write the artefact to reproduce it;
- remove credentials, personal paths and generated tool directories.

## Commit messages

Use a short action and component, for example:

`P2: add exactly-once prefix correction check`

Do not use messages such as `updates`, `final` or `fixed stuff`.

## Shared-file changes

Changes to the root `README.md`, `METRICS_GUIDE.md`, `friday_metrics.csv` or `.github/` require the instructor's approval, because these files are kept identical across every team repository. State which group-specific behaviour motivated the shared change. A project's "Frozen configuration for this cohort" section changes only with the instructor's written approval in the pull request.

## Large files

Do not commit FPGA build directories, local environments, downloaded datasets or credentials. Store immutable small test vectors and checksums in the project. Ask the instructor before adding a generated file larger than 10 MiB or enabling Git LFS.

## Failed work

Keep failing vectors and run metadata when they explain a design decision. Mark their status and failure reason. Do not overwrite or rename a failed run to make it appear successful.

## Review standard

A change is ready to merge when:

- its external behaviour is documented;
- widths, ordering and reset behaviour are explicit where relevant;
- new behaviour has a deterministic test or assertion;
- the result can be regenerated from the recorded command;
- no unrelated generated files are included.
