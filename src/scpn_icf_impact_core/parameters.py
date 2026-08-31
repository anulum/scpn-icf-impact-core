# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — impact-ICF parameter model

"""Validated parameter objects of an impact-ICF configuration.

The derived quantities implement standard mechanics and nothing more:
the projectile kinetic energy ``E = m v^2 / 2`` and the specific kinetic
energy ``e = v^2 / 2``. Both are rough consistency instruments with
documented applicability bounds (impact-fusion projectile-velocity
scale; Proc. Impact Fusion Workshop, LA-8000-C, 1979); no claim about
any real machine follows from them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from scpn_icf_impact_core.errors import DeviceConfigurationError


def require_finite(name: str, value: float) -> float:
    """Return ``value`` when finite, otherwise fail closed.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is NaN or infinite; non-finite input is rejected,
        never clamped.
    """
    if not math.isfinite(value):
        raise DeviceConfigurationError(f"{name}: must be finite, got {value!r}")
    return value


def require_positive(name: str, value: float) -> float:
    """Return ``value`` when finite and strictly positive.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated value.

    Raises
    ------
    DeviceConfigurationError
        If ``value`` is non-finite or not strictly positive.
    """
    require_finite(name, value)
    if value <= 0.0:
        raise DeviceConfigurationError(
            f"{name}: must be strictly positive, got {value!r}"
        )
    return value


@dataclass(frozen=True, slots=True)
class Projectile:
    """Projectile parameters of an impact-ICF configuration.

    Parameters
    ----------
    mass_mg
        Projectile mass in milligrams; strictly positive.
    velocity_km_s
        Projectile velocity in kilometres per second; strictly
        positive.

    Raises
    ------
    DeviceConfigurationError
        If any parameter is non-finite or not strictly positive.
    """

    mass_mg: float
    velocity_km_s: float

    def __post_init__(self) -> None:
        """Validate the projectile invariants.

        Raises
        ------
        DeviceConfigurationError
            If any parameter is non-finite or not strictly positive.
        """
        require_positive("mass_mg", self.mass_mg)
        require_positive("velocity_km_s", self.velocity_km_s)

    def kinetic_energy_kj(self) -> float:
        """Kinetic energy of the validated projectile.

        Returns
        -------
        float
            ``E = m v^2 / 2`` in kilojoules.
        """
        mass_kg = self.mass_mg * 1.0e-6
        velocity_m_s = self.velocity_km_s * 1.0e3
        return 0.5 * mass_kg * velocity_m_s**2 / 1.0e3

    def specific_kinetic_energy_j_kg(self) -> float:
        """Specific kinetic energy of the validated projectile.

        Returns
        -------
        float
            ``e = v^2 / 2`` in joules per kilogram.
        """
        velocity_m_s = self.velocity_km_s * 1.0e3
        return 0.5 * velocity_m_s**2


@dataclass(frozen=True, slots=True)
class TargetDeclaration:
    """Target declaration of an impact-ICF configuration.

    Parameters
    ----------
    target_radius_um
        Target outer radius in micrometres; strictly positive.

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive.
    """

    target_radius_um: float

    def __post_init__(self) -> None:
        """Validate the target invariants.

        Raises
        ------
        DeviceConfigurationError
            If the radius is non-finite or not strictly positive.
        """
        require_positive("target_radius_um", self.target_radius_um)
