# Worked Residue / Contribution Vectors - W1-R1

Threshold convention: `sign_threshold(x)=1 if x>=0 else 0`.

For valid encoded entries, compute `old_bit=sign_threshold(r)` and `new_bit=sign_threshold(r+u)` using at least a 5-bit signed sum. The first 36 vectors below are valid alphabet examples, satisfying the Week 1 requirement for at least 30 worked vectors. The final six are retained refusal examples.

| ID | r | u | r+u | old | new | Verdict | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V001 | -8 | -8 | -16 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V002 | -8 | -1 | -9 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V003 | -8 | 0 | -8 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V004 | -8 | 7 | -1 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V005 | -7 | -1 | -8 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V006 | -7 | 7 | 0 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V007 | -6 | 6 | 0 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V008 | -5 | -3 | -8 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V009 | -5 | 5 | 0 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V010 | -5 | 7 | 2 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V011 | -4 | -4 | -8 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V012 | -4 | 3 | -1 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V013 | -4 | 4 | 0 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V014 | -3 | -5 | -8 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V015 | -3 | 2 | -1 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V016 | -3 | 3 | 0 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V017 | -2 | -6 | -8 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V018 | -2 | 1 | -1 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V019 | -2 | 2 | 0 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V020 | -1 | -7 | -8 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V021 | -1 | 0 | -1 | 0 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V022 | -1 | 1 | 0 | 0 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V023 | 0 | -8 | -8 | 1 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V024 | 0 | -1 | -1 | 1 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V025 | 0 | 0 | 0 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V026 | 0 | 7 | 7 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V027 | 1 | -8 | -7 | 1 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V028 | 1 | -1 | 0 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V029 | 1 | 0 | 1 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V030 | 2 | -3 | -1 | 1 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V031 | 2 | -2 | 0 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V032 | 2 | 5 | 7 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V033 | 4 | -5 | -1 | 1 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V034 | 4 | -4 | 0 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V035 | 7 | -8 | -1 | 1 | 0 | accept | r and u are representable; threshold arithmetic shown |
| V036 | 7 | 7 | 14 | 1 | 1 | accept | r and u are representable; threshold arithmetic shown |
| V037 | 7 | 8 |  | 1 |  | refuse | conceptual +8 passes \|u\|<=8 wording but is not encodable in signed 4-bit two's-complement; retained failure exemplar |
| V038 | 0 | 9 |  | 1 |  | refuse | contribution exceeds alphabet and is not encodable |
| V039 | 0 | -9 |  | 1 |  | refuse | contribution magnitude/alphabet exceeded |
| V040 | 8 | 0 |  |  |  | refuse | pre_update_residue outside signed 4-bit range |
| V041 | -9 | 0 |  |  |  | refuse | pre_update_residue outside signed 4-bit range |
| V042 | 3 | 12 |  | 1 |  | refuse | contribution exceeds alphabet and is not encodable |

## Retained failure exemplar

`V037 = (r=7,u=+8)` is intentionally retained. Looking only at the phrase `|u|<=8` makes it appear legal, but the field is signed 4-bit two's-complement, where nibble `1000` decodes to `-8`, not `+8`. Therefore a host-side `+8` must be rejected before packing (outcome 4), or the field width/alphabet must be redesigned together.

## Independent check still required

These are fully worked vectors, but the uploaded artifact's request for a reproducer/countersignature is a human process step. Add reviewer name/date in the Friday evaluation after an independent person checks the CSV/MD pair.
