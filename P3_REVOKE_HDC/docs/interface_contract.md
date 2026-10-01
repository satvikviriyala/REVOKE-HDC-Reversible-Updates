# Interface and Record Contract - REVOKE-HDC (Week 1 Frozen)

## 1. Normative Architectural Constants

- **Dimension ($D$)**: 4096 bits per class prototype.
- **Classes**: 4 class prototypes (`class_id` low 2 bits $0..3$).
- **Word Width**: 64-bit packed words ($64 \text{ words} \times 64 \text{ bits} = 4096 \text{ bits} = 512 \text{ bytes/class}$).
- **Total Prototype Storage**: $4 \times 512 = 2048 \text{ bytes}$ (2 KiB BRAM).
- **Maximum Affected Dimensions per Update ($F_{max}$)**: 96 entries.
- **Header Width**: 16 bytes.
- **Wire Entry Width**: 3 bytes (24 bits).
- **Persisted Journal Entry Width**: 2 bytes (16 bits).
- **Multi-Byte Integer Endianness**: Little-endian across all fields.
- **Signed Integer Representation**: Two's complement for all signed fields.
- **Threshold Convention**:
  $$\text{sign\_threshold}(x) = \begin{cases} 1 & \text{if } x \ge 0 \\ 0 & \text{if } x < 0 \end{cases}$$
- **Bit Ordering within 64-bit Word**: Little-endian bit ordering.
  - Dimension $d \in [0, 4095]$ maps to:
    $$\text{word\_index} = d \gg 6 \quad (0..63)$$
    $$\text{bit\_index} = d \ \& \ 63 \quad (0..63)$$
    Bit mask: `1ULL << bit_index`.

---

## 2. 16-Byte Wire Packet Header Layout

The packet header is exactly 16 bytes, transmitted little-endian from host to controller:

| Field | Byte Offset | Width | Bits | Type / Encoding | Description / Contract |
|---|:---:|:---:|:---:|---|---|
| `source_id` | 0 | 1 byte | 8 | unsigned int | Identifies sending sensor/modality harness (e.g. 1=vision, 2=IMU). |
| `update_id` | 1-2 | 2 bytes | 16 | uint16_le | Monotonic global identifier; used for exact restoration lookup. |
| `class_id` | 3 | 1 byte | 8 | uint8 | Low 2 bits select prototype ($0..3$); high 6 bits MUST be zero. |
| `sequence` | 4-5 | 2 bytes | 16 | uint16_le | Per-class monotonic sequence count; cross-checked at admission. |
| `hA` | 6 | 1 byte | 8 | uint8 | Modality-A predicted hypothesis label ($0..3$). |
| `mA` | 7 | 1 byte | 8 | uint8 | Modality-A confidence margin ($0..255$). |
| `hB` | 8 | 1 byte | 8 | uint8 | Modality-B predicted hypothesis label ($0..3$). |
| `mB` | 9 | 1 byte | 8 | uint8 | Modality-B confidence margin ($0..255$). |
| `entry_count` ($F$) | 10 | 1 byte | 8 | uint8 | Number of affected-dimension entries ($0 \le F \le 96$). |
| `length` | 11-12 | 2 bytes | 16 | uint16_le | Total wire packet length: $16 + 3F$ bytes. |
| `reserved/format` | 13 | 1 byte | 8 | uint8 | Format version; MUST be `0x00` in frozen build. |
| `checksum` | 14-15 | 2 bytes | 16 | uint16_le | CRC-16/CCITT-FALSE over header (bytes 0-13) and payload. |

### Wire Packet Length Formulation
The 16-byte header explicitly includes the 2-byte checksum at bytes 14-15. With $F$ entries at 3 bytes each:
$$L_{\text{wire}}(F) = 16 + 3F \text{ bytes}$$
- At $F = 0$: $L_{\text{wire}} = 16 \text{ bytes}$.
- At $F = 40$: $L_{\text{wire}} = 16 + 120 = 136 \text{ bytes}$.
- At $F = 96$: $L_{\text{wire}} = 16 + 288 = 304 \text{ bytes}$ (maximum wire packet size).

---

## 3. Per-Entry Wire Payload (3 Bytes / 24 Bits Each)

Each affected dimension contributes one 24-bit entry $E$, repeated $F$ times ($F \le 96$):

```text
 23 22 21 20 19      16 15      12 11                      0
+-----+--+--+----------+----------+-------------------------+
| RSV |N |O |  contrib |  residue |     dimension_index     |
+-----+--+--+----------+----------+-------------------------+
  2b   1b 1b    4b         4b                12b
```

