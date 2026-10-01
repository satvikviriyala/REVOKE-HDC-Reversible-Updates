# Outcome / Refusal Table - W1-R1

| Code | Meaning | Prototype changed? | Project-specific trigger |
| --- | --- | --- | --- |
| 0 | accepted | yes | All structural, CRC, alphabet, expected-bit, trust-gate, ordering, stored-bit and capacity checks pass; journal record is durable before prototype commit. |
| 1 | quarantined | no | Packet is structurally valid but hA/hB/class_id agreement or one/both calibrated margin gates fail. |
| 2 | refused - capacity | no | No journal index slot or no safe contiguous ring allocation is available under the no-split wrap rule. |
| 3 | refused - checksum | no | Recomputed CRC-16 does not equal the transmitted/stored checksum. |
| 4 | refused - residue | no | Residue or contribution violates the frozen numeric contract; host-side +8 is also refused because signed 4-bit two's-complement cannot encode it. |
| 5 | refused - stale | no | Recomputed old_bit from pre_update_residue does not equal the currently stored packed prototype bit at that dimension. |
| 6 | refused - duplicate | no | A dimension_index occurs more than once in the same packet. |
| 7 | refused - ordering | no | Admission sequence is not the next per-class sequence, or restoration is requested for a record that is not the active head of its class. |
| 8 | refused - bit-state | no | expected_old_bit/expected_new_bit disagrees with recomputation, or another frozen bit-format invariant (reserved bits/class high bits/length) is malformed and no dedicated format code exists. |
| 9 | restored | yes (reverted) | Requested active class-head record is read once, old bits are reconstructed from retained residues, combined per 64-bit word, applied, then the record is retired. |
| 10 | already-retired | no | Restoration targets an update_id whose index entry is already in RETIRED state; no prototype write occurs. |

## Outcome precedence note

The fixed outcome alphabet contains seven refusal codes (2 through 8), plus accepted, quarantined, restored, and already-retired. R1 uses the deterministic validation precedence documented in `validation_rules.md` so a packet with multiple defects produces exactly one primary outcome.
