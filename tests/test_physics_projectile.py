# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tests for what the flying plate carries

"""What the plate carries, against the worked case that prints it."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    DERIVED_CHRISTIANSEN_PLATE_MASS_MG,
    PRINTED_CHRISTIANSEN_ENERGY_PER_AREA_MJ_PER_CM2,
    PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2,
    PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2,
    PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM,
    PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3,
    PRINTED_CHRISTIANSEN_VELOCITY_KM_S,
    anchor_configuration,
    two_significant_figure_floor,
)
from scpn_icf_impact_core.errors import DeviceConfigurationError
from scpn_icf_impact_core.physics.projectile import (
    areal_density_g_cm2,
    energy_per_area_mj_per_cm2,
    plate_thickness_cm,
)

#: Relative agreement of the two megajoule quantities with the value the
#: volume prints. Measured before it was written: neither is exact, and
#: both miss by one unit in the last place of a double.
PRINTED_MEGAJOULE_TOLERANCE = 1.0e-15


def test_the_plate_areal_density_reproduces_the_printed_value() -> None:
    """The plate's mass over its face is the areal density printed."""
    assert (
        areal_density_g_cm2(
            DERIVED_CHRISTIANSEN_PLATE_MASS_MG, PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2
        )
        == PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2
    )


def test_the_areal_density_falls_as_the_face_widens() -> None:
    """The same mass over twice the face carries half as much."""
    one = areal_density_g_cm2(DERIVED_CHRISTIANSEN_PLATE_MASS_MG, 1.0)
    two = areal_density_g_cm2(DERIVED_CHRISTIANSEN_PLATE_MASS_MG, 2.0)
    assert two == pytest.approx(one / 2.0, rel=1e-15)


def test_the_printed_plate_thickness_is_a_truncation_and_not_a_rounding() -> None:
    """The volume truncates the thickness its own relation gives.

    Measured: the relation gives 2.7659e-3 cm, the volume prints
    2.7e-3, and rounding to the same two significant figures would have
    given 2.8e-3. A test asserting rounding would have failed here.
    """
    thickness = plate_thickness_cm(
        PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2,
        PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3,
    )
    assert thickness == pytest.approx(2.7659574e-3, rel=1e-7)
    assert two_significant_figure_floor(thickness, -3) == pytest.approx(
        PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM, rel=1e-15
    )
    rounded = round(thickness * 1.0e3, 1) * 1.0e-3
    assert rounded != pytest.approx(PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM, rel=1e-9)
    assert rounded == pytest.approx(2.8e-3, rel=1e-9)


def test_a_denser_plate_material_carries_the_same_mass_in_less_thickness() -> None:
    """Thickness is the areal density a chosen material has to fill."""
    dense = plate_thickness_cm(PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2, 18.8)
    light = plate_thickness_cm(PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2, 9.4)
    assert light == pytest.approx(2.0 * dense, rel=1e-15)


def test_the_energy_per_area_reproduces_the_printed_value_as_a_bound() -> None:
    """The printed energy per unit area comes back, and not exactly.

    Measured before it was written: the product misses 1.04 by one unit
    in the last place, so this is a bound and the test says so rather
    than asserting an equality that would be false.
    """
    delivered = energy_per_area_mj_per_cm2(
        PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2,
        anchor_configuration().projectile.specific_kinetic_energy_j_kg(),
    )
    assert delivered != PRINTED_CHRISTIANSEN_ENERGY_PER_AREA_MJ_PER_CM2
    assert delivered == pytest.approx(
        PRINTED_CHRISTIANSEN_ENERGY_PER_AREA_MJ_PER_CM2,
        rel=PRINTED_MEGAJOULE_TOLERANCE,
    )


def test_the_delivered_energy_is_the_whole_kinetic_energy_of_the_plate() -> None:
    """Spreading the energy over the face neither adds nor loses any.

    The parameter model owns the kinetic energy and this module owns the
    spreading; over the printed one-square-centimetre face the two must
    agree bit for bit, which is what shows the energy is not being
    recomputed by a second route.
    """
    projectile = anchor_configuration().projectile
    delivered = energy_per_area_mj_per_cm2(
        PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2,
        projectile.specific_kinetic_energy_j_kg(),
    )
    over_the_face = delivered * PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2
    assert over_the_face == projectile.kinetic_energy_kj() / 1.0e3


def test_the_specific_energy_is_the_square_of_the_printed_speed() -> None:
    """The plate's specific kinetic energy is ``v^2 / 2``, in SI."""
    metres_per_second = PRINTED_CHRISTIANSEN_VELOCITY_KM_S * 1.0e3
    assert anchor_configuration().projectile.specific_kinetic_energy_j_kg() == (
        0.5 * metres_per_second**2
    )


@pytest.mark.parametrize(
    ("mass_mg", "impact_area_cm2", "field"),
    [
        (0.0, 1.0, "mass_mg"),
        (-1.0, 1.0, "mass_mg"),
        (math.nan, 1.0, "mass_mg"),
        (52.0, 0.0, "impact_area_cm2"),
        (52.0, -1.0, "impact_area_cm2"),
        (52.0, math.inf, "impact_area_cm2"),
    ],
)
def test_the_areal_density_refuses_an_unusable_plate(
    mass_mg: float, impact_area_cm2: float, field: str
) -> None:
    """Every input of the areal density is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        areal_density_g_cm2(mass_mg, impact_area_cm2)


@pytest.mark.parametrize(
    ("areal", "density", "field"),
    [
        (0.0, 18.8, "areal_density_g_cm2"),
        (math.nan, 18.8, "areal_density_g_cm2"),
        (0.052, 0.0, "material_density_g_cm3"),
        (0.052, -18.8, "material_density_g_cm3"),
    ],
)
def test_the_thickness_refuses_an_unusable_input(
    areal: float, density: float, field: str
) -> None:
    """Every input of the thickness relation is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        plate_thickness_cm(areal, density)


@pytest.mark.parametrize(
    ("areal", "specific", "field"),
    [
        (0.0, 2.0e10, "areal_density_g_cm2"),
        (-0.052, 2.0e10, "areal_density_g_cm2"),
        (0.052, 0.0, "specific_kinetic_energy_j_per_kg"),
        (0.052, math.nan, "specific_kinetic_energy_j_per_kg"),
    ],
)
def test_the_delivered_energy_refuses_an_unusable_input(
    areal: float, specific: float, field: str
) -> None:
    """Every input of the delivered-energy relation is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        energy_per_area_mj_per_cm2(areal, specific)
