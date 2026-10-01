"""
CRC-16/CCITT-FALSE Implementation for REVOKE-HDC.

Parameters:
- Polynomial: 0x1021 (x^16 + x^12 + x^5 + 1)
- Initial value: 0xFFFF
- RefIn: False
- RefOut: False
- XorOut: 0x0000
"""

def crc16_ccitt_false(data: bytes, init: int = 0xFFFF) -> int:
    crc = init
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def compute_packet_crc(packet_bytes: bytes) -> int:
    """
    Computes CRC-16 over packet bytes where bytes 14-15 (checksum field) are zeroed.
    """
    if len(packet_bytes) < 16:
        raise ValueError("Packet must be at least 16 bytes")
    # Replace checksum bytes at [14:16] with zeros
    zeroed = packet_bytes[:14] + b"\x00\x00" + packet_bytes[16:]
    return crc16_ccitt_false(zeroed)


def verify_packet_crc(packet_bytes: bytes) -> bool:
    """
    Verifies CRC-16 of packet.
    """
    if len(packet_bytes) < 16:
        return False
    expected_crc = int.from_bytes(packet_bytes[14:16], byteorder="little")
    computed_crc = compute_packet_crc(packet_bytes)
    return expected_crc == computed_crc
