# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — the fuel, in two geometries

"""What the fuel is, in each of the two geometries the sources describe.

The filed proceedings describe an impacted slab and a converging sphere,
and the same deuterium-tritium fuel in both. This module turns a density
and a dimension into a mass and into an areal density, in whichever of
the two geometries the caller means, and turns a mass into the energy a
complete burn would release.

**The two geometries start from different densities, and that is not an
oversight.** The slab is fuel *gas* held at a declared fraction of the
cryogenic density; the sphere is *solid* fuel at the cryogenic density
itself. A caller that hands the sphere the gas density has described a
different target, so both relations take the density explicitly rather
than reaching for a shared constant.

**The specific energy is computed, not typed.** It is built from the two
nuclear masses and the energy released per reaction, so that changing
either input moves the answer, rather than carried as a rounded figure
whose provenance would be gone.

Lengths are centimetres and densities grams per cubic centimetre,
because that is what the proceedings print. Masses are milligrams.

Design record: ADR 0005.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_icf_impact_core.errors import DeviceConfigurationError
from scpn_icf_impact_core.parameters import require_positive

#: Atomic mass unit in kilograms (CODATA 2022).
ATOMIC_MASS_UNIT_KG: Final = 1.66053906892e-27
#: One megaelectronvolt in joules, exact under the 2019 SI definition of
#: the elementary charge.
MEGAELECTRONVOLT_J: Final = 1.602176634e-13
#: Boltzmann constant in joules per kelvin, exact under the 2019 SI.
BOLTZMANN_CONSTANT_J_PER_K: Final = 1.380649e-23
#: Deuteron and triton masses in atomic mass units.
DEUTERON_MASS_U: Final = 2.013553212745
TRITON_MASS_U: Final = 3.01550941034
#: Energy released by one D + T -> alpha + n reaction, in MeV.
DT_FUSION_ENERGY_MEV: Final = 17.59
#: Pascals in a bar.
PASCALS_PER_BAR: Final = 1.0e5
#: Cubic centimetres in a cubic metre.
CUBIC_CM_PER_CUBIC_M: Final = 1.0e6
#: Milligrams in a gram, and grams in a kilogram.
MILLIGRAMS_PER_GRAM: Final = 1.0e3
GRAMS_PER_KILOGRAM: Final = 1.0e3
#: Joules in a megajoule.
JOULES_PER_MEGAJOULE: Final = 1.0e6


def dt_molecule_mass_u() -> float:
    """Return the mass of one deuterium-tritium molecule.

    Returns
    -------
    float
        The two nuclear masses added, in atomic mass units. Equimolar
        fuel has the same mean molecular mass whether it is counted as
        DT molecules or as an equilibrium mixture of D2, DT and T2,
        because the atom inventory is the same either way.
    """
    return DEUTERON_MASS_U + TRITON_MASS_U


def dt_specific_energy_j_per_g() -> float:
    """Return the energy a gram of equimolar fuel releases on full burn.

    Returns
    -------
    float
        Joules per gram consumed. The reacting pair is one deuteron and
        one triton, so a gram of equimolar fuel holds one pair per
        combined nuclear mass.
    """
    pair_mass_g = dt_molecule_mass_u() * ATOMIC_MASS_UNIT_KG * GRAMS_PER_KILOGRAM
    return DT_FUSION_ENERGY_MEV * MEGAELECTRONVOLT_J / pair_mass_g


def ideal_gas_density_g_cm3(pressure_bar: float, temperature_k: float) -> float:
    """Return the density of fuel gas at a stated pressure and temperature.

    Parameters
    ----------
    pressure_bar
        Gas pressure in bar; strictly positive.
    temperature_k
        Gas temperature in kelvin; strictly positive.

    Returns
    -------
    float
        Density in grams per cubic centimetre.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.

    Notes
    -----
    **This is a consistency instrument, not an anchor.** The filed
    worked case prints a pressure, a temperature and a density ratio
    without stating a relation between them; evaluating the ideal-gas
    law on the first two says whether the third is consistent with them.
    Doing so assumes the fuel is an ideal gas of diatomic molecules,
    which the source does not state, so what comes back agrees with the
    printed ratio only to the one significant figure that ratio carries.
    """
    require_positive("pressure_bar", pressure_bar)
    require_positive("temperature_k", temperature_k)
    number_density_per_m3 = (
        pressure_bar * PASCALS_PER_BAR / (BOLTZMANN_CONSTANT_J_PER_K * temperature_k)
    )
    density_kg_per_m3 = (
        number_density_per_m3 * dt_molecule_mass_u() * ATOMIC_MASS_UNIT_KG
    )
    return density_kg_per_m3 * GRAMS_PER_KILOGRAM / CUBIC_CM_PER_CUBIC_M


def density_from_ratio_g_cm3(
    density_ratio: float, reference_density_g_cm3: float
) -> float:
    """Return an absolute density from a ratio to a reference.

    Parameters
    ----------
    density_ratio
        The fuel density as a multiple of the reference; strictly
        positive. The filed worked case quotes every one of its four
        states this way.
    reference_density_g_cm3
        The reference the ratio is taken against, in grams per cubic
        centimetre; strictly positive. In the filed case that is the
        cryogenic density of the fuel.

    Returns
    -------
    float
        The absolute density in grams per cubic centimetre.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("density_ratio", density_ratio)
    require_positive("reference_density_g_cm3", reference_density_g_cm3)
    return density_ratio * reference_density_g_cm3


