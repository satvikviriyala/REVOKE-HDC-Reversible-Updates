# Week 1 Evaluation - W1-R1

## Numeric result

**Maximum supported persisted journal record size: 208 bytes.**

Derivation: frozen `F_max=96`, `R(F)=16+2F`, therefore `R(96)=16+192=208 B`.

## Evidence IDs

- Frozen document run ID: `P3_REVOKE_HDC_W1_FREEZE_R1_20260925`.
- Source document SHA-256: `38992d4c044d56fda32810f798eb3dccc67e03fb975457de48fc86507cfbb4aa`.
- Hand-vector evidence: `tests/hand_vectors.csv` (42 total: 36 valid, 6 refusals).
- Config mirror: `configs/revoke_hdc_week1_v1.yaml`.

## Friday checklist

- [x] Numeric maximum record size recorded: 208 B.
- [x] Main document/test IDs recorded.
- [ ] Original Git source commit/build ID - not present in uploaded material; replace manifest placeholder with repository commit.
- [x] Reference match stated as bounded against the supplied Week 1 contract.
- [x] What did not work retained: V037 demonstrates the `+8`/signed-4-bit representability conflict.
- [ ] Independent cross-checker named/countersigned - requires a real second person.
- [ ] Exact encoder/dataset and empirical alphabet check attached.
- [ ] `theta_A` / `theta_B` calibrated from the chosen dataset; illustrative 128 is intentionally not claimed.
- [x] Next smallest test stated: Week 2 should build one 2-entry packet and restore it in the software model.

## Team verdict

**AMBER pending external evidence.** The packet/record/refusal/sizing contract is complete and internally checkable, but the supplied source does not contain the team-specific encoder/dataset, calibrated thresholds, repository commit, independent reviewer identity, or the actual `PROJECT_PLAN.md` Section 3.3 controller-state names. Claiming Green without those would manufacture evidence.

### Conditions to change AMBER -> GREEN

1. Fill `encoder_dataset.encoder` and `encoder_dataset.dataset` in the config and document exact preprocessing/split.
2. Attach a histogram/summary of real per-dimension contributions confirming all values fit the frozen encoded alphabet, or redesign the field/alphabet together.
3. Replace `theta_A/theta_B: null` with calibrated values and attach the calibration method/result.
4. Record the real Git commit/build ID.
5. Have a second person check the 42-vector file and sign/date this evaluation.
6. Cross-check the R1 controller labels against the actual Section 3.3 state names and rename if needed.
