# P3 REVOKE-HDC Week 1 Submission Package (W1-R1)

This package implements the Week 1 contract described in the supplied `WEEK_1.md`: freeze the update alphabet, residue interpretation, sparse wire/journal record format, refusal outcomes, ordering contract, sizing math and evidence before any software reference model or RTL implementation begins.

## Final numeric results

- Prototype width: 4096 bits = 512 bytes.
- Wire packet: `L_wire(F) = 16 + 3F` bytes under the R1 clarification that the 16-byte listed header already contains the checksum field.
- Persisted sparse journal record: `R(F) = 16 + 2F` bytes.
- Frozen packet limit: `F <= 96`.
- Maximum supported journal record: `R(96) = 208 bytes`.
- Sparse-vs-full break-even: `16 + 2F < 512` -> `F < 248`.
- Signed residue: 4-bit two's complement, `-8..+7`.
- Signed contribution: 4-bit two's complement, `-8..+7`; conceptual `+8` is not encodable and is refused before packing.
- `sign_threshold(x) = 1` when `x >= 0`, otherwise `0` (R1 tie convention frozen here because the supplied Week 1 file does not define zero explicitly).

## Package map

- `docs/interface_contract.md` - exact byte/bit contract and persisted record format.
- `docs/validation_rules.md` - equations, signed arithmetic, validation order and atomicity.
- `docs/decision_log.md` - all 16 Week 1 decisions with owners/status.
- `docs/ordering_state.md` + `assets/ordering_state.png` - lifecycle and controller flow used by this submission profile.
- `docs/sizing_sheet.md` - all required byte-count calculations and capacity math.
- `docs/refusal_table.md` - outcomes 0..10 with one-line project-specific triggers.
- `tests/hand_vectors.csv` and `.md` - 36 valid worked vectors plus retained failure cases.
- `configs/revoke_hdc_week1_v1.yaml` - versioned machine-readable parameter mirror.
- `manifests/week1_freeze_manifest.yaml` - frozen artifact identity.
- `evaluation/EVALUATION_WEEK1.md` - Friday review and evidence status.
- `manual/REVOKE_HDC_Week1_Detailed_Manual.pdf` - detailed chronological manual.

## Source-truth boundary

The uploaded artifact references `README.md`, `PROJECT_PLAN.md` and `EVALUATION.md`, but those files were not supplied. This package therefore distinguishes three categories:

1. **Source-frozen facts** copied from `WEEK_1.md` (field widths, F limit, outcome codes, record sizing equation).
2. **R1 engineering decisions** required to make the contract executable and internally consistent (endianness, zero threshold convention, CRC parameters, ring wrap, memory sizes, clock target, AXI allocation).
3. **External/team evidence still required** where truth cannot be manufactured from the supplied file: exact encoder/dataset identity, empirical contribution distribution, calibrated `theta_A/theta_B`, original Git source commit, and independent reviewer/countersignature.

The contract documents are complete without those measurements, but the Friday team verdict is intentionally recorded as **AMBER pending external evidence** rather than falsely claiming measured/calibrated values.

## Two deliberate clarifications

The source calls the header 16 bytes and lists a 2-byte checksum inside those 16 bytes, while also describing length as header plus payload plus checksum. R1 treats the checksum as already included in the 16-byte header, so wire length is `16+3F`.

The source gives a 4-bit signed contribution and says `|u| <= 8`. In two's-complement, four signed bits represent `-8..+7`; therefore `-8` is legal but `+8` is not wire-encodable. R1 refuses conceptual `+8` before packing and retains an explicit failure vector demonstrating the issue.

## Submission status

**Contract/equation completeness: complete. Evidence completeness: AMBER.** Replace the external/team evidence entries listed in `evaluation/EVALUATION_WEEK1.md` before claiming a fully measured Green checkpoint.
