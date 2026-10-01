# Hand-Checked Residue and Alphabet Vectors (Week 1 Required Evidence)

This suite contains 42 hand-calculated vectors verifying the residue and alphabet contract:
- 36 valid passing vectors exploring the full signed residue range $[-8, +7]$ and signed contribution alphabet $[-8, +7]$.
- 6 retained negative failure vectors demonstrating exact refusal boundaries (e.g. unencodable $+8$, contributions outside $[-8, +7]$, residues outside $[-8, +7]$).

Threshold convention: $\text{sign\_threshold}(x) = 1 \text{ if } x \ge 0 \text{ else } 0$.

## Full Vector Table

| Vector ID | Residue ($r$) | Contribution ($u$) | Sum ($r+u$) | Old Bit | New Bit | Verdict | Failure Type / Reason | Retained Failure? |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|:---:|
| **V001** | $-8$ | $-8$ | $-16$ | 0 | 0 | **ACCEPT** | Valid, no threshold crossing | No |
| **V002** | $-8$ | $-1$ | $-9$ | 0 | 0 | **ACCEPT** | Valid, negative boundary | No |
| **V003** | $-8$ | $0$ | $-8$ | 0 | 0 | **ACCEPT** | Valid zero contribution | No |
| **V004** | $-8$ | $+7$ | $-1$ | 0 | 0 | **ACCEPT** | Valid maximum positive contribution | No |
| **V005** | $-7$ | $-1$ | $-8$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V006** | $-7$ | $+7$ | $0$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$ at zero boundary** | No |
| **V007** | $-6$ | $+6$ | $0$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$** | No |
| **V008** | $-5$ | $-3$ | $-8$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V009** | $-5$ | $+5$ | $0$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$** | No |
| **V010** | $-5$ | $+7$ | $+2$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$** | No |
| **V011** | $-4$ | $-4$ | $-8$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V012** | $-4$ | $+3$ | $-1$ | 0 | 0 | **ACCEPT** | Valid, near boundary | No |
| **V013** | $-4$ | $+4$ | $0$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$** | No |
| **V014** | $-3$ | $-5$ | $-8$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V015** | $-3$ | $+2$ | $-1$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V016** | $-3$ | $+3$ | $0$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$** | No |
| **V017** | $-2$ | $-6$ | $-8$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V018** | $-2$ | $+1$ | $-1$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V019** | $-2$ | $+2$ | $0$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$** | No |
| **V020** | $-1$ | $-7$ | $-8$ | 0 | 0 | **ACCEPT** | Valid | No |
| **V021** | $-1$ | $0$ | $-1$ | 0 | 0 | **ACCEPT** | Valid zero contribution | No |
| **V022** | $-1$ | $+1$ | $0$ | 0 | 1 | **ACCEPT** | **Threshold cross $0 \to 1$ (minimal flip)** | No |
| **V023** | $0$ | $-8$ | $-8$ | 1 | 0 | **ACCEPT** | **Threshold cross $1 \to 0$ (maximum flip)** | No |
| **V024** | $0$ | $-1$ | $-1$ | 1 | 0 | **ACCEPT** | **Threshold cross $1 \to 0$ (minimal flip)** | No |
| **V025** | $0$ | $0$ | $0$ | 1 | 1 | **ACCEPT** | Valid zero step at zero | No |
| **V026** | $0$ | $+7$ | $+7$ | 1 | 1 | **ACCEPT** | Valid | No |
| **V027** | $+1$ | $-8$ | $-7$ | 1 | 0 | **ACCEPT** | **Threshold cross $1 \to 0$** | No |
| **V028** | $+1$ | $-1$ | $0$ | 1 | 1 | **ACCEPT** | Valid, stays at threshold | No |
| **V029** | $+1$ | $0$ | $+1$ | 1 | 1 | **ACCEPT** | Valid | No |
| **V030** | $+2$ | $-3$ | $-1$ | 1 | 0 | **ACCEPT** | **Threshold cross $1 \to 0$** | No |
| **V031** | $+2$ | $-2$ | $0$ | 1 | 1 | **ACCEPT** | Valid | No |
| **V032** | $+2$ | $+5$ | $+7$ | 1 | 1 | **ACCEPT** | Valid | No |
| **V033** | $+4$ | $-5$ | $-1$ | 1 | 0 | **ACCEPT** | **Threshold cross $1 \to 0$** | No |
| **V034** | $+4$ | $-4$ | $0$ | 1 | 1 | **ACCEPT** | Valid | No |
| **V035** | $+7$ | $-8$ | $-1$ | 1 | 0 | **ACCEPT** | **Threshold cross $1 \to 0$** | No |
| **V036** | $+7$ | $+7$ | $+14$ | 1 | 1 | **ACCEPT** | Valid positive extreme | No |
| **V037** | $+7$ | $+8$ | N/A | 1 | N/A | **REFUSE** | Conceptual $+8$ unencodable in 4-bit 2's complement | **YES** |
| **V038** | $0$ | $+9$ | N/A | 1 | N/A | **REFUSE** | Contribution exceeds alphabet ($+9 > 7$) | No |
| **V039** | $0$ | $-9$ | N/A | 1 | N/A | **REFUSE** | Contribution exceeds alphabet ($-9 < -8$) | No |
| **V040** | $+8$ | $0$ | N/A | N/A | N/A | **REFUSE** | Residue outside signed 4-bit range ($+8 > 7$) | No |
| **V041** | $-9$ | $0$ | N/A | N/A | N/A | **REFUSE** | Residue outside signed 4-bit range ($-9 < -8$) | No |
| **V042** | $+3$ | $+12$ | N/A | 1 | N/A | **REFUSE** | Contribution gross overflow ($+12$) | No |
