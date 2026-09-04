# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tests for the fuel in two geometries

"""The fuel, against the two papers that print it."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    NOT_REPRODUCED_MARSHALL_GRAM_BURN_GJ,
    NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG,
    PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3,
    PRINTED_CHRISTIANSEN_DENSITY_RATIOS,
    PRINTED_CHRISTIANSEN_INITIAL_PRESSURE_BAR,
    PRINTED_CHRISTIANSEN_INITIAL_TEMPERATURE_K,
    PRINTED_CHRISTIANSEN_SHOCKED_PRESSURES_MB,
    PRINTED_CHRISTIANSEN_SHOCKED_TEMPERATURES_EV,
    PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM,
    PRINTED_MARSHALL_AREAL_DENSITY_G_CM2,
)
from scpn_icf_impact_core.errors import DeviceConfigurationError
from scpn_icf_impact_core.physics.fuel import (
    ATOMIC_MASS_UNIT_KG,
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

#: The sphere radius Marshall prints, in the centimetres this module
#: works in rather than the micrometres the configuration carries.
MARSHALL_SPHERE_RADIUS_CM = 0.1
#: Measured specific energy of the fuel, in gigajoules per gram.
MEASURED_SPECIFIC_ENERGY_GJ_PER_G = 337.4738
#: Measured mass of the printed sphere at the printed cryogenic density.
MEASURED_MARSHALL_SPHERE_MASS_MG = 0.8922123
#: Density the printed sphere mass implies instead.
IMPLIED_MARSHALL_DENSITY_G_CM3 = 0.2005


def test_the_molecule_mass_is_the_two_nuclear_masses() -> None:
    """A reacting pair is one deuteron and one triton, and nothing else."""
    assert dt_molecule_mass_u() == DEUTERON_MASS_U + TRITON_MASS_U


def test_the_specific_energy_is_built_from_its_inputs() -> None:
    """The specific energy is computed, not a rounded constant.

    Asserting the closed form rather than a literal is what makes the
    provenance testable: changing either nuclear mass or the released
    energy per reaction moves this answer.
    """
    pair_mass_g = dt_molecule_mass_u() * ATOMIC_MASS_UNIT_KG * 1.0e3
    assert dt_specific_energy_j_per_g() == (
        DT_FUSION_ENERGY_MEV * MEGAELECTRONVOLT_J / pair_mass_g
    )


def test_the_printed_one_gram_burn_does_not_reproduce() -> None:
    """The volume's one-gram burn energy is not what the masses give.

    Measured: 337.5 GJ against a printed "nearly 400 GJ", about 19 %
    apart. Recorded rather than absorbed into a tolerance, and used as
    an anchor nowhere.
    """
    measured_gj = dt_specific_energy_j_per_g() / 1.0e9
    assert measured_gj == pytest.approx(MEASURED_SPECIFIC_ENERGY_GJ_PER_G, rel=1e-6)
    assert measured_gj < NOT_REPRODUCED_MARSHALL_GRAM_BURN_GJ
    assert NOT_REPRODUCED_MARSHALL_GRAM_BURN_GJ / measured_gj > 1.15


def test_the_printed_density_ratio_is_consistent_with_its_gas_state() -> None:
    """The printed pressure, temperature and ratio agree to one figure.

    Measured: the ideal-gas law on the printed 10 bar and 300 K gives
    0.009466 of the cryogenic density against a printed 0.01, so the
    three printed values are mutually consistent at the one significant
    figure the ratio carries and disagree by 5.3 % below it. The
    calculation assumes an ideal gas of diatomic molecules, which the
    volume does not state, so this is a consistency instrument and not
    an anchor.
    """
    density = ideal_gas_density_g_cm3(
        PRINTED_CHRISTIANSEN_INITIAL_PRESSURE_BAR,
        PRINTED_CHRISTIANSEN_INITIAL_TEMPERATURE_K,
    )
    ratio = density / PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3
    assert ratio == pytest.approx(0.009466, rel=1e-4)
    assert round(ratio, 2) == PRINTED_CHRISTIANSEN_DENSITY_RATIOS[0]
    assert ratio != pytest.approx(PRINTED_CHRISTIANSEN_DENSITY_RATIOS[0], rel=1e-2)


def test_the_gas_density_follows_its_two_state_variables() -> None:
    """Check that the gas density follows both of its state variables.

    Doubling the pressure doubles the density and doubling the
    temperature halves it, which is what shows neither has been dropped
    from the relation.
    """
    base = ideal_gas_density_g_cm3(10.0, 300.0)
    assert ideal_gas_density_g_cm3(20.0, 300.0) == pytest.approx(2.0 * base, rel=1e-15)
    assert ideal_gas_density_g_cm3(10.0, 600.0) == pytest.approx(base / 2.0, rel=1e-15)


def test_the_printed_states_rise_monotonically() -> None:
    """Every shocked state the volume prints is above the one before it.

    The record takes only the first and the fourth of these. The chain
    between them is a shock solution this repository does not perform,
    and this test states the one property of it that can be checked
    without performing it.
    """
    ratios = PRINTED_CHRISTIANSEN_DENSITY_RATIOS
    assert list(ratios) == sorted(ratios)
    pressures = PRINTED_CHRISTIANSEN_SHOCKED_PRESSURES_MB
    assert list(pressures) == sorted(pressures)
    temperatures = PRINTED_CHRISTIANSEN_SHOCKED_TEMPERATURES_EV
    assert list(temperatures) == sorted(temperatures)


def test_the_absolute_densities_come_from_the_printed_ratios() -> None:
    """The initial and compressed densities are the printed multiples."""
    assert density_from_ratio_g_cm3(
        PRINTED_CHRISTIANSEN_DENSITY_RATIOS[0],
        PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3,
    ) == pytest.approx(2.13e-3, rel=1e-15)
    assert density_from_ratio_g_cm3(
        PRINTED_CHRISTIANSEN_DENSITY_RATIOS[3],
        PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3,
    ) == pytest.approx(0.8946, rel=1e-15)


def test_the_slab_areal_density_is_its_density_times_its_thickness() -> None:
    """The plane target's areal density along the plate's direction."""
    initial = density_from_ratio_g_cm3(
        PRINTED_CHRISTIANSEN_DENSITY_RATIOS[0],
        PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3,
    )
    assert slab_areal_density_g_cm2(
        PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM, initial
    ) == pytest.approx(2.13e-3, rel=1e-15)


def test_the_slab_mass_scales_with_every_dimension_it_is_given() -> None:
    """Thickness, cross-section and density each enter once."""
    base = slab_mass_mg(1.0, 1.0, 2.13e-3)
    assert base == pytest.approx(2.13, rel=1e-15)
    assert slab_mass_mg(2.0, 1.0, 2.13e-3) == pytest.approx(2.0 * base, rel=1e-15)
    assert slab_mass_mg(1.0, 3.0, 2.13e-3) == pytest.approx(3.0 * base, rel=1e-15)
    assert slab_mass_mg(1.0, 1.0, 4.26e-3) == pytest.approx(2.0 * base, rel=1e-15)


def test_the_printed_sphere_mass_does_not_reproduce() -> None:
    """The volume's 0.84 mg is not what its own density gives.

    Measured: a 1 mm sphere at the printed cryogenic density masses
    0.8922 mg, 6.2 % above the printed value, and the printed value
    needs about 0.2005 g/cm3 instead. The relation is not adjusted and
    the printed mass is used as an anchor nowhere.
    """
    mass = sphere_mass_mg(
        MARSHALL_SPHERE_RADIUS_CM, PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3
    )
    assert mass == pytest.approx(MEASURED_MARSHALL_SPHERE_MASS_MG, rel=1e-6)
    assert mass > NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG
    assert (mass - NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG) / mass == pytest.approx(
        0.0585, rel=1e-2
    )
    volume_cm3 = 4.0 / 3.0 * math.pi * MARSHALL_SPHERE_RADIUS_CM**3
    implied = NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG / 1.0e3 / volume_cm3
    assert implied == pytest.approx(IMPLIED_MARSHALL_DENSITY_G_CM3, rel=1e-3)


def test_the_printed_compressed_areal_density_reproduces_to_its_one_figure() -> None:
    """The volume's 2 g/cm2 comes back as 2.13 at one significant figure.

    Unlike the sphere's mass, this statement does reproduce on the
    printed cryogenic density, so it is the one anchor the convergent
    paper supplies.
    """
    compressed_density = PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3 * 1.0e3
    compressed_radius = MARSHALL_SPHERE_RADIUS_CM / 10.0
    areal = sphere_areal_density_g_cm2(compressed_radius, compressed_density)
    assert areal == pytest.approx(2.13, rel=1e-12)
    assert math.floor(areal) == PRINTED_MARSHALL_AREAL_DENSITY_G_CM2
    assert round(areal) == PRINTED_MARSHALL_AREAL_DENSITY_G_CM2


def test_the_full_burn_energy_is_the_inventory_times_the_specific_energy() -> None:
    """A complete burn releases exactly what the inventory holds."""
    assert full_burn_energy_mj(1.0e3) == pytest.approx(
        dt_specific_energy_j_per_g() / 1.0e6, rel=1e-15
    )
    assert full_burn_energy_mj(2.13) == pytest.approx(718.8192, rel=1e-6)


@pytest.mark.parametrize("value", [0.01, 0.5, 0.999999])
def test_a_gas_below_the_cryogenic_density_is_accepted(value: float) -> None:
    """A ratio inside ``(0, 1)`` passes through unchanged."""
    assert require_below_unity("initial_density_ratio", value) == value


@pytest.mark.parametrize("value", [1.0, 4.2, math.inf])
def test_a_gas_at_or_above_the_cryogenic_density_is_refused(value: float) -> None:
    """Fuel at its own liquid density is not the declared gas."""
    with pytest.raises(DeviceConfigurationError, match=r"below 1\.0|must be finite"):
        require_below_unity("initial_density_ratio", value)


@pytest.mark.parametrize("value", [0.0, -0.5])
def test_a_non_positive_ratio_is_refused_before_the_unity_check(
    value: float,
) -> None:
    """Positivity is checked first, and names the same field."""
    with pytest.raises(DeviceConfigurationError, match="strictly positive"):
        require_below_unity("initial_density_ratio", value)


@pytest.mark.parametrize(
    ("pressure", "temperature", "field"),
    [
        (0.0, 300.0, "pressure_bar"),
        (math.nan, 300.0, "pressure_bar"),
        (10.0, 0.0, "temperature_k"),
        (10.0, -300.0, "temperature_k"),
    ],
)
def test_the_gas_density_refuses_an_unusable_state(
    pressure: float, temperature: float, field: str
) -> None:
    """Every input of the gas relation is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        ideal_gas_density_g_cm3(pressure, temperature)


