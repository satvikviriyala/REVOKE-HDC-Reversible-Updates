"""
Negative Test Suite for REVOKE-HDC:
Systematically verifies every row in the WEEK_2.md negative-test mapping table:
- Stale old_bit -> refused_stale (5)
- Corrupt residue / contribution out of range -> refused_residue (4)
- Duplicate dimension index within packet -> refused_duplicate (6)
- Journal capacity full (Jreq > Jfree) -> refused_capacity (2)
- Corrupt or mismatched checksum -> refused_checksum (3)
- Out-of-order restoration attempt -> refused_ordering (7)
- Corrupted prototype bit prior to restoration -> refused_bit_state (8)
- Repeat restoration of already-retired record -> already_retired (10)
- Trust gate failure (margins below threshold / agreement fail) -> quarantined (1)

Verifies Invariant 7: Refused or quarantined requests change neither prototype memory
nor journal free_bytes.
"""

import sys
import os
import csv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sim.engine import RevokeHdcEngine, OutcomeCode
from sim.packet import WireEntry, WirePacket
from sim.packet_generator import PacketGenerator
from sim.crc16 import compute_packet_crc


def test_negative_cases():
    print("=== Running Complete REVOKE-HDC Negative Test Suite ===")
    engine = RevokeHdcEngine(seed=0x20261001)
    gen = PacketGenerator(seed=0x20261001)

    results = []

    def check_invariants_untouched(baseline_words, baseline_free, case_name):
        curr_words = engine.proto_mem.clone_state()
        curr_free = engine.journal_ring.free_bytes
        assert curr_words == baseline_words, f"[{case_name}] Prototype memory mutated on refusal!"
        assert curr_free == baseline_free, f"[{case_name}] Journal free_bytes changed on refusal!"

    # Case 1: Corrupt Checksum -> refused_checksum (3)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    pkt = gen.generate_valid_packet(engine.proto_mem, class_id=0, target_F=10)
    raw = bytearray(pkt.to_bytes())
    raw[14] ^= 0xFF  # Corrupt checksum byte
    outcome = engine.process_update_packet(bytes(raw))
    print(f"Case 1 (Corrupt Checksum): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_CHECKSUM
    check_invariants_untouched(base_words, base_free, "Corrupt Checksum")
    results.append(("Corrupt Checksum", "refused_checksum", 3, outcome, "PASS"))

    # Case 2: Duplicate Dimension Index -> refused_duplicate (6)
    engine.proto_mem.set_bit(0, 42, 0)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    entries_dup = [
        WireEntry(dim_idx=42, pre_residue=-2, contrib=3, expected_old_bit=0, expected_new_bit=1),
        WireEntry(dim_idx=42, pre_residue=-2, contrib=3, expected_old_bit=0, expected_new_bit=1),
    ]
    pkt_dup = WirePacket.create(1, 1050, 0, engine.index_table.class_next_seq[0], 0, 180, 0, 180, entries_dup)
    outcome = engine.process_update_packet(pkt_dup.to_bytes())
    print(f"Case 2 (Duplicate Dimension): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_DUPLICATE
    check_invariants_untouched(base_words, base_free, "Duplicate Dimension")
    results.append(("Duplicate Dimension", "refused_duplicate", 6, outcome, "PASS"))

    # Case 3: Out-of-alphabet Residue / Contribution -> refused_residue (4)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    # Conceptual +8 is unencodable or raw out of range
    # In wire format, 4 bits signed represents -8..+7. If someone sends an entry where contrib > 7 or residue > 7
    # Here we test wire parser detecting residue > 7 or out of range
    entries_res = [
        WireEntry(dim_idx=50, pre_residue=10, contrib=2, expected_old_bit=1, expected_new_bit=1)
    ]
    # In WireEntry, pre_residue 10 wraps or is rejected. Let's make an entry with out of range in raw bytes
    raw_pkt = bytearray(pkt.to_bytes())
    # Manually pack invalid signed 4-bit by setting entry field
    # Alternatively, our engine directly checks: not (-8 <= e.pre_residue <= 7)
    # Let's test by crafting wire bytes with invalid entry values or invalid bit claim
    # WireEntry with pre_residue -8 and contrib +8 (which cannot flip or overflows)
    pkt_res = WirePacket.create(1, 1051, 0, engine.index_table.class_next_seq[0], 0, 180, 0, 180, entries_res)
    outcome = engine.process_update_packet(pkt_res.to_bytes())
    print(f"Case 3 (Residue/Contrib Exceeded): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_RESIDUE
    check_invariants_untouched(base_words, base_free, "Residue Exceeded")
    results.append(("Residue Exceeded", "refused_residue", 4, outcome, "PASS"))

    # Case 4: Stale Old Bit -> refused_stale (5)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    # Generate packet against current bit, but flip prototype bit right before submitting!
    pkt_stale = gen.generate_valid_packet(
        engine.proto_mem, class_id=0, target_F=5, sequence=engine.index_table.class_next_seq[0]
    )
    dim_target = pkt_stale.entries[0].dim_idx
    curr_b = engine.proto_mem.get_bit(0, dim_target)
    # Invert stored bit in memory behind packet's back
    engine.proto_mem.set_bit(0, dim_target, 1 - curr_b)
    base_words_stale = engine.proto_mem.clone_state()
    outcome = engine.process_update_packet(pkt_stale.to_bytes())
    print(f"Case 4 (Stale Old Bit): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_STALE
    check_invariants_untouched(base_words_stale, base_free, "Stale Old Bit")
    results.append(("Stale Old Bit", "refused_stale", 5, outcome, "PASS"))
    # Restore inverted bit
    engine.proto_mem.set_bit(0, dim_target, curr_b)

    # Case 5: Trust Gate Margin Failure -> quarantined (1)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    pkt_quar = gen.generate_valid_packet(
        engine.proto_mem, class_id=1, target_F=5, sequence=engine.index_table.class_next_seq[1]
    )
    # Lower mA below theta_A=128
    pkt_quar.mA = 80
    pkt_quar.checksum = compute_packet_crc(pkt_quar.to_bytes(compute_crc=False))
    outcome = engine.process_update_packet(pkt_quar.to_bytes())
    print(f"Case 5 (Quarantined Margin): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.QUARANTINED
    check_invariants_untouched(base_words, base_free, "Quarantined Margin")
    results.append(("Quarantined Margin", "quarantined", 1, outcome, "PASS"))

    # Case 6: Out-of-Order Sequence -> refused_ordering (7 at admission)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    pkt_seq = gen.generate_valid_packet(
        engine.proto_mem, class_id=1, target_F=5, sequence=engine.index_table.class_next_seq[1]
    )
    pkt_seq.sequence = 999  # Skip expected sequence
    pkt_seq.checksum = compute_packet_crc(pkt_seq.to_bytes(compute_crc=False))
    outcome = engine.process_update_packet(pkt_seq.to_bytes())
    print(f"Case 6 (Out-of-Order Sequence): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_ORDERING
    check_invariants_untouched(base_words, base_free, "Out-of-Order Sequence")
    results.append(("Out-of-Order Sequence", "refused_ordering", 7, outcome, "PASS"))

    # Case 7: Journal Capacity Full -> refused_capacity (2)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    saved_free = engine.journal_ring.free_bytes
    engine.journal_ring.free_bytes = 10  # Force insufficient capacity (< 16 + 2*F)
    pkt_cap = gen.generate_valid_packet(
        engine.proto_mem, class_id=1, target_F=5, sequence=engine.index_table.class_next_seq[1]
    )
    outcome = engine.process_update_packet(pkt_cap.to_bytes())
    print(f"Case 7 (Journal Full): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_CAPACITY
    engine.journal_ring.free_bytes = saved_free
    check_invariants_untouched(base_words, base_free, "Journal Full")
    results.append(("Journal Full", "refused_capacity", 2, outcome, "PASS"))

    # Case 8: Out-of-Order Restoration -> refused_ordering (7 at restoration)
    # Commit two updates for class 2: Update A then Update B
    pkt_A = gen.generate_valid_packet(engine.proto_mem, class_id=2, target_F=8)
    res_A = engine.process_update_packet(pkt_A.to_bytes())
    assert res_A == OutcomeCode.ACCEPTED

    pkt_B = gen.generate_valid_packet(engine.proto_mem, class_id=2, target_F=8)
    res_B = engine.process_update_packet(pkt_B.to_bytes())
    assert res_B == OutcomeCode.ACCEPTED

    # Attempt to restore Update A before Update B!
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    outcome = engine.process_restoration_request(class_id=2, update_id=pkt_A.update_id)
    print(f"Case 8 (Out-of-Order Restoration): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_ORDERING
    check_invariants_untouched(base_words, base_free, "Out-of-Order Restoration")
    results.append(("Out-of-Order Restoration", "refused_ordering", 7, outcome, "PASS"))

    # Case 9: Corrupted Prototype Bit prior to Restore -> refused_bit_state (8)
    # Now restore Update B, but first corrupt one of its target dimensions in prototype RAM!
    slot_B_id = engine.index_table.class_head_slot[2]
    slot_B = engine.index_table.slots[slot_B_id]
    corrupt_dim = list(slot_B.expected_new_bits.keys())[0]
    expected_new = slot_B.expected_new_bits[corrupt_dim]
    engine.proto_mem.set_bit(2, corrupt_dim, 1 - expected_new)  # Corrupt bit
    base_words_corrupt = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes

    outcome = engine.process_restoration_request(class_id=2, update_id=pkt_B.update_id)
    print(f"Case 9 (Corrupted Prototype Bit on Restore): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.REFUSED_BIT_STATE
    check_invariants_untouched(base_words_corrupt, base_free, "Corrupted Prototype Bit on Restore")
    results.append(("Corrupted Prototype Bit on Restore", "refused_bit_state", 8, outcome, "PASS"))

    # Fix corrupted bit so we can legally restore Update B then Update A
    engine.proto_mem.set_bit(2, corrupt_dim, expected_new)
    res_restore_B = engine.process_restoration_request(class_id=2, update_id=pkt_B.update_id)
    assert res_restore_B == OutcomeCode.RESTORED

    # Case 10: Repeat Restoration -> already_retired (10)
    base_words = engine.proto_mem.clone_state()
    base_free = engine.journal_ring.free_bytes
    outcome = engine.process_restoration_request(class_id=2, update_id=pkt_B.update_id)
    print(f"Case 10 (Repeat Restoration of Retired Record): Outcome={outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.ALREADY_RETIRED
    check_invariants_untouched(base_words, base_free, "Repeat Restoration")
    results.append(("Repeat Restoration", "already_retired", 10, outcome, "PASS"))

    # Also restore Update A to leave class 2 clean
    res_restore_A = engine.process_restoration_request(class_id=2, update_id=pkt_A.update_id)
    assert res_restore_A == OutcomeCode.RESTORED

    # Write negative test report to CSV
    os.makedirs("P3_REVOKE_HDC/results/raw", exist_ok=True)
    csv_path = "P3_REVOKE_HDC/results/raw/negative_tests.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["case_name", "expected_outcome_name", "expected_code", "actual_code", "status"])
        for r in results:
            writer.writerow(r)

    print(f"\nALL 10 NEGATIVE TEST CASES PASSED! Results saved to {csv_path}")


if __name__ == "__main__":
    test_negative_cases()
