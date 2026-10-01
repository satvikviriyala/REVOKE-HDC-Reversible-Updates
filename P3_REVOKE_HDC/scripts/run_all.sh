#!/usr/bin/env bash
set -euo pipefail

echo "======================================================================"
echo "REVOKE-HDC Master Execution Pipeline (Weeks 0, 1, 2 Complete)"
echo "Stage Chain: setup -> software reference -> tests -> simulation -> figures"
echo "======================================================================"

# Stage 1: Setup & Environment Validation
echo -e "\n>>> STAGE 1: SETUP & ENVIRONMENT VALIDATION"
bash P3_REVOKE_HDC/scripts/run_week0.sh

# Stage 2: Software Reference & Contract Verification
echo -e "\n>>> STAGE 2: SOFTWARE REFERENCE & CONTRACT VERIFICATION (WEEK 1)"
bash P3_REVOKE_HDC/scripts/run_week1.sh

# Stage 3: Deterministic Tests & Regressions
echo -e "\n>>> STAGE 3: DETERMINISTIC TESTS & NEGATIVE SUITE (WEEK 2)"
python3 P3_REVOKE_HDC/tests/test_smallest_w2.py
python3 P3_REVOKE_HDC/tests/test_negative_cases.py

# Stage 4: Simulation & 1,000-Update Campaign
echo -e "\n>>> STAGE 4: SIMULATION (1,000-UPDATE EXACT RESTORATION REGRESSION)"
python3 P3_REVOKE_HDC/tests/test_exact_restoration.py

# Stage 5: Synthesis & Board Run Status
echo -e "\n>>> STAGE 5: SYNTHESIS & BOARD RUN"
echo "  Synthesis: pending Week 3 (RTL BRAM memories and XOR/popcount path)"
echo "  Board Run: pending Week 5 (KV260 hardware integration)"
echo "  Bit-true software model and register map validation: COMPLETED"

# Stage 6: Figure Generation
echo -e "\n>>> STAGE 6: GENERATE SUMMARY FIGURES"
python3 P3_REVOKE_HDC/scripts/generate_figures.py

echo -e "\n======================================================================"
echo "PIPELINE SUCCESS: Weeks 0, 1, and 2 fully verified and reproducible!"
echo "======================================================================"
