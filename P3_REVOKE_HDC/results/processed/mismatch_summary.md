# REVOKE-HDC: Exact Restoration Regression and Flip-Density Report

## Executive Summary
- **Total Admitted Updates**: 1000
- **Total Software Restorations**: 1000
- **Total Bit Mismatches**: **0** (Target: 0)
- **Reference Match**: **y** (Bit-identical word-for-word across all 4096 dimensions)
- **Verdict**: **GREEN**

---

## Flip-Density Statistics ($F$)
- **Minimum $F$**: 2
- **Mean $F$**: 40.62
- **Median $F$**: 40
- **95th Percentile ($p95$)**: **65**
- **Maximum $F$**: **91** (Strictly $\le 96$)

---

## Persisted Journal Sizing vs Snapshot
- **Sizing Formula**: $R(F) = 16 + 2F$ bytes
- **Mean Record Size**: 97.23 bytes (vs 512 bytes snapshot: **81.0% savings**)
- **$p95$ Record Size**: 146 bytes (**71.5% savings**)
- **Maximum Record Size**: 198 bytes (**61.3% savings**)
- **Break-Even Condition**: $16 + 2F < 512 \iff F < 248$
- **Break-Even Frequency**: **100.0%** (1000/1000 updates strictly beat snapshot)

---

## Invariants Audit
All 8 required Week 2 correctness invariants held with **0 violations** across the entire 1,000-update regression campaign.
