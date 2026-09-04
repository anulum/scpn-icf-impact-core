# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — what the flying plate carries

"""What an impacting plate carries onto the target it strikes.

An impact-fusion driver is a mass moving fast enough that its kinetic
energy, spread over the face it presents, is what heats the fuel. Three
quantities follow from that and nothing else: the mass the plate carries
per unit of that face, the thickness a given material has to be to carry
it, and the energy that face delivers per unit area.

**The kinetic energy itself is not here.** It belongs to
:class:`~scpn_icf_impact_core.parameters.Projectile`, which already owns
the plate's mass and velocity and states ``E = m v^2 / 2`` and
``e = v^2 / 2`` once. This module consumes the specific kinetic energy
that class computes rather than restating it.

Lengths are centimetres, densities grams per cubic centimetre and areas
square centimetres, because that is what the filed proceedings print.

Design record: ADR 0005.
"""

from __future__ import annotations

from typing import Final

from scpn_icf_impact_core.parameters import require_positive

#: Grams in a kilogram. The plate's areal density is quoted in grams and
#: its specific kinetic energy in joules per kilogram; this is the only
#: place the two systems meet.
GRAMS_PER_KILOGRAM: Final = 1.0e3
#: Joules in a megajoule.
JOULES_PER_MEGAJOULE: Final = 1.0e6
#: Milligrams in a gram.
MILLIGRAMS_PER_GRAM: Final = 1.0e3


def areal_density_g_cm2(mass_mg: float, impact_area_cm2: float) -> float:
    """Return the mass a plate carries per unit of the face it presents.

    Parameters
    ----------
    mass_mg
        Plate mass in milligrams; strictly positive.
    impact_area_cm2
        Area of the face that strikes the target, in square
        centimetres; strictly positive.

    Returns
    -------
    float
        ``rho t`` in grams per square centimetre, which is the unit the
        filed proceedings quote a projectile by.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.
    """
    require_positive("mass_mg", mass_mg)
    require_positive("impact_area_cm2", impact_area_cm2)
    return mass_mg / MILLIGRAMS_PER_GRAM / impact_area_cm2


def plate_thickness_cm(
    areal_density_g_cm2: float, material_density_g_cm3: float
) -> float:
    """Return how thick a plate of a given material has to be.

    Parameters
    ----------
    areal_density_g_cm2
        Mass per unit face area, in grams per square centimetre;
        strictly positive.
    material_density_g_cm3
        Bulk density of the plate material, in grams per cubic
        centimetre; strictly positive.

    Returns
    -------
    float
        Thickness in centimetres.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.

    Notes
    -----
    This is the direction the filed worked case runs: it solves its own
    equation for the areal density a given fuel state demands, and only
    then divides by a chosen material's density to say how thick the
    plate is. The choice of material is what turns an areal density into
    a dimension.
    """
    require_positive("areal_density_g_cm2", areal_density_g_cm2)
    require_positive("material_density_g_cm3", material_density_g_cm3)
    return areal_density_g_cm2 / material_density_g_cm3


def energy_per_area_mj_per_cm2(
    areal_density_g_cm2: float, specific_kinetic_energy_j_per_kg: float
) -> float:
    """Return the energy a plate delivers per unit of its face.

    Parameters
    ----------
    areal_density_g_cm2
        Mass per unit face area, in grams per square centimetre;
        strictly positive.
    specific_kinetic_energy_j_per_kg
        Kinetic energy per unit mass, in joules per kilogram; strictly
        positive. Supplied by
        :meth:`~scpn_icf_impact_core.parameters.Projectile.specific_kinetic_energy_j_kg`,
        which owns ``v^2 / 2``.

    Returns
    -------
    float
        Delivered energy per unit area, in megajoules per square
        centimetre.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.

    Notes
    -----
    The product is the whole kinetic energy of the plate spread over its
    face. Nothing is subtracted for what the plate keeps after impact,
    for radiation, or for the fraction that never couples: this is what
    arrives, not what is absorbed.
    """
    require_positive("areal_density_g_cm2", areal_density_g_cm2)
    require_positive(
        "specific_kinetic_energy_j_per_kg", specific_kinetic_energy_j_per_kg
    )
    joules_per_cm2 = (
        areal_density_g_cm2 / GRAMS_PER_KILOGRAM * specific_kinetic_energy_j_per_kg
    )
    return joules_per_cm2 / JOULES_PER_MEGAJOULE
