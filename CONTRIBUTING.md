# Contributing to Noetic-ASH

Thank you for your interest in the Noetic-ASH project. This document defines the contribution rules aligned with the [Noetic Physics](https://histoire-des-sciences.eu) ecosystem.

## Philosophy

All contributions must respect the **four pillars** of noetic methodology:

1. **Zero adjustable parameters** — $f_0$ and $N_{\mathrm{oct}}$ are fixed by the physical domain, never fitted to data
2. **SHA-256 reproducibility** — every benchmark, dataset, and result must be frozen with a cryptographic hash
3. **B3-FAIL** — null results are published with the same rigor as successes
4. **Cross-repo coherence** — changes to ASH must remain compatible with [`noetic-machine`](https://github.com/PORTEMANN/noetic-machine) and [`ko6-spectral-solver`](https://github.com/PORTEMANN/ko6-spectral-solver)

---

## Priority Contributions

### 1. Noetic Benchmarks (Critical)

The benchmark protocol follows the **C12.1** standard (see [`noetic-machine-complete`](https://github.com/PORTEMANN/noetic-machine-complete)):

- Pre-compute all constants before any data fitting
- Lock dependency versions (SHA-256 of each package)
- Document B3-FAIL: if ASH underperforms, publish the null result

**Target datasets:**
- **ECG5000** (UCR Archive) — binary normal/abnormal
- **NASA Bearing** (prognostics) — regime change detection
- **EPFL EEG Motor Imagery** — left/right hand classification
- **MIT-BIH Arrhythmia** — full 48 records, not just record 100

**Benchmark report format:**
```markdown
## Benchmark: [Dataset Name]

### Protocol
- ASH version: [commit SHA]
- Baseline methods: FFT+LDA, Wavelet+SVM, CNN-1D
- Cross-validation: 5-fold, stratified
- Noise test: SNR 20dB, 10dB, 0dB

### Results
| Method | Accuracy | F1 | ROC-AUC | Time/window |
|--------|----------|-----|---------|-------------|
| ASH + k-NN | 0.XX | 0.XX | 0.XX | X.XX ms |
| ... | ... | ... | ... | ... |

### SHA-256 Verification
- Dataset: `sha256:...`
- Code: `sha256:...`
- Results: `sha256:...`

### B3-FAIL Declaration
[ ] Success  [ ] Partial  [X] Fail — [explanation]
```

### 2. Embedded Ports

| Platform | MCU | Status | Maintainer |
|----------|-----|--------|------------|
| STM32F4 | ARM Cortex-M4 @ 168 MHz | ✅ Tested | — |
| ESP32 | Xtensa LX6 @ 240 MHz | ✅ Tested | — |
| ESP32-S3 | Xtensa LX7 @ 240 MHz | 🟡 Requested | — |
| nRF52840 | Cortex-M4 @ 64 MHz | 🟡 Requested | — |
| RP2040 | Cortex-M0+ @ 133 MHz | 🟡 Requested | — |
| Apollo4 Blue | Ultra-low-power | 🔴 Requested | — |

### 3. Noetic Hardware Prototypes

- **CERVEAU-1**: EEG headset with TGAM module + ESP32 (see `hardware/esp32_neurosky/`)
- **VIBRO-1**: Vibration sensor with STM32 + LoRaWAN
- **CARDIO-1**: ECG patch with nRF52840 + BLE

---

## Code Conventions

### Python

- PEP 8
- Type hints mandatory
- Docstrings must reference the noetic foundation when applicable:

```python
def process_window(
    signal: np.ndarray,
    fs: float,
    f0: float = 1.0,
    n_octaves: int = 4
) -> Tuple[float, int, float, np.ndarray, float]:
    """Analyze a signal window using noetic spectral discretization.

    The equal-temperament grid $f_n = f_0 \cdot 2^{n/12}$ implements
    the minimal spectral discretization compatible with the Koilon's
    torsion field periodicity (see spectral-triple-minimality, Thm T1).

    Args:
        signal: Time-series vector (1D)
        fs: Sampling frequency (Hz)
        f0: Fundamental frequency of the noetic grid (Hz)
        n_octaves: Number of octaves (determines spectral coverage)

    Returns:
        Tuple (Rc, Rtop, Rdyn, bands, ReN) where ReN is the Reynolds
        Noetic Number discriminating cosmological, meso, and quantum
        dynamical regimes.
    """
```

### C++

- C++11 minimum
- No external dependencies (FFT radix-2 homegrown)
- Fixed-size arrays preferred over dynamic allocation
- Doxygen documentation with `@noetic` tags for physical interpretation

```cpp
/**
 * @brief Compute the Reynolds Noetic Number
 * @param Rc Spectral energy
 * @param Rtop Peak count (topological complexity)
 * @param Rdyn Harmonic mismatch (torsion indicator)
 * @param bands Normalized octave-band vector
 * @return ReN — regime discriminator
 * 
 * @noetic The ReN quantifies the competition between torsion
 * (high-frequency complexity, $\lambda T[\Psi]$) and pressure
 * (low-frequency coherence, $J_{cosmo}(z)$) in the Koilon's
 * hydrodynamic regime. See noetic-machine, §3.4.
 */
float compute_ren(float Rc, uint8_t Rtop, float Rdyn, const float* bands);
```

---

## Pull Request Process

1. **Fork** the repository
2. **Branch**: `git checkout -b feature/noetic-description`
3. **Commit format**: `type(scope): description [PXX]`
   - `feat(benchmarks): add NASA Bearing benchmark [P34]`
   - `fix(embedded): correct FFT overflow on ESP32 [P32]`
   - `docs(algorithm): clarify Koilon-grid relation [P0]`
4. **SHA-256**: Include hashes of all datasets and results
5. **B3-FAIL**: If the contribution includes negative results, document them fully
6. **Cross-repo check**: Verify compatibility with `noetic-machine` and `ko6-spectral-solver`

---

## Issue Reporting

Use GitHub Issues with the following template:

```markdown
**Environment**
- ASH version: [commit SHA]
- Platform: [STM32/ESP32/etc.]
- Signal type: [EEG/ECG/vibration/audio]

**Expected behavior (noetic interpretation)**
What regime should be detected and why?

**Observed behavior**
Actual ReN, Rtop, Rdyn values.

**Reproduction**
Minimal code + dataset (with SHA-256).

**B3-FAIL check**
Does this invalidate a noetic prediction? [Yes/No/Unknown]
```

---

## Labels

| Label | Usage |
|-------|-------|
| `benchmark` | Comparative study against state-of-the-art |
| `embedded` | Microcontroller port or optimization |
| `hardware` | CERVEAU-1, VIBRO-1, CARDIO-1 prototypes |
| `noetic-foundation` | Link to CTFT, Koilon, or spectral-triple-minimality |
| `b3-fail` | Null or negative result |
| `cross-repo` | Requires coordination with noetic-machine or ko6-spectral-solver |
| `good first issue` | Accessible to new contributors |

---

## Resources

- [Noetic Physics](https://histoire-des-sciences.eu)
- [spectral-triple-minimality](https://github.com/PORTEMANN/spectral-triple-minimality) — Mathematical foundations
- [noetic-machine](https://github.com/PORTEMANN/noetic-machine) — Core physics
- [noetic-applications](https://github.com/PORTEMANN/noetic-applications) — Experimental case studies
- [Open Source Guides](https://opensource.guide/)

---

> *"La science véritable n'exclut pas l'invisible : elle le modélise."*
