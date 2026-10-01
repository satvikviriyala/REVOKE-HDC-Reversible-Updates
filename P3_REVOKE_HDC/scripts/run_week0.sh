#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "P3 REVOKE-HDC: Running Week 0 Foundations & Verification"
echo "=========================================================="

python3 - << 'EOF'
import sys

print("[1/3] Verifying 8-Dimensional Hamming Distance Example...")
Q  = [1, 0, 1, 1, 0, 0, 1, 0]
P0 = [1, 1, 1, 0, 0, 0, 1, 1]
P1 = [0, 0, 1, 1, 1, 0, 1, 0]

h0 = sum(q ^ p for q, p in zip(Q, P0))
h1 = sum(q ^ p for q, p in zip(Q, P1))
print(f"  Query Q:      {Q}")
print(f"  Prototype P0: {P0} -> Hamming Dist = {h0}")
print(f"  Prototype P1: {P1} -> Hamming Dist = {h1}")
assert h0 == 3, f"Expected 3, got {h0}"
assert h1 == 2, f"Expected 2, got {h1}"
winner = 1 if h1 < h0 else 0
print(f"  Classification Winner: Class {winner} (Margin: {abs(h0 - h1)} bit)")

print("\n[2/3] Verifying Threshold Loss: Non-Injectivity of sign_threshold...")
pairs = [
    (2, 8, -4),   # Pair 1: both bit 1
    (-1, -15, 5), # Pair 2: both bit 0
    (0, 6, -1),   # Pair 3: both bit 1
]
for c1, c2, u in pairs:
    b1 = 1 if c1 >= 0 else 0
    b2 = 1 if c2 >= 0 else 0
    assert b1 == b2, "Initial bits must match"
    new_c1 = c1 + u
    new_c2 = c2 + u
    new_b1 = 1 if new_c1 >= 0 else 0
    new_b2 = 1 if new_c2 >= 0 else 0
    print(f"  c1={c1:+3d}, c2={c2:+3d} (Shared Bit {b1}) + Update {u:+2d} -> c1'={new_c1:+3d} (Bit {new_b1}) vs c2'={new_c2:+3d} (Bit {new_b2})")
    assert new_b1 != new_b2, "Update must cause diverging threshold bit states"

print("\n[3/3] Checking Core Restoration Order Statement:")
statement = "Restoration for a class occurs strictly in reverse commit order, recomputing each restored prototype bit as sign_threshold(pre_update_residue) from the active head record."
print(f"  '{statement}'")

print("\nWeek 0 Foundation Checks: ALL PASS!")
EOF
