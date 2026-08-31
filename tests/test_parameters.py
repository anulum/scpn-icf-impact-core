# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — parameter model tests

"""Every validation branch of the impact-ICF parameter model.

All parameter sets in this module are synthetic fixtures; none describes
any real machine.
"""

from __future__ import annotations

import math

import pytest

from scpn_icf_impact_core.errors import DeviceConfigurationError
from scpn_icf_impact_core.parameters import (
    Projectile,
    TargetDeclaration,
    require_finite,
    require_positive,
)


def synthetic_projectile(**overrides: float) -> Projectile:
    """Build a valid synthetic projectile with optional overrides."""
    values: dict[str, float] = {"mass_mg": 10.0, "velocity_km_s": 150.0}
    values.update(overrides)
    return Projectile(**values)


def test_require_finite_accepts_and_rejects() -> None:
    """The finite guard returns the value and rejects NaN and infinity."""
    assert require_finite("x", 1.5) == 1.5
    for bad in (math.nan, math.inf, -math.inf):
        with pytest.raises(DeviceConfigurationError, match="x: must be finite"):
            require_finite("x", bad)


def test_require_positive_accepts_and_rejects() -> None:
    """The positive guard returns the value and rejects zero and below."""
    assert require_positive("x", 0.1) == 0.1
    for bad in (0.0, -2.0):
        with pytest.raises(DeviceConfigurationError, match="strictly positive"):
            require_positive("x", bad)
    with pytest.raises(DeviceConfigurationError, match="must be finite"):
        require_positive("x", math.nan)


def test_kinetic_energy_formulas() -> None:
    """The kinetic-energy relations follow standard mechanics exactly."""
    projectile = synthetic_projectile()
    assert projectile.kinetic_energy_kj() == pytest.approx(
        0.5 * 10.0e-6 * (150.0e3) ** 2 / 1.0e3
    )
    assert projectile.specific_kinetic_energy_j_kg() == pytest.approx(
        0.5 * (150.0e3) ** 2
    )


@pytest.mark.parametrize(
    ("overrides", "fragment"),
    [
        ({"mass_mg": 0.0}, "mass_mg"),
        ({"velocity_km_s": -1.0}, "velocity_km_s"),
        ({"velocity_km_s": math.nan}, "velocity_km_s"),
    ],
)
def test_invalid_projectile_is_rejected(
    overrides: dict[str, float], fragment: str
) -> None:
    """Each projectile violation is rejected with its field name."""
    with pytest.raises(DeviceConfigurationError, match=fragment):
        synthetic_projectile(**overrides)


def test_invalid_target_is_rejected() -> None:
    """Non-positive target radii are rejected."""
    with pytest.raises(DeviceConfigurationError, match="target_radius_um"):
        TargetDeclaration(target_radius_um=0.0)
    with pytest.raises(DeviceConfigurationError, match="target_radius_um"):
        TargetDeclaration(target_radius_um=math.inf)
