"""
Week 2 Smallest Test Verification:
Tests one hand-built 2-entry packet update and exact restoration.
Matches the worked example in WEEK_2.md lines 14-21.
"""

import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sim.engine import RevokeHdcEngine, OutcomeCode
from sim.packet_generator import PacketGenerator


def test_smallest_w2():
    print("=== Running Week 2 Smallest Test (2-entry hand-built packet) ===")
    engine = RevokeHdcEngine(seed=0x20261001)
    gen = PacketGenerator(seed=0x20261001)

    # Initial state setup: class 0, dim 100 = 0, dim 200 = 1
    engine.proto_mem.set_bit(0, 100, 0)
    engine.proto_mem.set_bit(0, 200, 1)

    # Baseline clone
    baseline_words = engine.proto_mem.clone_state()
    baseline_crc = engine.proto_mem.get_crc32(0)

    # Generate hand-built 2-entry packet
    pkt = gen.generate_hand_packet_w2_smallest(engine.proto_mem, class_id=0)
    wire_bytes = pkt.to_bytes()

    print(f"Wire packet bytes: {len(wire_bytes)} (expected: 16 + 3*2 = 22 bytes)")
    assert len(wire_bytes) == 22, f"Expected 22 bytes, got {len(wire_bytes)}"

    # 1. Forward Commit
    outcome = engine.process_update_packet(wire_bytes)
    print(f"Update outcome: {outcome} ({OutcomeCode(outcome).name})")
    assert outcome == OutcomeCode.ACCEPTED, f"Expected ACCEPTED (0), got {outcome}"

    # Verify bits flipped
    assert engine.proto_mem.get_bit(0, 100) == 1, "Dim 100 did not flip to 1"
    assert engine.proto_mem.get_bit(0, 200) == 0, "Dim 200 did not flip to 0"
    assert engine.proto_mem.get_crc32(0) != baseline_crc, "Prototype CRC did not change after commit"

    # 2. Exact Reverse-Order Restoration
    restore_outcome = engine.process_restoration_request(class_id=0, update_id=pkt.update_id)
    print(f"Restoration outcome: {restore_outcome} ({OutcomeCode(restore_outcome).name})")
    assert restore_outcome == OutcomeCode.RESTORED, f"Expected RESTORED (9), got {restore_outcome}"

    # Verify bits restored
    assert engine.proto_mem.get_bit(0, 100) == 0, "Dim 100 not restored to 0"
    assert engine.proto_mem.get_bit(0, 200) == 1, "Dim 200 not restored to 1"
    assert engine.proto_mem.get_crc32(0) == baseline_crc, "Prototype CRC does not match baseline"

    # Full memory compare
    restored_words = engine.proto_mem.clone_state()
    assert restored_words == baseline_words, "Restored memory has bit mismatches against baseline!"

    print("PASS: Week 2 Smallest Test passed with 0 mismatches!")


if __name__ == "__main__":
    test_smallest_w2()
