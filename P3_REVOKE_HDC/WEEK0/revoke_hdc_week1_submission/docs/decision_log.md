# Week 1 Decision Log - W1-R1

Every Week 1 open item receives either a concrete R1 decision or an explicit evidence dependency with an owner. Values labeled OPEN are not fabricated.

| # | Decision | Status | Recorded answer | Owner |
| --- | --- | --- | --- | --- |
| 1 | Encoder and dataset choice | OPEN - team evidence required | The uploaded Week 1 brief does not name the actual encoder/dataset. Do not fabricate this. Freeze the exact encoder revision and dataset/split in the final team copy. | HDC/ML owner |
| 2 | Residue range and update alphabet check | CONTRACT CLOSED; empirical check open | Residue is signed 4-bit two's-complement [-8,+7]. Contribution is signed 4-bit two's-complement [-8,+7]. The source phrase \|u\|<=8 is interpreted with representability: -8 is encodable; +8 is not. Measure the real encoder contribution distribution before declaring empirical PASS. | HDC/ML owner |
| 3 | Duplicate dimension indices | CONFIRMED | Refuse the whole packet with outcome 6; no partial mutation. | System owner |
| 4 | Entry ordering | DECIDED | Preserve stream order in the record; commit/restoration logic accumulates per-64-bit-word masks so all entries for the same word are combined. | System owner |
| 5 | 64-bit write-mask combining | CONFIRMED | For dimension d: word=d>>6, bit=d&63. Accumulate one mask/value pair per touched word and perform one grouped prototype update per touched word. | RTL owner |
| 6 | theta_A and theta_B calibration | OPEN - empirical | Do not treat 128 as calibrated. Derive thresholds from the chosen encoder/dataset validation split; store final integers in the config and calibration evidence. | HDC/ML owner |
| 7 | Journal allocation | CONFIRMED | Ring-buffer byte store plus record-index table; per-class head pointers enforce reverse commit order. | System owner |
| 8 | Ring wrap behaviour | DECIDED | Records never split across the physical wrap. If fewer than R(F) bytes remain to the ring end, pad/skip to end and allocate at offset 0 after capacity/overlap checks. | RTL owner |
| 9 | Reverse-order restoration | CONFIRMED | Only the current ACTIVE head record of the requested class may transition ACTIVE -> RESTORING. Any older active record is refused_ordering. | System owner |
| 10 | Sparse break-even | CLOSED | 16+2F < 512 iff F<248. F=247 -> 510 B; F=248 -> 512 B. The measured workload F distribution remains empirical work. | Reproducer |
| 11 | PL target clock and packet rate | DECIDED TARGET | 100 MHz PL clock; engineering target >=50,000 accepted/refused packet decisions per second for F<=96. This is a design target, not a Week 1 measured result. | FPGA owner |
| 12 | Journal BRAM capacity | DECIDED CONSERVATIVE | 256 KiB byte ring. With N=1024 and Rmax=208 B, worst-case live payload is 212,992 B, leaving 49,152 B before considering index/trace memories (stored separately). | FPGA owner |
| 13 | Record index depth N | DECIDED | N=1024 live/indexable slots across four classes; slot_id width=ceil(log2(1024))=10 bits. | System owner |
| 14 | Trace buffer depth | DECIDED | 4096 trace entries. Reference trace entry is 16 B, giving 64 KiB; increase only if the actual Section 8 demonstration exceeds 4096 outcomes. | Reproducer |
| 15 | CRC-16 polynomial | DECIDED | CRC-16/CCITT-FALSE: poly=0x1021, init=0xFFFF, refin=false, refout=false, xorout=0x0000. Checksum field is zero while computing CRC, then overwritten with result. | System owner |
| 16 | AXI-Lite base and interconnect | DECIDED PROJECT ALLOCATION | Reserve 0xA0000000-0xA000FFFF for the REVOKE-HDC AXI4-Lite control/status block; connect PS M_AXI_HPM0_FPD -> SmartConnect -> PL AXI4-Lite slave. Vivado Address Editor is authoritative and must match this allocation. | FPGA integration owner |

## Clarifications added by R1

1. **Zero threshold tie:** the supplied file names `sign_threshold` but does not define zero. R1 freezes `x>=0 -> 1` so vectors and RTL are deterministic.
2. **Checksum inclusion:** because the listed 16-byte header already contains a 2-byte checksum, R1 uses wire length `16+3F` rather than double-counting the checksum.
3. **4-bit +8 contradiction:** a signed 4-bit two's-complement field cannot encode +8. R1's actual wire alphabet is `-8..+7`; conceptual +8 is rejected by the host packer.
4. **Journal header wording:** R1 reuses the 16-byte header schema but re-derives journal `length` and `checksum` for the persisted representation, so the stored record can be independently checked.
5. **Generic format errors:** the frozen outcome list has no dedicated format/length refusal. R1 maps frozen bit-format violations to outcome 8 and records that mapping here rather than silently creating a twelfth code.

## External evidence still needed for a fully measured Green verdict

- exact encoder name/version and dataset/split;
- measured per-dimension contribution distribution demonstrating compatibility with the frozen alphabet;
- calibrated `theta_A` and `theta_B` with method and validation statistics;
- original Git source commit/build ID;
- independent reviewer name/countersignature;
- exact PROJECT_PLAN Section 3.3 state names if they differ from the R1 controller labels.
