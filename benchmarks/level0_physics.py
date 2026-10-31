# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — level-0 physics benchmark

"""Benchmark the level-0 physics of this package on the Python floor.

Follows the ecosystem benchmark standard: warm-up, repeated samples,
percentiles, one row per (operation, backend), unavailable backends marked
explicitly, full provenance in the artefact. Two operations are timed:

- ``closed_forms``: the plate areal density, thickness and energy per
  area, the slab and sphere masses, the compressed thickness and radius
  and the full-burn energy over a deterministic grid of synthetic plate
  masses and compression factors; each sample times one full grid pass;
- ``level0_record``: the composed level-0 record with its canonical bytes
  on the synthetic fuel, projectile and schemes over a grid of plate
  masses; each sample times one full grid pass.

This package has no native crate. The ``rust_native`` row records that
explicitly instead of omitting it. Nothing measured here is a physics
claim, and a run on a loaded host is a smoke timing, not a performance
measurement.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import platform
import shutil
import statistics
import subprocess
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Final

ROOT: Final = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from scpn_icf_impact_core.configuration import (  # noqa: E402
    DeviceConfiguration,
    RegistryBinding,
)
from scpn_icf_impact_core.parameters import (  # noqa: E402
    Projectile,
    TargetDeclaration,
)
from scpn_icf_impact_core.physics import (  # noqa: E402
    FuelDeclaration,
    ProjectileDeclaration,
    SchemeDeclaration,
    level0_physics,
)
from scpn_icf_impact_core.physics.compression import (  # noqa: E402
    planar_compressed_thickness_cm,
    spherical_compressed_radius_cm,
)
from scpn_icf_impact_core.physics.fuel import (  # noqa: E402
    full_burn_energy_mj,
    slab_mass_mg,
    sphere_mass_mg,
)
from scpn_icf_impact_core.physics.projectile import (  # noqa: E402
    areal_density_g_cm2,
    energy_per_area_mj_per_cm2,
    plate_thickness_cm,
)

SCHEMA: Final = "scpn-icf-impact-core.level0-physics-benchmark.v1"
NATIVE_STATUS: Final = (
    "unavailable: this package has no native crate; the level-0 kernels use "
    "+ - * / and the platform pow (cubes) only, and the decision on a "
    "native backend is open with the project owner"
)


def grid(points: int) -> list[tuple[float, float]]:
    """Build a deterministic synthetic grid of plate masses and factors.

    Parameters
    ----------
    points
        Number of grid points.

    Returns
    -------
    list of (float, float)
        ``(plate_mass_mg, compression_factor)`` pairs, the mass between 10
        and 100 mg and the factor between 2 and 20.
    """
    return [
        (10.0 + 90.0 * (index % 97) / 96.0, 2.0 + 18.0 * (index % 89) / 88.0)
        for index in range(points)
    ]


def configuration(plate_mass_mg: float) -> DeviceConfiguration:
    """Return a synthetic impact configuration; it describes nothing.

    Parameters
    ----------
    plate_mass_mg
        Mass of the plate.

    Returns
    -------
    DeviceConfiguration
        A ``projectile_or_impact_icf`` configuration at 200 km/s.
    """
    return DeviceConfiguration(
        identifier="projectile_or_impact_icf",
        projectile=Projectile(mass_mg=plate_mass_mg, velocity_km_s=200.0),
        target=TargetDeclaration(target_radius_um=1000.0),
        registry=RegistryBinding(version="1.0.0", digest_sha256="0" * 64),
    )


def closed_forms_pass(sample_grid: list[tuple[float, float]]) -> float:
    """Evaluate the closed forms once over the grid.

    Parameters
    ----------
    sample_grid
        Plate-mass and compression-factor pairs.

    Returns
    -------
    float
        Checksum of the results, so the work cannot be optimised away.
    """
    total = 0.0
    for mass, factor in sample_grid:
        areal = areal_density_g_cm2(mass, 1.0)
        total += areal + plate_thickness_cm(areal, 18.8)
        total += energy_per_area_mj_per_cm2(areal, 2.0e10)
        total += slab_mass_mg(1.0, 1.0, 0.00213) + sphere_mass_mg(0.1, 0.213)
        total += planar_compressed_thickness_cm(1.0, 0.01, 4.2)
        total += spherical_compressed_radius_cm(0.1, factor)
        total += full_burn_energy_mj(mass)
    return total


def record_pass_factory() -> Callable[[list[tuple[float, float]]], float]:
    """Return a grid pass that composes and serialises level-0 records.

    Returns
    -------
    callable
        The pass; the plate mass of each grid point sets the configuration
        and its factor is ignored.
    """
    fuel = FuelDeclaration(
        cryogenic_density_g_cm3=0.213,
        initial_pressure_bar=10.0,
        initial_temperature_k=300.0,
        initial_density_ratio=0.01,
        compressed_density_ratio=4.2,
    )
    projectile = ProjectileDeclaration(material_density_g_cm3=18.8, impact_area_cm2=1.0)
    scheme = SchemeDeclaration(slab_thickness_cm=1.0, radial_compression_factor=10.0)

    def record_pass(sample_grid: list[tuple[float, float]]) -> float:
        total = 0
        for mass, _factor in sample_grid:
            record = level0_physics(configuration(mass), fuel, projectile, scheme)
            total += len(record.canonical_bytes())
        return float(total)

    return record_pass


def measure(
    run: Callable[[list[tuple[float, float]]], float],
    sample_grid: list[tuple[float, float]],
    warmup: int,
    repeats: int,
) -> dict[str, float]:
    """Time repeated grid passes and summarise them.

    Parameters
    ----------
    run
        Grid pass to time.
    sample_grid
        Parameter grid.
    warmup
        Discarded leading passes.
    repeats
        Timed passes.

    Returns
    -------
    dict[str, float]
        Percentiles, mean, min, max in microseconds per grid point and the
        throughput in points per second (P50-based).
    """
    for _ in range(warmup):
        run(sample_grid)
    samples: list[float] = []
    for _ in range(repeats):
        start = time.perf_counter_ns()
        run(sample_grid)
        samples.append((time.perf_counter_ns() - start) / 1e3 / len(sample_grid))
    ordered = sorted(samples)

    def percentile(fraction: float) -> float:
        return ordered[min(len(ordered) - 1, round(fraction * (len(ordered) - 1)))]

    p50 = percentile(0.5)
    return {
        "p50_us_per_point": p50,
        "p95_us_per_point": percentile(0.95),
        "p99_us_per_point": percentile(0.99),
        "mean_us_per_point": statistics.fmean(samples),
        "min_us_per_point": ordered[0],
        "max_us_per_point": ordered[-1],
        "throughput_points_per_s": 1e6 / p50,
    }


def provenance() -> dict[str, Any]:
    """Collect the environment provenance of a run.

    Returns
    -------
    dict[str, Any]
        Interpreter, platform, CPU model, commit and host-load context.
    """
    cpu_model = "unknown"
    with contextlib.suppress(OSError):
        for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    load = "unavailable"
    with contextlib.suppress(OSError):
        load = Path("/proc/loadavg").read_text(encoding="utf-8").split()[0]
    commit = "unknown"
    git = shutil.which("git")
    if git is not None:
        with contextlib.suppress(OSError):
            # A fixed argument vector with the resolved executable; no shell.
            commit = subprocess.run(  # noqa: S603
                [git, "rev-parse", "HEAD"],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            ).stdout.strip()
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_model": cpu_model,
        "load_average_1min_at_start": load,
        "commit": commit,
        "isolated_cores": False,
    }


def main(argv: list[str] | None = None) -> int:
    """Run the benchmark command-line interface.

    Parameters
    ----------
    argv
        Argument vector; None reads sys.argv.

    Returns
    -------
    int
        0 on completion.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=int, default=20_000)
    parser.add_argument("--record-points", type=int, default=2_000)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--label", default="local")
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "results")
    args = parser.parse_args(argv)
    sample_grid = grid(args.points)
    record_grid = grid(args.record_points)
    record_pass = record_pass_factory()
    results: list[dict[str, Any]] = [
        {
            "name": "closed_forms",
            "backend": "python_floor",
            "stats": measure(closed_forms_pass, sample_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "closed_forms",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
        {
            "name": "level0_record",
            "backend": "python_floor",
            "stats": measure(record_pass, record_grid, args.warmup, args.repeats),
            "status": "measured",
        },
        {
            "name": "level0_record",
            "backend": "rust_native",
            "stats": None,
            "status": NATIVE_STATUS,
        },
    ]
    artefact = {
        "schema": SCHEMA,
        "generated_at": datetime.now(UTC).isoformat(),
        "label": args.label,
        "platform": provenance(),
        "parameters": {
            "points": args.points,
            "record_points": args.record_points,
            "warmup": args.warmup,
            "repeats": args.repeats,
        },
        "results": results,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / f"level0_physics.{args.label}.json"
    target.write_text(
        json.dumps(artefact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"benchmark: wrote {target}")
    for row in results:
        print(f"  {row['name']} {row['backend']}: {row['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
