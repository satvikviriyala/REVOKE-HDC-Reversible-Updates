"""
Candidate Transition Packet Generator for REVOKE-HDC.
Generates deterministic valid packets and directed negative test vectors.
"""

import random
from typing import Dict, List, Optional, Tuple
from sim.hdc_core import PrototypeMemory, sign_threshold
from sim.packet import WireEntry, WirePacket


class PacketGenerator:
    """
    Generates candidate transition packets for the REVOKE-HDC testbench.
    """

    def __init__(self, seed: int = 0x20261001):
        self.rng = random.Random(seed)
        self.next_update_id: int = 1000
        self.class_sequences: List[int] = [0, 0, 0, 0]

    def generate_valid_packet(
        self,
        proto_mem: PrototypeMemory,
        class_id: int,
        target_F: Optional[int] = None,
        source_id: int = 1,
        sequence: Optional[int] = None,
    ) -> WirePacket:
        """
        Generates a valid, admitted candidate transition packet targeting class_id.
        All entries match current stored prototype bits and respect signed alphabet bounds.
        """
        if target_F is None:
            # Typical realistic distribution centered around 35-50 flips
            target_F = min(96, max(2, int(self.rng.gauss(42, 18))))

        update_id = self.next_update_id
        self.next_update_id += 1
        if sequence is None:
            sequence = self.class_sequences[class_id]
            self.class_sequences[class_id] += 1

        # Select target_F distinct random dimensions
        dims = sorted(self.rng.sample(range(4096), target_F))

        entries: List[WireEntry] = []
        for dim in dims:
            stored_bit = proto_mem.get_bit(class_id, dim)
            if stored_bit == 0:
                # pre_residue must be < 0: range -8..-1
                pre_res = self.rng.randint(-8, -1)
                # To cause a flip, contrib must push sum >= 0: contrib >= -pre_res
                # Since pre_res in [-8, -1], -pre_res in [1, 8].
                # But contrib must be <= 7 in 4-bit 2's complement!
                # If pre_res == -8, cannot flip with contrib <= 7. So clamp pre_res to -7..-1 for flipping
                if pre_res == -8:
                    pre_res = -7
                min_contrib_to_flip = -pre_res
                contrib = self.rng.randint(min_contrib_to_flip, 7)
            else:
                # stored_bit == 1: pre_residue must be >= 0: range 0..7
                pre_res = self.rng.randint(0, 7)
                # To cause a flip, contrib must push sum < 0: contrib <= -pre_res - 1
                max_contrib_to_flip = -pre_res - 1
                contrib = self.rng.randint(-8, max_contrib_to_flip)

            exp_old = sign_threshold(pre_res)
            exp_new = sign_threshold(pre_res + contrib)
            assert exp_old == stored_bit, f"Mismatch: exp_old={exp_old} != stored_bit={stored_bit}"

            entries.append(
                WireEntry(
                    dim_idx=dim,
                    pre_residue=pre_res,
                    contrib=contrib,
                    expected_old_bit=exp_old,
                    expected_new_bit=exp_new,
                )
            )

        # Modalities A and B agree with high margins (above theta=128)
        mA = self.rng.randint(140, 220)
        mB = self.rng.randint(140, 220)

        return WirePacket.create(
            source_id=source_id,
            update_id=update_id,
            class_id=class_id,
            sequence=sequence,
            hA=class_id,
            mA=mA,
            hB=class_id,
            mB=mB,
            entries=entries,
        )

    def generate_hand_packet_w2_smallest(self, proto_mem: PrototypeMemory, class_id: int = 0) -> WirePacket:
        """
        Generates the exact hand-built 2-entry packet specified in WEEK_2.md lines 14-21.
        Entry 1: dim 100, residue -3, contrib +5, old_bit 0, new_bit 1
        Entry 2: dim 200, residue +2, contrib -5, old_bit 1, new_bit 0
        """
        # Ensure prototype memory has expected starting bits: dim 100 -> 0, dim 200 -> 1
        proto_mem.set_bit(class_id, 100, 0)
        proto_mem.set_bit(class_id, 200, 1)

        update_id = self.next_update_id
        self.next_update_id += 1
        sequence = self.class_sequences[class_id]
        self.class_sequences[class_id] += 1

        entries = [
            WireEntry(dim_idx=100, pre_residue=-3, contrib=5, expected_old_bit=0, expected_new_bit=1),
            WireEntry(dim_idx=200, pre_residue=2, contrib=-5, expected_old_bit=1, expected_new_bit=0),
        ]

        return WirePacket.create(
            source_id=1,
            update_id=update_id,
            class_id=class_id,
            sequence=sequence,
            hA=class_id,
            mA=180,
            hB=class_id,
            mB=170,
            entries=entries,
        )
