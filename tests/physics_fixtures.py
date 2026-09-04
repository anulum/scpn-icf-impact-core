# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — level-0 physics anchors and builders

"""Anchors and builders shared by the level-0 physics tests.

Reproducing a printed value is an anchor, never a claim about that
machine.

Every constant below whose name begins ``PRINTED_`` is read from the
proceedings this repository cites, *Proceedings of the Impact Fusion
Workshop*, LA-8000-C (Los Alamos Scientific Laboratory, 1979), which is
on file and freely published. The volume is a scan carrying an optical
transcription, so **every value was read off pages rendered at 170 dpi**
rather than off the text layer, and the scan duplicates some early
leaves, so the printed-page and document-page numbers below are both
given and do not differ by a constant.

Two papers in the volume carry geometry and they describe **two
different schemes**:

- ``CHRISTIANSEN_`` — W. Christiansen, *Target Dynamics and
  Thermonuclear Burn, Part 2*, printed p. 33 / document p. 46. The only
  fully dimensioned case in the volume: a uranium plate driving a plane
  slab of fuel gas against a rigid wall, worked through four states.
- ``MARSHALL_`` — J. Marshall, *Target Dynamics and Thermonuclear Burn,
  Part I*, printed p. 27 / document p. 38. The convergent alternative,
  and the verdict that "simple one-dimensional shock heating is
  unsuitable for fusion power production".

**No filed source pairs the two.** Marshall's sphere has no projectile
printed for it anywhere in the volume, and Christiansen's plate belongs
to the plane case. The fixtures build one configuration from both
because the repository owns one configuration; the record's non-claims
say plainly that this is an evaluation of two published schemes and not
a description of one design.

**Two of the volume's printed values do not reproduce, and both are
named for it.** ``NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG`` is 0.84 mg
for a 1 mm sphere of solid fuel, which needs a density near 0.20 g/cm3
rather than the 0.213 g/cm3 the volume prints elsewhere.
``NOT_REPRODUCED_MARSHALL_GRAM_BURN_GJ`` is the "nearly 400 GJ" of a
one-gram burn, against 337.5 GJ from the nuclear masses. Neither is
adjusted to make an anchor come out, and neither is used as one.

**The volume truncates rather than rounds**, measured on two independent
values: a plate thickness whose relation gives 2.766e-3 cm is printed
2.7e-3, and a compressed thickness whose relation gives 2.381e-3 cm is
printed 2.3e-3. Rounding would have given 2.8e-3 and 2.4e-3, so a test
asserting rounding would have failed on both.
"""

from __future__ import annotations

import math
from typing import Final

from scpn_icf_impact_core.configuration import DeviceConfiguration, RegistryBinding
from scpn_icf_impact_core.parameters import Projectile, TargetDeclaration
from scpn_icf_impact_core.physics.level0 import (
    FuelDeclaration,
    ProjectileDeclaration,
    SchemeDeclaration,
)

# --- Christiansen, printed p. 33: the worked plane case ---
#: Cryogenic density of the fuel, the reference every ratio is against.
PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3: Final = 0.213
#: The density ratio of all four printed states. Only the first and the
#: fourth enter the record: the record states where the fuel starts and
#: where it ends up, and the chain between them is a shock solution this
#: repository does not perform.
PRINTED_CHRISTIANSEN_DENSITY_RATIOS: Final = (0.01, 0.04, 0.10, 4.2)
#: Pressure and temperature of the three shocked states. **State 1 is
#: not in these tuples**, because the volume prints it in different units
#: from the other three — bar and kelvin against megabar and
#: electronvolts — and silently converting it would hide that.
PRINTED_CHRISTIANSEN_SHOCKED_PRESSURES_MB: Final = (1.12, 6.7, 3400.0)
PRINTED_CHRISTIANSEN_SHOCKED_TEMPERATURES_EV: Final = (173.0, 415.0, 5000.0)
#: State 1, in the units the volume prints it in.
PRINTED_CHRISTIANSEN_INITIAL_PRESSURE_BAR: Final = 10.0
PRINTED_CHRISTIANSEN_INITIAL_TEMPERATURE_K: Final = 300.0
#: The plate: a uranium slab at 200 km/s presenting a 1 cm by 1 cm face.
PRINTED_CHRISTIANSEN_VELOCITY_KM_S: Final = 200.0
PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3: Final = 18.8
PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2: Final = 1.0
#: The plate's areal density, which the volume's Eq. (6) is solved for.
PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2: Final = 0.052
#: The plate thickness that areal density implies for uranium, printed
#: to two significant figures as a truncation of 2.7659e-3.
PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM: Final = 2.7e-3
#: The fuel slab before and at peak compression, in centimetres. The
#: compressed value is printed to two significant figures as a
#: truncation of 2.3810e-3.
PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM: Final = 1.0
PRINTED_CHRISTIANSEN_COMPRESSED_THICKNESS_CM: Final = 2.3e-3
#: Energy the plate's face delivers per unit area.
PRINTED_CHRISTIANSEN_ENERGY_PER_AREA_MJ_PER_CM2: Final = 1.04

