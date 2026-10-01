"""
BRAM Journal Ring Buffer and Record Index Table for REVOKE-HDC.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional, Tuple
from sim.crc16 import compute_packet_crc


class SlotState(IntEnum):
    FREE = 0
    ACTIVE = 1
    RESTORING = 2
    RETIRED = 3


@dataclass
class JournalEntry:
    dim_idx: int     # 12 bits: 0..4095
    pre_residue: int # 4 bits signed: -8..+7

    def to_bytes(self) -> bytes:
        # 16-bit word: [11:0] dim_idx, [15:12] residue
        res_4b = self.pre_residue & 0xF
        word16 = (self.dim_idx & 0xFFF) | (res_4b << 12)
        return word16.to_bytes(2, byteorder="little")

    @classmethod
    def from_bytes(cls, b: bytes) -> "JournalEntry":
        assert len(b) == 2
        word16 = int.from_bytes(b, byteorder="little")
        dim_idx = word16 & 0xFFF
        res_raw = (word16 >> 12) & 0xF
        res_signed = res_raw if res_raw < 8 else res_raw - 16
        return cls(dim_idx=dim_idx, pre_residue=res_signed)


@dataclass
class PersistedRecord:
    source_id: int
    update_id: int
    class_id: int
    sequence: int
    hA: int
    mA: int
    hB: int
    mB: int
    entry_count: int
    length: int
    format_ver: int
    checksum: int
    entries: List[JournalEntry]

    @classmethod
    def from_wire(cls, wire_header_bytes: bytes, entries: List[JournalEntry]) -> "PersistedRecord":
        assert len(wire_header_bytes) == 16
        entry_count = len(entries)
        length = 16 + 2 * entry_count
        hdr = bytearray(wire_header_bytes)
        # Update entry count and length
        hdr[10] = entry_count & 0xFF
        hdr[11:13] = length.to_bytes(2, byteorder="little")
        hdr[14:16] = b"\x00\x00"

        # Construct raw payload to compute CRC
        payload = bytearray()
        for e in entries:
            payload.extend(e.to_bytes())

        full_raw = bytes(hdr + payload)
        crc = compute_packet_crc(full_raw)

        return cls(
            source_id=hdr[0],
            update_id=int.from_bytes(hdr[1:3], byteorder="little"),
            class_id=hdr[3] & 0x3,
            sequence=int.from_bytes(hdr[4:6], byteorder="little"),
            hA=hdr[6],
            mA=hdr[7],
            hB=hdr[8],
            mB=hdr[9],
            entry_count=entry_count,
            length=length,
            format_ver=hdr[13],
            checksum=crc,
            entries=entries,
        )

    def to_bytes(self) -> bytes:
        hdr = bytearray(16)
        hdr[0] = self.source_id & 0xFF
        hdr[1:3] = self.update_id.to_bytes(2, byteorder="little")
        hdr[3] = self.class_id & 0xFF
        hdr[4:6] = self.sequence.to_bytes(2, byteorder="little")
        hdr[6] = self.hA & 0xFF
        hdr[7] = self.mA & 0xFF
        hdr[8] = self.hB & 0xFF
        hdr[9] = self.mB & 0xFF
        hdr[10] = self.entry_count & 0xFF
        hdr[11:13] = self.length.to_bytes(2, byteorder="little")
        hdr[13] = self.format_ver & 0xFF
        hdr[14:16] = self.checksum.to_bytes(2, byteorder="little")

        payload = bytearray()
        for e in self.entries:
            payload.extend(e.to_bytes())

        return bytes(hdr + payload)

    @classmethod
    def from_bytes(cls, raw: bytes) -> "PersistedRecord":
        assert len(raw) >= 16
        source_id = raw[0]
        update_id = int.from_bytes(raw[1:3], byteorder="little")
        class_id = raw[3] & 0x3
        sequence = int.from_bytes(raw[4:6], byteorder="little")
        hA = raw[6]
        mA = raw[7]
        hB = raw[8]
        mB = raw[9]
        entry_count = raw[10]
        length = int.from_bytes(raw[11:13], byteorder="little")
        format_ver = raw[13]
        checksum = int.from_bytes(raw[14:16], byteorder="little")

        entries: List[JournalEntry] = []
        offset = 16
        for _ in range(entry_count):
            if offset + 2 > len(raw):
                break
            entries.append(JournalEntry.from_bytes(raw[offset : offset + 2]))
            offset += 2

        return cls(
            source_id=source_id,
            update_id=update_id,
            class_id=class_id,
            sequence=sequence,
            hA=hA,
            mA=mA,
            hB=hB,
            mB=mB,
            entry_count=entry_count,
            length=length,
            format_ver=format_ver,
            checksum=checksum,
            entries=entries,
        )


class JournalRing:
    """
    Append-only BRAM ring buffer with pad-to-end ring wrap.
    Capacity: 256 KiB (262,144 bytes).
    """

    def __init__(self, capacity_bytes: int = 262144):
        self.capacity = capacity_bytes
        self.buffer = bytearray(capacity_bytes)
        self.head_ptr: int = 0
        self.tail_ptr: int = 0
        self.free_bytes: int = capacity_bytes

    def can_allocate(self, record_len: int) -> bool:
        if record_len > self.free_bytes:
            return False
        # Under pad-to-end rule:
        rem_end = self.capacity - self.head_ptr
        if rem_end < record_len:
            # Need to pad to end and wrap to 0. Required space is rem_end + record_len
            return self.free_bytes >= (rem_end + record_len)
        return True

    def allocate_and_write(self, record: PersistedRecord) -> int:
        """
        Appends record to ring buffer.
        Returns the ring offset where the record was written.
        """
        rec_bytes = record.to_bytes()
        rec_len = len(rec_bytes)
        if not self.can_allocate(rec_len):
            raise MemoryError("Journal capacity full")

        rem_end = self.capacity - self.head_ptr
        if rem_end < rec_len:
            # Pad to end
            self.free_bytes -= rem_end
            self.head_ptr = 0

        write_offset = self.head_ptr
        self.buffer[write_offset : write_offset + rec_len] = rec_bytes
        self.head_ptr = (self.head_ptr + rec_len) % self.capacity
        self.free_bytes -= rec_len
        return write_offset

    def read_record(self, ring_offset: int, length: int) -> PersistedRecord:
        raw = bytes(self.buffer[ring_offset : ring_offset + length])
        return PersistedRecord.from_bytes(raw)


@dataclass
class IndexSlot:
    slot_id: int
    state: SlotState = SlotState.FREE
    class_id: int = 0
    source_id: int = 0
    update_id: int = 0
    sequence: int = 0
    ring_offset: int = 0
    length: int = 0
    prev_slot_id: int = -1
    expected_new_bits: Optional[Dict[int, int]] = None


class RecordIndexTable:
    """
    Fixed-depth table of N=1024 slots with per-class head pointers.
    Enforces reverse-commit ordering per class.
    """

    def __init__(self, depth: int = 1024):
        self.depth = depth
        self.slots: List[IndexSlot] = [IndexSlot(slot_id=i) for i in range(depth)]
        self.class_head_slot: List[int] = [-1, -1, -1, -1]
        self.class_next_seq: List[int] = [0, 0, 0, 0]
        self.next_free_slot: int = 0

    def has_free_slot(self) -> bool:
        for s in self.slots:
            if s.state == SlotState.FREE:
                return True
        return False

    def allocate_slot(
        self,
        class_id: int,
        source_id: int,
        update_id: int,
        sequence: int,
        ring_offset: int,
        length: int,
        expected_new_bits: Dict[int, int],
    ) -> int:
        for i in range(self.depth):
            idx = (self.next_free_slot + i) % self.depth
            if self.slots[idx].state == SlotState.FREE:
                self.next_free_slot = (idx + 1) % self.depth
                slot = self.slots[idx]
                slot.state = SlotState.ACTIVE
                slot.class_id = class_id
                slot.source_id = source_id
                slot.update_id = update_id
                slot.sequence = sequence
                slot.ring_offset = ring_offset
                slot.length = length
                slot.prev_slot_id = self.class_head_slot[class_id]
                slot.expected_new_bits = dict(expected_new_bits)

                # Update class head
                self.class_head_slot[class_id] = idx
                self.class_next_seq[class_id] = sequence + 1
                return idx

        raise IndexError("Record Index Table full")

    def find_slot_by_update_id(self, class_id: int, update_id: int) -> int:
        for s in self.slots:
            if s.state != SlotState.FREE and s.class_id == class_id and s.update_id == update_id:
                return s.slot_id
        return -1

    def transition_state(self, slot_id: int, target_state: SlotState):
        slot = self.slots[slot_id]
        current = slot.state
        # Enforce Invariant 4: ACTIVE -> RESTORING -> RETIRED
        if current == SlotState.ACTIVE and target_state == SlotState.RESTORING:
            slot.state = SlotState.RESTORING
        elif current == SlotState.RESTORING and target_state == SlotState.RETIRED:
            slot.state = SlotState.RETIRED
        else:
            raise ValueError(f"Illegal slot state transition from {current} to {target_state}")

    def retire_head(self, class_id: int, slot_id: int):
        assert self.class_head_slot[class_id] == slot_id
        slot = self.slots[slot_id]
        assert slot.state == SlotState.RESTORING
        slot.state = SlotState.RETIRED
        self.class_head_slot[class_id] = slot.prev_slot_id
