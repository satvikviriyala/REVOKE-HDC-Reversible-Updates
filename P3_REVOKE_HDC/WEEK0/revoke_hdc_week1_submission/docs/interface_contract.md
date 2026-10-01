# Interface and Record Contract - W1-R1

## 1. Normative constants

- Dimensions per packed prototype: 4096 bits.
- Classes/prototypes: 4 (`class_id` low two bits `0..3`).
- Maximum affected dimensions per packet: `F_max = 96`.
- Header width: 16 bytes.
- Wire entry width: 3 bytes.
- Journal entry width: 2 bytes.
- Multi-byte integer byte order in R1: little-endian.
- Signed 4-bit values: two's-complement.
- Threshold convention: `sign_threshold(x) = 1 if x >= 0 else 0`.

## 2. 16-byte header byte layout

| Field | Byte offset | Bytes | Bits | R1 rule |
| --- | --- | --- | --- | --- |
| source_id | 0 | 1 | 8 | sending modality/harness ID |
| update_id | 1-2 | 2 | 16 | global monotonic update identifier; little-endian |
| class_id | 3 | 1 | 8 | low 2 bits select prototype 0..3; high 6 bits must be zero |
| sequence | 4-5 | 2 | 16 | per-class monotonic sequence; little-endian |
| hA | 6 | 1 | 8 | modality-A hypothesis label |
| mA | 7 | 1 | 8 | modality-A margin |
| hB | 8 | 1 | 8 | modality-B hypothesis label |
| mB | 9 | 1 | 8 | modality-B margin |
| entry_count (F) | 10 | 1 | 8 | 0..96 accepted |
| length | 11-12 | 2 | 16 | wire: 16+3F; journal: 16+2F; little-endian |
| reserved/format | 13 | 1 | 8 | must be 0 in frozen build |
| checksum | 14-15 | 2 | 16 | CRC-16/CCITT-FALSE; little-endian field |

### Length clarification

The 16-byte field list already contains the 2-byte checksum at bytes 14-15. Therefore the normative R1 wire size is:

`L_wire(F) = 16 + 3F` bytes.

For a journal record the same 16-byte **layout** is reused, with `length = 16 + 2F` and the checksum recomputed over the journal representation. This is a deliberate clarification of the phrase "reuses the 16-byte header unchanged": R1 interprets *unchanged* as unchanged schema, not necessarily unchanged `length/checksum` values.

## 3. Wire entry, 24 bits

Pack a little-endian 24-bit word `E`:

- `E[11:0]  = dimension_index` (`0..4095`)
- `E[15:12] = pre_update_residue` (signed 4-bit two's complement)
- `E[19:16] = update_contribution` (signed 4-bit two's complement)
- `E[20]    = expected_old_bit`
- `E[21]    = expected_new_bit`
- `E[23:22] = 0` (reserved)

The encoded contribution alphabet is exactly `-8..+7`. A host-side integer `+8` satisfies the magnitude phrase `|u|<=8` but cannot be represented in four signed two's-complement bits; R1 therefore rejects it before wire packing.

## 4. Persisted journal entry, 16 bits

Pack a little-endian 16-bit word `J`:

- `J[11:0]  = dimension_index`
- `J[15:12] = pre_update_residue` (signed 4-bit two's complement)

No update contribution or expected bits are retained after validation. Restoration computes the prior packed bit from the retained residue.

## 5. CRC-16

R1 uses CRC-16/CCITT-FALSE:

- polynomial `0x1021`
- init `0xFFFF`
- refin `false`
- refout `false`
- xorout `0x0000`

For computation, bytes 14-15 of the header are set to zero, the CRC is evaluated over the entire current representation (wire header + wire entries, or journal header + journal entries), then the checksum field is overwritten by the 16-bit result. Validation repeats the same zero-and-recompute operation and compares values.

## 6. Trust gate

A structurally valid packet is eligible for journaling only when:

`hA == hB == class_id`, `mA >= theta_A`, and `mB >= theta_B`.

Failure of this trust gate produces `quarantined` (outcome 1), not a prototype mutation.

## 7. Atomicity rule

For an accepted update, the journal record must become durable before any packed prototype bit changes. Any refusal/quarantine produces no prototype write. Restoration marks the active class-head record `RESTORING`, applies all reconstructed old bits, then retires the record exactly once.