| Subfield | Bits | Width | Encoding | Description |
|---|:---:|:---:|---|---|
| `dimension_index` | $[11:0]$ | 12 bits | unsigned ($0..4095$) | Target dimension in prototype memory. |
| `pre_update_residue` | $[15:12]$ | 4 bits | signed 2's compl ($-8..+7$) | Distance to threshold prior to update. |
| `update_contribution` | $[19:16]$ | 4 bits | signed 2's compl ($-8..+7$) | Value added by this update ($|u| \le 8$, conceptual $+8$ unencodable). |
| `expected_old_bit` | $[20]$ | 1 bit | binary ($0 \text{ or } 1$) | Sender's claim: $\text{sign\_threshold}(pre\_residue)$. |
| `expected_new_bit` | $[21]$ | 1 bit | binary ($0 \text{ or } 1$) | Sender's claim: $\text{sign\_threshold}(pre\_residue + update\_contribution)$. |
| `reserved` | $[23:22]$ | 2 bits | binary (`00`) | Reserved for future format expansion; MUST be zero. |

---

## 4. Persisted Sparse Journal Record (2 Bytes per Entry)

Once admitted, the controller writes a compact journal record to the BRAM ring buffer. The parser discards `update_contribution`, `expected_old_bit`, and `expected_new_bit` because the prior bit is strictly recoverable from `pre_update_residue`.

The persisted journal record reuses the 16-byte header (with `length = 16 + 2F` and updated CRC-16), followed by $F$ 16-bit entries:

```text
 15      12 11                      0
+----------+-------------------------+
|  residue |     dimension_index     |
+----------+-------------------------+
    4b                12b
```

| Subfield | Bits | Width | Encoding | Description |
|---|:---:|:---:|---|---|
| `dimension_index` | $[11:0]$ | 12 bits | unsigned ($0..4095$) | Dimension index to restore. |
| `pre_update_residue` | $[15:12]$ | 4 bits | signed 2's compl ($-8..+7$) | Retained signed pre-threshold residue. |

### Persisted Record Sizing Formula
$$R(F) = 16 + 2F \text{ bytes}$$
- At $F = 40$: $R(40) = 16 + 80 = 96 \text{ bytes}$.
- At $F = 96$: $R(96) = 16 + 192 = 208 \text{ bytes}$ (maximum persisted record size).
- Compared to full 512-byte prototype snapshot: sparse journaling is smaller whenever $16 + 2F < 512 \implies F < 248$.

---

## 5. Outcome Record Layout (12 Bytes)

Every processed update or restoration request generates exactly one 12-byte outcome record:

| Byte Offset | Field | Width | Description |
|:---:|---|:---:|---|
| $0$ | `request_type` & `class_id` | 1 byte | Bit 0: request type ($0=\text{update}, 1=\text{restore}$); Bits $[2:1]$: `class_id` ($0..3$); Bits $[7:3]$: reserved (0). |
| $1$ | `source_id` | 1 byte | Source ID from update packet (0 for restoration). |
| $2-3$ | `update_id` | 2 bytes | uint16_le identifier of request. |
| $4$ | `outcome_code` | 1 byte | Outcome code $0..10$ (low 4 bits). |
| $5-6$ | `slot_id` | 2 bytes | uint16_le allocated Record Index Table slot ($0..1023$, or $0\text{xFFFF}$ if none). |
| $7$ | `affected_count` | 1 byte | Number of dimensions flipped / restored ($F$). |
| $8-11$ | `cycle_timestamp` | 4 bytes | uint32_le PL cycle timestamp when outcome posted. |

---

## 6. Trace Record Layout (8 Bytes)

Exposed through the `TRACE_POP` register (`0x30`) to trace controller lifecycle transitions:

| Byte Offset | Field | Width | Description |
|:---:|---|:---:|---|
| $0-3$ | `cycle_timestamp` | 4 bytes | uint32_le PL cycle clock. |
| $4$ | `event_type` & `class_id` | 1 byte | Bits $[3:0]$: event type (1=ADMIT, 2=REFUSE, 3=JRN_WRITE, 4=COMMIT, 5=RESTORE_LOOKUP, 6=RESTORE_APPLY, 7=RETIRE); Bits $[5:4]$: `class_id`. |
| $5-6$ | `update_id` | 2 bytes | uint16_le update ID. |
| $7$ | `outcome_code` & `cursor` | 1 byte | Bits $[3:0]$: `outcome_code`; Bits $[7:4]$: high bits of dimension cursor. |

---

## 7. CRC-16 Specification

- **Algorithm**: CRC-16/CCITT-FALSE
- **Polynomial**: `0x1021` ($x^{16} + x^{12} + x^5 + 1$)
- **Initial Value**: `0xFFFF`
- **RefIn**: `False`
- **RefOut**: `False`
- **XorOut**: `0x0000`
- **Checksum Calculation**:
  Bytes 14-15 of the 16-byte header are zeroed out. CRC is computed over the entire packet length (header bytes 0-15 with checksum=0, followed by all $F$ entries). The resulting 16-bit integer is written into bytes 14-15 in little-endian format.