def slab_areal_density_g_cm2(thickness_cm: float, density_g_cm3: float) -> float:
    """Return the areal density along the axis of a plane fuel slab.

    Parameters
    ----------
    thickness_cm
        Slab thickness along the direction the plate travels, in
        centimetres; strictly positive.
    density_g_cm3
        Uniform fuel density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        ``rho R`` in grams per square centimetre.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("thickness_cm", thickness_cm)
    require_positive("density_g_cm3", density_g_cm3)
    return density_g_cm3 * thickness_cm


def slab_mass_mg(thickness_cm: float, area_cm2: float, density_g_cm3: float) -> float:
    """Return the fuel mass of a plane slab of stated cross-section.

    Parameters
    ----------
    thickness_cm
        Slab thickness in centimetres; strictly positive.
    area_cm2
        Cross-section the slab presents to the plate, in square
        centimetres; strictly positive.
    density_g_cm3
        Uniform fuel density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        Mass in milligrams.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive.
    """
    require_positive("thickness_cm", thickness_cm)
    require_positive("area_cm2", area_cm2)
    require_positive("density_g_cm3", density_g_cm3)
    return thickness_cm * area_cm2 * density_g_cm3 * MILLIGRAMS_PER_GRAM


def sphere_mass_mg(radius_cm: float, density_g_cm3: float) -> float:
    """Return the mass of a uniform fuel sphere.

    Parameters
    ----------
    radius_cm
        Sphere radius in centimetres; strictly positive.
    density_g_cm3
        Uniform fuel density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        Mass in milligrams.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("radius_cm", radius_cm)
    require_positive("density_g_cm3", density_g_cm3)
    volume_cm3 = 4.0 / 3.0 * math.pi * radius_cm**3
    return volume_cm3 * density_g_cm3 * MILLIGRAMS_PER_GRAM


def sphere_areal_density_g_cm2(radius_cm: float, density_g_cm3: float) -> float:
    """Return the areal density from the centre of a fuel sphere outwards.

    Parameters
    ----------
    radius_cm
        Sphere radius in centimetres; strictly positive.
    density_g_cm3
        Uniform fuel density in grams per cubic centimetre; strictly
        positive.

    Returns
    -------
    float
        ``rho r`` in grams per square centimetre, along one radius from
        the centre to the surface. That is the convention the filed
        proceedings quote against the ignition requirement, and it is
        half of what a chord through the whole sphere would give.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("radius_cm", radius_cm)
    require_positive("density_g_cm3", density_g_cm3)
    return density_g_cm3 * radius_cm


def full_burn_energy_mj(fuel_mass_mg: float) -> float:
    """Return the energy an inventory would release if all of it burned.

    Parameters
    ----------
    fuel_mass_mg
        Fuel inventory in milligrams; strictly positive.

    Returns
    -------
    float
        Released energy in megajoules.

    Raises
    ------
    DeviceConfigurationError
        If the mass is non-finite or not strictly positive.

    Notes
    -----
    **No target burns all of its fuel**, and no filed source in this
    family prints a burn-up fraction. Rather than invent one, this
    module states the upper bound the inventory sets and leaves the
    fraction to whoever has measured it. The filed proceedings make the
    same statement in the same direction, about one gram of fuel.
    """
    require_positive("fuel_mass_mg", fuel_mass_mg)
    grams = fuel_mass_mg / MILLIGRAMS_PER_GRAM
    return grams * dt_specific_energy_j_per_g() / JOULES_PER_MEGAJOULE


def require_below_unity(name: str, value: float) -> float:
    """Return a ratio when it is strictly positive and below one.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated ratio.

    Raises
    ------
    DeviceConfigurationError
        If the value is non-finite, not strictly positive, or at or
        above one. A fuel gas at or above the cryogenic density of its
        own liquid is not the gas the declaration describes, so the
        value is refused rather than carried.
    """
    require_positive(name, value)
    if value >= 1.0:
        raise DeviceConfigurationError(f"{name}: must be below 1.0, got {value!r}")
    return value
