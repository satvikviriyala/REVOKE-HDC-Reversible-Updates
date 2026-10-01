#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "P3 REVOKE-HDC: Running Week 1 Contract & Vector Verification"
echo "=========================================================="

python3 - << 'EOF'
import csv
import json

print("[1/3] Validating 42 Hand-Checked Vectors from tests/hand_vectors.csv...")
csv_path = "P3_REVOKE_HDC/tests/hand_vectors.csv"
vectors = []
with open(csv_path) as f:
    reader = csv.DictReader(f)
    for row in reader:
        vectors.append(row)

assert len(vectors) == 42, f"Expected 42 vectors, found {len(vectors)}"
accept_count = 0
refuse_count = 0
retained_failures = 0

for v in vectors:
    vid = v["vector_id"]
    verdict = v["verdict"]
    retained = v["retained_failure"] == "yes"
    if verdict == "accept":
        accept_count += 1
        r = int(v["residue"])
        u = int(v["contribution"])
        expected_sum = int(v["sum"])
        assert r + u == expected_sum, f"[{vid}] Sum mismatch"
        old_b = int(v["old_bit"])
        new_b = int(v["new_bit"])
        calc_old = 1 if r >= 0 else 0
        calc_new = 1 if (r + u) >= 0 else 0
        assert old_b == calc_old, f"[{vid}] old_bit mismatch"
        assert new_b == calc_new, f"[{vid}] new_bit mismatch"
    else:
        refuse_count += 1
        if retained:
            retained_failures += 1

print(f"  Total Vectors: {len(vectors)} (Accepted: {accept_count}, Refused: {refuse_count}, Retained Failures: {retained_failures})")
assert accept_count == 36
assert refuse_count == 6
assert retained_failures == 1

print("\n[2/3] Checking Sizing Formulations & Break-Even Math...")
def record_bytes(f): return 16 + 2 * f
def wire_bytes(f): return 16 + 3 * f
snapshot_bytes = 512

assert record_bytes(40) == 96, "F=40 record size must equal 96 bytes"
assert record_bytes(96) == 208, "F=96 record size must equal 208 bytes"
assert record_bytes(247) == 510, "F=247 record size must equal 510 bytes"
assert record_bytes(248) == 512, "F=248 record size must equal 512 bytes"
assert wire_bytes(96) == 304, "F=96 wire size must equal 304 bytes"
print("  F=40  -> Record: 96 B  (Snapshot: 512 B, Savings: 81.3%)")
print("  F=96  -> Record: 208 B (Snapshot: 512 B, Savings: 59.4%) [Frozen Max]")
print("  F=247 -> Record: 510 B (Snapshot: 512 B, Savings:  0.4%) [Last Sparse Win]")
print("  F=248 -> Record: 512 B (Snapshot: 512 B, Equal)           [Break-Even Boundary]")

print("\n[3/3] Validating Machine-Readable Configuration...")
with open("P3_REVOKE_HDC/configs/revoke_hdc_config.json") as f:
    cfg = json.load(f)
assert cfg["architecture"]["dimension_d"] == 4096
assert cfg["architecture"]["class_count"] == 4
assert cfg["wire_packet"]["max_entries_f"] == 96
assert cfg["journal_record"]["max_record_bytes"] == 208
assert cfg["journal_record"]["breakeven_f"] == 248
print("  Configuration parameters verified and consistent with contract.")

print("\nWeek 1 Contract & Vector Checks: ALL PASS!")
EOF
