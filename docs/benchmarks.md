<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Impact Core — Benchmarks and computation contract
-->

# Benchmarks and computation contract

## Computation contract

The level-0 physics of this package is a set of closed forms evaluated in
IEEE-754 binary64 on the Python floor (lengths in cm, densities in g/cm³,
masses in mg, energies in MJ):

| Module | Kernels | Operations |
|---|---|---|
| `physics/projectile.py` | plate areal density, thickness and energy per area | `* /` |
| `physics/fuel.py` | D-T specific energy from CODATA 2022 masses, ideal-gas density, slab and sphere masses `4/3 pi rho r^3`, areal densities, full-burn energy | `* / +`, `pi`, **`pow`** (cube) |
| `physics/compression.py` | compression ratio, planar compressed thickness, spherical compressed radius and density ratio `f^3` | `* /`, **`pow`** (cube) |
| `physics/level0.py` | the composed record with canonical bytes and SHA-256 digest | composition, JSON serialisation |

Every input outside its domain is refused with the package error, never
clamped. Apart from the cube, every operation is correctly rounded by
IEEE-754; the cube is the platform `pow`, which the standard does not
require to be correctly rounded. A native backend that must agree bit for
bit would have to compute the cube the same way on both sides. The
constants and their editions are documented in `physics/fuel.py` and bound
by tests.

**Backend status.** Python floor only. There is no native crate. Audit
plan Q01 asks for a native path on required numeric paths and allows a
scoped, owner-approved exception for trivial non-hot arithmetic; that
decision is the owner's and is recorded as open in the backlog. The
benchmark marks the native backend as unavailable instead of omitting it.

## Level-0 physics — local workstation (non-isolated)

Artefact: `benchmarks/results/level0_physics.local.json` (schema
`scpn-icf-impact-core.level0-physics-benchmark.v1`, generated 2026-10-31T03:58:16.317815+00:00, at commit
`dc893f31fe1a` with the working tree of the landing commit).
Host: 11th Gen Intel(R) Core(TM) i5-11600K @ 3.90GHz, Linux-7.0.0-34-generic-x86_64-with-glibc2.39, Python 3.12.3; load average
at start 4.58 (other sessions were active on the host);
cores not isolated, so treat the numbers as a smoke timing, not a
performance measurement. Parameters: 20000 closed-form points and
2000 records, 3 warm-up passes, 20 timed passes.

### `closed_forms` (plate, fuel, compression and burn closed forms per point)

| Backend | P50 µs/point | P95 µs/point | P99 µs/point | mean µs/point | throughput points/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 1.591 | 1.689 | 1.704 | 1.593 | 628347 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

### `level0_record` (composed record with canonical bytes per point)

| Backend | P50 µs/record | P95 µs/record | P99 µs/record | mean µs/record | throughput records/s | status |
|---|---|---|---|---|---|---|
| `python_floor` (public API) | 36.679 | 43.791 | 48.373 | 37.412 | 27264 | measured |
| `rust_native` | — | — | — | — | — | unavailable: no native crate |

## Regenerate

```bash
.venv/bin/python benchmarks/level0_physics.py --label local
```

The script writes `benchmarks/results/level0_physics.<label>.json` with the
provenance above. A number from a fixed CI runner or isolated cores would
replace the smoke timing here; none is claimed yet.
