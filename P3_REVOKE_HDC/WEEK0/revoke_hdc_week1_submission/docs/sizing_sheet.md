# Sparse Record Sizing Sheet - W1-R1

## Core formulas

Packed prototype size: `4096 bits / 8 = 512 bytes`.

Wire packet size (R1 clarification):

`L_wire(F) = 16 + 3F` bytes.

Persisted journal record size:

`R(F) = 16 + 2F` bytes.

Sparse storage is strictly smaller than a full 512-byte snapshot when:

`16 + 2F < 512`

`2F < 496`

`F < 248`.

Therefore the largest integer F that is strictly smaller is `F=247`, producing `510 B`; `F=248` produces exactly `512 B` and is not a strict win.

| F | Wire bytes 16+3F | Journal bytes 16+2F | Bytes saved vs 512 | Strictly sparse? | Scope |
| --- | --- | --- | --- | --- | --- |
| 0 | 16 | 16 | 496 | yes | supported |
| 1 | 19 | 18 | 494 | yes | supported |
| 40 | 136 | 96 | 416 | yes | supported |
| 96 | 304 | 208 | 304 | yes | supported |
| 247 | 757 | 510 | 2 | yes | theoretical break-even only; exceeds frozen packet Fmax=96 |
| 248 | 760 | 512 | 0 | equal | theoretical break-even only; exceeds frozen packet Fmax=96 |

## Required hand calculations

- `F=40`: `16 + 2*40 = 16 + 80 = 96 bytes`.
- `F=96`: `16 + 2*96 = 16 + 192 = 208 bytes`.
- `F=247`: `16 + 494 = 510 bytes < 512`.
- `F=248`: `16 + 496 = 512 bytes`, so not strictly smaller.

Because the frozen packet uses only `F<=96`, the maximum supported journal record in this Week 1 contract is **208 bytes**. The theoretical `F=247/248` rows exist only to prove the break-even algebra requested by the brief.

## Journal capacity decision

R1 selects a 256 KiB (`262,144 B`) ring and `N=1024` index slots.

Worst-case live journal payload at the frozen maximum record size:

`1024 * 208 = 212,992 bytes`.

Raw ring headroom after 1024 maximum-size records:

`262,144 - 212,992 = 49,152 bytes` (23.1% over worst-case live payload).

The ring could physically hold `floor(262,144 / 208) = 1260` maximum-size records in ideal packing, so the `N=1024` index depth is the deliberate live-record limit rather than byte capacity.

### KV260 resource sanity check

The AMD KV260 datasheet lists 144 Block RAM blocks. A 256 KiB journal requires about `56.9` 36-Kib BRAM equivalents if implemented purely in BRAM. A reference 4096x16-byte trace is 64 KiB and a reference 1024x16-byte index is 16 KiB; together with the journal, the approximate memory payload is `336 KiB`, or `74.7` 36-Kib equivalents before synthesis overhead. This is a sizing sanity check, not a post-synthesis utilization claim.

Official board reference: AMD Kria KV260 Data Sheet DS986 / UG1089.
