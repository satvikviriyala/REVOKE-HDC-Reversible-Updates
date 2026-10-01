"""
Wire Packet Framing, Validation, Serialization, and Deserialization for REVOKE-HDC.
"""

from dataclasses import dataclass
import struct
from typing import List, Optional, Tuple
from sim.crc16 import compute_packet_crc, verify_packet_crc
from sim.hdc_core import sign_threshold


@dataclass
class WireEntry:
    dim_idx: int          # 12 bits: 0..4095
    pre_residue: int      # 4 bits signed: -8..+7
    contrib: int          # 4 bits signed: -8..+7
    expected_old_bit: int # 1 bit: 0 or 1
    expected_new_bit: int # 1 bit: 0 or 1
    alphabet_overflow: bool = False

    def to_bytes(self) -> bytes:
        # 24-bit word:
        # [11:0]  dim_idx
        # [15:12] pre_residue (4-bit two's complement)
        # [19:16] contrib (4-bit two's complement)
        # [20]    expected_old_bit
        # [21]    expected_new_bit
        # [22]    alphabet_overflow flag (set if |u| > 7 or residue not in -8..7)
        # [23]    reserved (0)
        overflow = self.alphabet_overflow or not (-8 <= self.pre_residue <= 7) or not (-8 <= self.contrib <= 7)
        res_4b = self.pre_residue & 0xF
        cnt_4b = self.contrib & 0xF
        word24 = (
            (self.dim_idx & 0xFFF)
            | (res_4b << 12)
            | (cnt_4b << 16)
            | ((self.expected_old_bit & 1) << 20)
            | ((self.expected_new_bit & 1) << 21)
            | ((1 if overflow else 0) << 22)
        )
        return word24.to_bytes(3, byteorder="little")

    @classmethod
    def from_bytes(cls, b: bytes) -> "WireEntry":
        assert len(b) == 3
        word24 = int.from_bytes(b, byteorder="little")
        dim_idx = word24 & 0xFFF
        res_raw = (word24 >> 12) & 0xF
        cnt_raw = (word24 >> 16) & 0xF
        exp_old = (word24 >> 20) & 1
        exp_new = (word24 >> 21) & 1
        overflow = bool(word24 & (1 << 22))

        # Sign-extend 4-bit values to python int
        res_signed = res_raw if res_raw < 8 else res_raw - 16
        cnt_signed = cnt_raw if cnt_raw < 8 else cnt_raw - 16

        return cls(
            dim_idx=dim_idx,
            pre_residue=res_signed,
            contrib=cnt_signed,
            expected_old_bit=exp_old,
            expected_new_bit=exp_new,
            alphabet_overflow=overflow,
        )


@dataclass
class WirePacket:
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
    entries: List[WireEntry]

    @classmethod
    def create(
        cls,
        source_id: int,
        update_id: int,
        class_id: int,
        sequence: int,
        hA: int,
        mA: int,
        hB: int,
        mB: int,
        entries: List[WireEntry],
        format_ver: int = 0,
    ) -> "WirePacket":
        entry_count = len(entries)
        length = 16 + 3 * entry_count
        pkt = cls(
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
            checksum=0,
            entries=entries,
        )
        # Compute and assign CRC
        raw_pre_crc = pkt.to_bytes(compute_crc=False)
        pkt.checksum = compute_packet_crc(raw_pre_crc)
        return pkt

    def to_bytes(self, compute_crc: bool = True) -> bytes:
        ck = self.checksum if not compute_crc else 0
        header = bytearray(16)
        header[0] = self.source_id & 0xFF
        header[1:3] = self.update_id.to_bytes(2, byteorder="little")
        header[3] = self.class_id & 0xFF
        header[4:6] = self.sequence.to_bytes(2, byteorder="little")
        header[6] = self.hA & 0xFF
        header[7] = self.mA & 0xFF
        header[8] = self.hB & 0xFF
        header[9] = self.mB & 0xFF
        header[10] = self.entry_count & 0xFF
        header[11:13] = self.length.to_bytes(2, byteorder="little")
        header[13] = self.format_ver & 0xFF
        header[14:16] = ck.to_bytes(2, byteorder="little")

        payload = bytearray()
        for e in self.entries:
            payload.extend(e.to_bytes())

        packet_bytes = bytes(header + payload)
        if compute_crc:
            actual_crc = compute_packet_crc(packet_bytes)
            # overwrite bytes 14-15
            packet_bytes = packet_bytes[:14] + actual_crc.to_bytes(2, byteorder="little") + packet_bytes[16:]
        return packet_bytes

    @classmethod
    def from_bytes(cls, raw: bytes) -> "WirePacket":
        if len(raw) < 16:
            raise ValueError(f"Packet too short: {len(raw)} bytes < 16")
        source_id = raw[0]
        update_id = int.from_bytes(raw[1:3], byteorder="little")
        class_id = raw[3]
        sequence = int.from_bytes(raw[4:6], byteorder="little")
        hA = raw[6]
        mA = raw[7]
        hB = raw[8]
        mB = raw[9]
        entry_count = raw[10]
        length = int.from_bytes(raw[11:13], byteorder="little")
        format_ver = raw[13]
        checksum = int.from_bytes(raw[14:16], byteorder="little")

        entries: List[WireEntry] = []
        offset = 16
        for _ in range(entry_count):
            if offset + 3 > len(raw):
                break
            entry_bytes = raw[offset : offset + 3]
            entries.append(WireEntry.from_bytes(entry_bytes))
            offset += 3

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
