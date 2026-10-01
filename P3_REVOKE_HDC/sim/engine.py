"""
Complete REVOKE-HDC Simulation Engine and Controller Implementation.
Implements the exact state machine, admission gate, write-ahead journaling,
masked prototype RAM commits, reverse-order restoration, and invariant auditing.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional, Tuple
from sim.crc16 import verify_packet_crc
from sim.hdc_core import PrototypeMemory, sign_threshold
from sim.journal import (
    IndexSlot,
    JournalEntry,
    JournalRing,
    PersistedRecord,
    RecordIndexTable,
    SlotState,
)
from sim.packet import WireEntry, WirePacket


class OutcomeCode(IntEnum):
    ACCEPTED = 0
    QUARANTINED = 1
    REFUSED_CAPACITY = 2
    REFUSED_CHECKSUM = 3
    REFUSED_RESIDUE = 4
    REFUSED_STALE = 5
    REFUSED_DUPLICATE = 6
    REFUSED_ORDERING = 7
    REFUSED_BIT_STATE = 8
    RESTORED = 9
    ALREADY_RETIRED = 10


@dataclass
class TraceRecord:
    cycle_timestamp: int
    event_type: str
    class_id: int
    update_id: int
    outcome_code: int
    cursor: int = 0


class RevokeHdcEngine:
    """
    Bit-true REVOKE-HDC Engine coordinating:
    - 4096-bit word-packed Prototype RAM per class
    - 256 KiB Append-Only BRAM Journal Ring
    - 1024-slot Record Index Table
    - Centralized Admission and Commit/Restore Controller
    - AXI-Lite Status Registers and Trace Buffer
    """

    def __init__(
        self,
        seed: int = 0x20261001,
        theta_A: int = 128,
        theta_B: int = 128,
        journal_capacity_bytes: int = 262144,
        index_depth: int = 1024,
    ):
        self.proto_mem = PrototypeMemory(seed=seed)
        self.journal_ring = JournalRing(capacity_bytes=journal_capacity_bytes)
        self.index_table = RecordIndexTable(depth=index_depth)

        # Configurable admission thresholds
        self.theta_A = theta_A
        self.theta_B = theta_B

        # AXI-Lite Accessible Registers (Section 4.6)
        self.last_outcome_code: int = 0
        self.last_update_id: int = 0
        self.update_counter: int = 0
        self.restore_counter: int = 0
        self.refused_counter: int = 0
        self.cycle_clock: int = 0

        # Trace buffer (Section 4.4)
        self.trace_buffer: List[TraceRecord] = []
        self.max_trace_depth: int = 512

    def _log_trace(self, event_type: str, class_id: int, update_id: int, outcome_code: int, cursor: int = 0):
        self.cycle_clock += 10
        rec = TraceRecord(
            cycle_timestamp=self.cycle_clock,
            event_type=event_type,
            class_id=class_id,
            update_id=update_id,
            outcome_code=outcome_code,
            cursor=cursor,
        )
        self.trace_buffer.append(rec)
        if len(self.trace_buffer) > self.max_trace_depth:
            self.trace_buffer.pop(0)

    def process_update_packet(self, raw_bytes: bytes) -> int:
        """
        Parses, validates, journals, and commits an incoming wire packet.
        Returns the resulting OutcomeCode (0..8).
        """
        self.cycle_clock += 5

        # Check 1: Structural minimum length and framing
        if len(raw_bytes) < 16:
            self._refuse(0, 0, OutcomeCode.REFUSED_BIT_STATE)
            return int(OutcomeCode.REFUSED_BIT_STATE)

        source_id = raw_bytes[0]
        update_id = int.from_bytes(raw_bytes[1:3], byteorder="little")
        class_id_raw = raw_bytes[3]
        class_id = class_id_raw & 0x3
        sequence = int.from_bytes(raw_bytes[4:6], byteorder="little")
        hA = raw_bytes[6]
        mA = raw_bytes[7]
        hB = raw_bytes[8]
        mB = raw_bytes[9]
        entry_count = raw_bytes[10]
        declared_length = int.from_bytes(raw_bytes[11:13], byteorder="little")
        format_ver = raw_bytes[13]

        expected_wire_length = 16 + 3 * entry_count
        if (
            len(raw_bytes) != declared_length
            or declared_length != expected_wire_length
            or entry_count > 96
            or format_ver != 0
            or (class_id_raw & ~0x3) != 0
        ):
            self._refuse(class_id, update_id, OutcomeCode.REFUSED_BIT_STATE)
            return int(OutcomeCode.REFUSED_BIT_STATE)

        # Check 2: CRC-16 Checksum
        if not verify_packet_crc(raw_bytes):
            self._refuse(class_id, update_id, OutcomeCode.REFUSED_CHECKSUM)
            return int(OutcomeCode.REFUSED_CHECKSUM)

        # Parse entries
        entries: List[WireEntry] = []
        seen_dims = set()
        offset = 16
        for _ in range(entry_count):
            e = WireEntry.from_bytes(raw_bytes[offset : offset + 3])
            # Check 3: Duplicate dimension indices within packet
            if e.dim_idx in seen_dims:
                self._refuse(class_id, update_id, OutcomeCode.REFUSED_DUPLICATE)
                return int(OutcomeCode.REFUSED_DUPLICATE)
            seen_dims.add(e.dim_idx)

            # Check 4: Alphabet range bounds (-8..+7) and conceptual +8 overflow
            if e.alphabet_overflow or not (-8 <= e.pre_residue <= 7) or not (-8 <= e.contrib <= 7):
                self._refuse(class_id, update_id, OutcomeCode.REFUSED_RESIDUE)
                return int(OutcomeCode.REFUSED_RESIDUE)

            # Check bit claims against recomputed equations
            expected_old = sign_threshold(e.pre_residue)
            expected_new = sign_threshold(e.pre_residue + e.contrib)
            if e.expected_old_bit != expected_old or e.expected_new_bit != expected_new:
                self._refuse(class_id, update_id, OutcomeCode.REFUSED_BIT_STATE)
                return int(OutcomeCode.REFUSED_BIT_STATE)

            entries.append(e)
            offset += 3

        # Check 5: Multi-modal agreement and margin trust gate
        if not (hA == hB == class_id) or (mA < self.theta_A) or (mB < self.theta_B):
            self._refuse(class_id, update_id, OutcomeCode.QUARANTINED)
            return int(OutcomeCode.QUARANTINED)

        # Check 6: Monotonic sequence count per class
        expected_seq = self.index_table.class_next_seq[class_id]
        if sequence != expected_seq:
            self._refuse(class_id, update_id, OutcomeCode.REFUSED_ORDERING)
            return int(OutcomeCode.REFUSED_ORDERING)

        # Check 7: Journal capacity available
        required_journal_bytes = 16 + 2 * entry_count
        if not self.journal_ring.can_allocate(required_journal_bytes) or not self.index_table.has_free_slot():
            self._refuse(class_id, update_id, OutcomeCode.REFUSED_CAPACITY)
            return int(OutcomeCode.REFUSED_CAPACITY)

        # Check 8: Stored prototype bits match pre-update expectations (stale check)
        for e in entries:
            stored_b = self.proto_mem.get_bit(class_id, e.dim_idx)
            if stored_b != e.expected_old_bit:
                self._refuse(class_id, update_id, OutcomeCode.REFUSED_STALE)
                return int(OutcomeCode.REFUSED_STALE)

        # ALL CHECKS PASS -> COMMIT PIPELINE
        # Step A: Write persisted journal record (durable before commit)
        journal_entries = [JournalEntry(dim_idx=e.dim_idx, pre_residue=e.pre_residue) for e in entries]
        persisted_rec = PersistedRecord.from_wire(raw_bytes[:16], journal_entries)
        ring_offset = self.journal_ring.allocate_and_write(persisted_rec)

        # Step B: Allocate Record Index Table slot (ACTIVE)
        exp_new_map = {e.dim_idx: e.expected_new_bit for e in entries}
        slot_id = self.index_table.allocate_slot(
            class_id=class_id,
            source_id=source_id,
            update_id=update_id,
            sequence=sequence,
            ring_offset=ring_offset,
            length=required_journal_bytes,
            expected_new_bits=exp_new_map,
        )

        # Step C: Commit masked prototype words
        updates_to_apply = [(e.dim_idx, e.expected_new_bit) for e in entries]
        self.proto_mem.apply_masked_update(class_id, updates_to_apply)

        # Post accepted outcome
        self.last_outcome_code = int(OutcomeCode.ACCEPTED)
        self.last_update_id = update_id
        self.update_counter += 1
        self._log_trace("COMMIT", class_id, update_id, int(OutcomeCode.ACCEPTED))
        return int(OutcomeCode.ACCEPTED)

    def process_restoration_request(self, class_id: int, update_id: int) -> int:
        """
        Processes a reverse-order restoration request for (class_id, update_id).
        Returns the resulting OutcomeCode (7, 8, 9, 10).
        """
        self.cycle_clock += 5

        # Step 1: Look up slot
        slot_id = self.index_table.find_slot_by_update_id(class_id, update_id)
        if slot_id == -1:
            self._refuse(class_id, update_id, OutcomeCode.REFUSED_ORDERING)
            return int(OutcomeCode.REFUSED_ORDERING)

        slot = self.index_table.slots[slot_id]

        # Step 2: Check for already retired
        if slot.state == SlotState.RETIRED:
            self.last_outcome_code = int(OutcomeCode.ALREADY_RETIRED)
            self.last_update_id = update_id
            self._log_trace("RESTORE_LOOKUP", class_id, update_id, int(OutcomeCode.ALREADY_RETIRED))
            return int(OutcomeCode.ALREADY_RETIRED)

        if slot.state != SlotState.ACTIVE:
            self._refuse(class_id, update_id, OutcomeCode.REFUSED_ORDERING)
            return int(OutcomeCode.REFUSED_ORDERING)

        # Step 3: Check reverse commit order (must be current head of class chain)
        if slot_id != self.index_table.class_head_slot[class_id]:
            self._refuse(class_id, update_id, OutcomeCode.REFUSED_ORDERING)
            return int(OutcomeCode.REFUSED_ORDERING)

        # Step 4: Check that current prototype bits match expected post-update bits
        for dim, exp_new in slot.expected_new_bits.items():
            stored_b = self.proto_mem.get_bit(class_id, dim)
            if stored_b != exp_new:
                self._refuse(class_id, update_id, OutcomeCode.REFUSED_BIT_STATE)
                return int(OutcomeCode.REFUSED_BIT_STATE)

        # ALL RESTORATION CHECKS PASS -> RESTORE PIPELINE
        # Transition: ACTIVE -> RESTORING
        self.index_table.transition_state(slot_id, SlotState.RESTORING)

        # Read persisted record from journal ring
        persisted_rec = self.journal_ring.read_record(slot.ring_offset, slot.length)

        # Recompute prior bits as sign_threshold(pre_residue)
        restored_pairs = []
        for e in persisted_rec.entries:
            restored_b = sign_threshold(e.pre_residue)
            restored_pairs.append((e.dim_idx, restored_b))

        # Commit restored masked words to prototype memory
        self.proto_mem.apply_masked_update(class_id, restored_pairs)

        # Transition: RESTORING -> RETIRED and advance class head
        self.index_table.retire_head(class_id, slot_id)

        self.last_outcome_code = int(OutcomeCode.RESTORED)
        self.last_update_id = update_id
        self.restore_counter += 1
        self._log_trace("RETIRE", class_id, update_id, int(OutcomeCode.RESTORED))
        return int(OutcomeCode.RESTORED)

    def _refuse(self, class_id: int, update_id: int, code: OutcomeCode):
        self.last_outcome_code = int(code)
        self.last_update_id = update_id
        self.refused_counter += 1
        self._log_trace("REFUSE", class_id, update_id, int(code))
