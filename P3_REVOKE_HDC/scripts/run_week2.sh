#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "P3 REVOKE-HDC: Running Week 2 Exact Restoration Campaign"
echo "=========================================================="

echo "[1/4] Running Week 2 Smallest Test (2-entry packet)..."
python3 P3_REVOKE_HDC/tests/test_smallest_w2.py

echo -e "\n[2/4] Running Full Negative Test Suite (All 10 Injected Cases)..."
python3 P3_REVOKE_HDC/tests/test_negative_cases.py

echo -e "\n[3/4] Running 1,000-Update Exact Restoration Regression..."
python3 P3_REVOKE_HDC/tests/test_exact_restoration.py

echo -e "\n[4/4] Generating Publication Figures..."
python3 P3_REVOKE_HDC/scripts/generate_figures.py

echo -e "\n=========================================================="
echo "Week 2 Campaign: ALL SUITES PASSED WITH 0 MISMATCHES!"
echo "=========================================================="
