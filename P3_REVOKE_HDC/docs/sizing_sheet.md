# Sizing Sheet: Wire Packets, Sparse Records and Break-Even Analysis

## 1. Memory Formulations & Break-Even Derivation

### Formulations
1. **Wire Packet Length**:
   $$L_{\text{wire}}(F) = 16 + 3F \text{ bytes}$$
   - 16-byte header (including 2-byte CRC-16 checksum)
   - $F$ entries at 3 bytes each (12b dimension index, 4b signed residue, 4b signed contribution, 1b old_bit, 1b new_bit, 2b reserved)
2. **Persisted Sparse Journal Record**:
   $$R(F) = 16 + 2F \text{ bytes}$$
   - 16-byte header (reused schema, updated length and CRC-16)
   - $F$ entries at 2 bytes each (12b dimension index, 4b signed residue)
3. **Full Prototype Snapshot (Arm C Baseline)**:
   $$S_{\text{snapshot}} = 512 \text{ bytes}$$
   - 4096 dimensions $\times$ 1 bit/dim = 512 bytes per class

### Mathematical Break-Even Condition
Sparse journaling uses strictly less storage than a complete prototype snapshot if and only if:
$$R(F) < S_{\text{snapshot}}$$
$$16 + 2F < 512$$
$$2F < 496$$
$$F < 248$$

- At $F = 247$: $R(247) = 16 + 2 \times 247 = 510 \text{ bytes}$ ($< 512 \text{ bytes}$, sparse is smaller).
- At $F = 248$: $R(248) = 16 + 2 \times 248 = 512 \text{ bytes}$ (equal to snapshot, zero benefit).
- At $F > 248$: sparse journaling uses more memory than a snapshot.

Since the frozen cohort configuration enforces a maximum packet size of $F_{\max} = 96$, **REVOKE-HDC operates exclusively in the range $F \in [0, 96] \ll 248$**, where sparse records achieve massive memory savings.

---

## 2. Comprehensive Sizing Reference Table

| $F$ (Affected Dims) | Wire Length ($16 + 3F$) | Journal Record ($16 + 2F$) | Snapshot Size | Memory Saved vs Snapshot | Context / Milestone |
|:---:|:---:|:---:|:---:|:---:|---|
| **0** | 16 bytes | 16 bytes | 512 bytes | 496 bytes (96.9%) | Zero-flip heartbeat / metadata packet |
| **10** | 46 bytes | 36 bytes | 512 bytes | 476 bytes (93.0%) | Minor boundary adjustment |
| **25** | 91 bytes | 66 bytes | 512 bytes | 446 bytes (87.1%) | Small single-feature update |
| **40** | 136 bytes | **96 bytes** | 512 bytes | 416 bytes (81.3%) | **Week 1 Smallest Test milestone** ($R=96\text{ B}$) |
| **52** | 172 bytes | 120 bytes | 512 bytes | 392 bytes (76.6%) | **Week 5 Accepted Path milestone** ($F=52$) |
| **60** | 196 bytes | 136 bytes | 512 bytes | 376 bytes (73.4%) | **Week 5 Controlled Bad Update milestone** ($F=60$) |
| **96** | 304 bytes | **208 bytes** | 512 bytes | 304 bytes (59.4%) | **Frozen Maximum Supported Record** ($R_{\max}=208\text{ B}$) |
| **150** | 466 bytes | 316 bytes | 512 bytes | 196 bytes (38.3%) | Theoretical large update ($> F_{\max}$) |
| **200** | 616 bytes | 416 bytes | 512 bytes | 96 bytes (18.8%) | Theoretical extreme update |
| **247** | 757 bytes | **510 bytes** | 512 bytes | 2 bytes (0.4%) | **Last point below break-even** |
| **248** | 760 bytes | **512 bytes** | 512 bytes | 0 bytes (0.0%) | **Exact break-even point ($F = 248$)** |
| **250** | 766 bytes | 516 bytes | 512 bytes | -4 bytes (snapshot wins) | Regime where snapshot is superior |

---

## 3. Ring Buffer Capacity & BRAM Utilization

- **Allocated Journal Ring BRAM**: $256 \text{ KiB} = 262,144 \text{ bytes}$.
- **Storage Capability**:
  - Maximum-size records ($F = 96 \implies 208 \text{ bytes}$):
    $$\lfloor 262,144 / 208 \rfloor = 1,260 \text{ simultaneous records}$$
  - Typical records ($F = 40 \implies 96 \text{ bytes}$):
    $$\lfloor 262,144 / 96 \rfloor = 2,730 \text{ simultaneous records}$$
  - Mean measured workload ($F \approx 32 \implies 80 \text{ bytes}$):
    $$\lfloor 262,144 / 80 \rfloor = 3,276 \text{ simultaneous records}$$
- **Record Index Table**:
  - $N = 1024$ slots.
  - Each slot: 16 bytes.
  - Total Index Table RAM: $1024 \times 16 = 16,384 \text{ bytes} = 16 \text{ KiB}$ (4 36Kb BRAMs).
- **Prototype Memory**:
  - 4 classes $\times$ 512 bytes = 2048 bytes (0.5 36Kb BRAM).
- **Trace Buffer**:
  - 512 entries $\times$ 8 bytes = 4096 bytes (1 36Kb BRAM).
- **Total PL BRAM Footprint**:
  - Journal Ring: 64 36Kb BRAMs
  - Index Table: 4 36Kb BRAMs
  - Prototype Memory: 1 36Kb BRAM
  - Trace Buffer: 1 36Kb BRAM
  - **Total**: 70 36Kb BRAM blocks out of 144 available on the Xilinx Zynq UltraScale+ XCZU5EV (Kria KV260) $\implies \mathbf{48.6\%}$ BRAM utilization.

---

## 4. Ring-Wrap Padding Analysis

Under the pad-to-end rule:
- If remaining space $L_{\text{rem}} < R(F)$, the allocator writes a pad marker of length $L_{\text{rem}}$ and restarts at offset 0.
- Worst-case padding per wrap: $R(F) - 1 \le 207 \text{ bytes}$.
- Total ring size: $262,144 \text{ bytes}$.
- Maximum wasted space ratio per wrap:
  $$\frac{207}{262,144} = 0.079\%$$
- Conclusion: Padding to avoid record fragmentation incurs less than $0.08\%$ memory overhead, which is negligible and vastly simplifies hardware verification.