# --- Marshall, printed p. 27: the convergent alternative ---
#: Radius of the solid-fuel sphere, in micrometres for the configuration.
PRINTED_MARSHALL_SPHERE_RADIUS_UM: Final = 1.0e3
#: Factor its radius falls by.
PRINTED_MARSHALL_RADIAL_COMPRESSION_FACTOR: Final = 10.0
#: Areal density it reaches, printed to one significant figure.
PRINTED_MARSHALL_AREAL_DENSITY_G_CM2: Final = 2.0

# --- Printed, measured, and not reproduced ---
#: Printed mass of the 1 mm sphere. At the volume's own cryogenic
#: density that sphere masses 0.8922 mg; 0.84 mg implies about
#: 0.2005 g/cm3. The relation is not adjusted to reach it.
NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG: Final = 0.84
#: Printed energy of a one-gram burn. The nuclear masses give 337.5 GJ.
NOT_REPRODUCED_MARSHALL_GRAM_BURN_GJ: Final = 400.0

# --- Derived from printed values, and named for it ---
#: The plate's mass over its printed face, which the configuration needs
#: and the volume does not print. It is the printed areal density times
#: the printed area, so recovering that areal density from it is a round
#: trip and the tests say which of the two is the anchor.
DERIVED_CHRISTIANSEN_PLATE_MASS_MG: Final = (
    PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2
    * PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2
    * 1.0e3
)

# --- Synthetic; pins nothing ---
SYNTHETIC_REGISTRY_VERSION: Final = "1.0.0"
SYNTHETIC_REGISTRY_DIGEST: Final = "0" * 64


def two_significant_figure_floor(value: float, exponent: int) -> float:
    """Return a value truncated, not rounded, to two significant figures.

    Parameters
    ----------
    value
        The value to truncate; strictly positive.
    exponent
        Power of ten the value's leading digit sits at, so the answer
        comes back at the same scale as the printed constant it is
        compared against.

    Returns
    -------
    float
        The truncation.

    Notes
    -----
    The volume truncates rather than rounds, measured on two independent
    values, so this is the operation its printed figures are the result
    of. Rounding would disagree with both.
    """
    scale = 10.0 ** (1 - exponent)
    return math.floor(value * scale) / scale


def registry_binding() -> RegistryBinding:
    """Build the synthetic registry pin the fixtures share.

    Returns
    -------
    RegistryBinding
        A well-formed pin; its digest is synthetic and pins nothing.
    """
    return RegistryBinding(
        version=SYNTHETIC_REGISTRY_VERSION,
        digest_sha256=SYNTHETIC_REGISTRY_DIGEST,
    )


def anchor_configuration() -> DeviceConfiguration:
    """Build the configuration the anchors are evaluated on.

    Returns
    -------
    DeviceConfiguration
        The plate mass and velocity of the worked plane case, and the
        target radius of the convergent one. The two come from two
        papers and the record's non-claims say so.
    """
    return DeviceConfiguration(
        identifier="projectile_or_impact_icf",
        projectile=Projectile(
            mass_mg=DERIVED_CHRISTIANSEN_PLATE_MASS_MG,
            velocity_km_s=PRINTED_CHRISTIANSEN_VELOCITY_KM_S,
        ),
        target=TargetDeclaration(target_radius_um=PRINTED_MARSHALL_SPHERE_RADIUS_UM),
        registry=registry_binding(),
    )


def anchor_fuel() -> FuelDeclaration:
    """Build the fuel states the worked plane case prints.

    Returns
    -------
    FuelDeclaration
        The cryogenic reference density, the gas pressure and
        temperature before impact, and the first and fourth density
        ratios of the printed four-state chain.
    """
    return FuelDeclaration(
        cryogenic_density_g_cm3=PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3,
        initial_pressure_bar=PRINTED_CHRISTIANSEN_INITIAL_PRESSURE_BAR,
        initial_temperature_k=PRINTED_CHRISTIANSEN_INITIAL_TEMPERATURE_K,
        initial_density_ratio=PRINTED_CHRISTIANSEN_DENSITY_RATIOS[0],
        compressed_density_ratio=PRINTED_CHRISTIANSEN_DENSITY_RATIOS[3],
    )


def anchor_projectile() -> ProjectileDeclaration:
    """Build the plate material and face the worked case prints.

    Returns
    -------
    ProjectileDeclaration
        Uranium at its printed density, presenting the printed face. The
        mass and the velocity are not here; they belong to the
        configuration.
    """
    return ProjectileDeclaration(
        material_density_g_cm3=PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3,
        impact_area_cm2=PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2,
    )


def anchor_scheme() -> SchemeDeclaration:
    """Build the dimensions of the two printed geometries.

    Returns
    -------
    SchemeDeclaration
        The plane case's fuel thickness and the convergent case's radial
        compression factor. The convergent target's own radius is not
        here; it belongs to the configuration.
    """
    return SchemeDeclaration(
        slab_thickness_cm=PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM,
        radial_compression_factor=PRINTED_MARSHALL_RADIAL_COMPRESSION_FACTOR,
    )
