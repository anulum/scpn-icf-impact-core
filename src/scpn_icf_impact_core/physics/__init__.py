# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — level-0 device physics package

"""Closed-form level-0 physics of an impact-driven inertial-fusion target.

Three surfaces: what a flying plate carries onto the target it strikes,
what the fuel is in each of the two geometries the filed proceedings
describe, and where that fuel ends up when it is compressed. Nothing
here integrates anything in time and nothing here solves a shock.
Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_icf_impact_core.physics.compression import (
    compression_ratio,
    planar_compressed_thickness_cm,
    require_compression_factor,
    spherical_compressed_radius_cm,
    spherical_density_ratio,
)
from scpn_icf_impact_core.physics.fuel import (
    ATOMIC_MASS_UNIT_KG,
    BOLTZMANN_CONSTANT_J_PER_K,
    DEUTERON_MASS_U,
    DT_FUSION_ENERGY_MEV,
    MEGAELECTRONVOLT_J,
    TRITON_MASS_U,
    density_from_ratio_g_cm3,
    dt_molecule_mass_u,
    dt_specific_energy_j_per_g,
    full_burn_energy_mj,
    ideal_gas_density_g_cm3,
    require_below_unity,
    slab_areal_density_g_cm2,
    slab_mass_mg,
    sphere_areal_density_g_cm2,
    sphere_mass_mg,
)
from scpn_icf_impact_core.physics.level0 import (
    KILOJOULES_PER_MEGAJOULE,
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    MICROMETRES_PER_CENTIMETRE,
    FuelDeclaration,
    Level0Physics,
    OperatingPoint,
    ProjectileDeclaration,
    SchemeDeclaration,
    level0_physics,
    target_radius_cm,
)
from scpn_icf_impact_core.physics.projectile import (
    areal_density_g_cm2,
    energy_per_area_mj_per_cm2,
    plate_thickness_cm,
)

__all__ = [
    "ATOMIC_MASS_UNIT_KG",
    "BOLTZMANN_CONSTANT_J_PER_K",
    "DEUTERON_MASS_U",
    "DT_FUSION_ENERGY_MEV",
    "KILOJOULES_PER_MEGAJOULE",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MEGAELECTRONVOLT_J",
    "MICROMETRES_PER_CENTIMETRE",
    "TRITON_MASS_U",
    "FuelDeclaration",
    "Level0Physics",
    "OperatingPoint",
    "ProjectileDeclaration",
    "SchemeDeclaration",
    "areal_density_g_cm2",
    "compression_ratio",
    "density_from_ratio_g_cm3",
    "dt_molecule_mass_u",
    "dt_specific_energy_j_per_g",
    "energy_per_area_mj_per_cm2",
    "full_burn_energy_mj",
    "ideal_gas_density_g_cm3",
    "level0_physics",
    "planar_compressed_thickness_cm",
    "plate_thickness_cm",
    "require_below_unity",
    "require_compression_factor",
    "slab_areal_density_g_cm2",
    "slab_mass_mg",
    "sphere_areal_density_g_cm2",
    "sphere_mass_mg",
    "spherical_compressed_radius_cm",
    "spherical_density_ratio",
    "target_radius_cm",
]
