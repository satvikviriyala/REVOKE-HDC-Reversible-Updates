# Packet Validation and Restoration Equations - W1-R1

## 1. Signed decode

For a 4-bit nibble `n` in `0..15`, two's-complement decode is:

`decode4(n) = n` for `0 <= n <= 7`, otherwise `n - 16` for `8 <= n <= 15`.

Thus both `pre_update_residue` and wire-encoded `update_contribution` decode to `[-8,+7]`.

## 2. Threshold equations

R1 freezes the zero tie as positive:

`sign_threshold(x) = 1 when x >= 0; 0 when x < 0`.

For each entry:

`r = pre_update_residue`

`u = update_contribution`

`old_bit_calc = sign_threshold(r)`

`sum = r + u`

`new_bit_calc = sign_threshold(sum)`

The exact arithmetic range of the sum is `[-16,+14]`, so RTL must use at least **5 signed bits** for `r+u`; doing this in a 4-bit adder would overflow and can invert the decision around zero.

## 3. Expected-bit checks

The sender-provided bits must satisfy:

`expected_old_bit == old_bit_calc`

`expected_new_bit == new_bit_calc`

A mismatch is `refused - bit-state` (8).

After that, admission compares the recomputed old bit with the actual packed prototype bit:

`old_bit_calc == prototype[class_id][dimension_index]`

A mismatch is `refused - stale` (5). This distinction prevents a malformed sender expectation from being confused with a genuinely stale snapshot.

## 4. Deterministic validation precedence

R1 uses the following outcome precedence so a malformed packet cannot map to different codes depending on implementation timing:

1. Framing present and complete; checksum recomputation. CRC mismatch -> code 3.
2. Frozen structural invariants: `class_id` high bits zero, `class_id<=3`, `F<=96`, length equation, header/entry reserved bits zero. Structural bit-format mismatch -> code 8.
3. Numeric alphabet/range check. Non-encodable/invalid residue/contribution -> code 4.
4. Duplicate dimension detection -> code 6.
5. Expected old/new-bit recomputation -> code 8.
6. Trust gate `hA==hB==class_id` and margins -> quarantine code 1.
7. Per-class sequence check -> code 7.
8. Current packed prototype old-bit check -> code 5.
9. Journal slot/ring capacity -> code 2.
10. Journal write + checksum; only after durable record, apply combined word writes -> code 0.

No validation failure before step 10 may modify the packed prototype.

## 5. Per-class ordering

Admission accepts only the next expected 16-bit per-class sequence. Numeric wrap is modulo `2^16`, but the record index chain, not numeric comparison alone, is authoritative for restoration order.

Each class has a head pointer to its newest ACTIVE record. Restoration of any older ACTIVE record is refused with code 7. Repeating restoration of a record still represented by a RETIRED index tombstone returns code 10.

## 6. 64-bit write-mask combining

For each affected dimension `d`:

`word_index = d >> 6` (range `0..63`)

`bit_index = d & 63` (range `0..63`)

For update commit, group all entries touching the same 64-bit word and produce one mask/value operation for that word. Duplicate dimensions are already forbidden, so no bit position is assigned twice.

For restoration, derive `old_bit_calc` from each retained residue and accumulate:

`mask[word] |= 1 << bit_index`

`value[word] = (value[word] & ~(1 << bit_index)) | (old_bit_calc << bit_index)`

Then restore the word atomically under the mask.

## 7. Why restoration is exact for the packed bit but not the hidden count

The journal retains the residue `r`, so it can always recompute the **old packed prototype bit** `sign_threshold(r)`. It does not retain the original full signed hidden count, so it cannot reconstruct that hidden integer. This is intentional: the reversible object is the packed prototype bit-state, not Arm A's full count state.