@pytest.mark.parametrize(
    ("ratio", "reference", "field"),
    [
        (0.0, 0.213, "density_ratio"),
        (-0.01, 0.213, "density_ratio"),
        (0.01, 0.0, "reference_density_g_cm3"),
        (0.01, math.inf, "reference_density_g_cm3"),
    ],
)
def test_the_density_from_a_ratio_refuses_an_unusable_input(
    ratio: float, reference: float, field: str
) -> None:
    """Every input of the ratio relation is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        density_from_ratio_g_cm3(ratio, reference)


@pytest.mark.parametrize(
    ("thickness", "density", "field"),
    [
        (0.0, 2.13e-3, "thickness_cm"),
        (math.nan, 2.13e-3, "thickness_cm"),
        (1.0, 0.0, "density_g_cm3"),
        (1.0, -1.0, "density_g_cm3"),
    ],
)
def test_the_slab_areal_density_refuses_an_unusable_input(
    thickness: float, density: float, field: str
) -> None:
    """Every input of the slab areal density is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        slab_areal_density_g_cm2(thickness, density)


@pytest.mark.parametrize(
    ("thickness", "area", "density", "field"),
    [
        (0.0, 1.0, 2.13e-3, "thickness_cm"),
        (1.0, 0.0, 2.13e-3, "area_cm2"),
        (1.0, math.inf, 2.13e-3, "area_cm2"),
        (1.0, 1.0, 0.0, "density_g_cm3"),
    ],
)
def test_the_slab_mass_refuses_an_unusable_input(
    thickness: float, area: float, density: float, field: str
) -> None:
    """Every input of the slab mass is refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        slab_mass_mg(thickness, area, density)


@pytest.mark.parametrize(
    ("radius", "density", "field"),
    [
        (0.0, 0.213, "radius_cm"),
        (-0.1, 0.213, "radius_cm"),
        (0.1, 0.0, "density_g_cm3"),
        (0.1, math.nan, "density_g_cm3"),
    ],
)
def test_the_sphere_relations_refuse_an_unusable_input(
    radius: float, density: float, field: str
) -> None:
    """Both sphere relations refuse the same inputs by the same names."""
    with pytest.raises(DeviceConfigurationError, match=field):
        sphere_mass_mg(radius, density)
    with pytest.raises(DeviceConfigurationError, match=field):
        sphere_areal_density_g_cm2(radius, density)


@pytest.mark.parametrize("mass", [0.0, -1.0, math.inf])
def test_the_full_burn_energy_refuses_an_unusable_inventory(mass: float) -> None:
    """An inventory that is not a positive mass is refused by name."""
    with pytest.raises(DeviceConfigurationError, match="fuel_mass_mg"):
        full_burn_energy_mj(mass)
