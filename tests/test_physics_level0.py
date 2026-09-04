# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tests for the composed level-0 record

"""The composed level-0 record, and the boundaries it declares."""

from __future__ import annotations

import json
import math
from dataclasses import replace

import pytest

from physics_fixtures import (
    NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG,
    PRINTED_CHRISTIANSEN_COMPRESSED_THICKNESS_CM,
    PRINTED_CHRISTIANSEN_ENERGY_PER_AREA_MJ_PER_CM2,
    PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2,
    PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM,
    PRINTED_MARSHALL_AREAL_DENSITY_G_CM2,
    PRINTED_MARSHALL_SPHERE_RADIUS_UM,
    anchor_configuration,
    anchor_fuel,
    anchor_projectile,
    anchor_scheme,
    two_significant_figure_floor,
)
from scpn_icf_impact_core.errors import DeviceConfigurationError
from scpn_icf_impact_core.physics.level0 import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    FuelDeclaration,
    Level0Physics,
    ProjectileDeclaration,
    SchemeDeclaration,
    level0_physics,
    target_radius_cm,
)

#: Relative agreement of the two megajoule quantities with the printed
#: value; measured, and not exact.
PRINTED_MEGAJOULE_TOLERANCE = 1.0e-15


def anchor_record() -> Level0Physics:
    """Compose the record every anchor below is read from.

    Returns
    -------
    Level0Physics
        The record built from the four anchor declarations.
    """
    return level0_physics(
        anchor_configuration(), anchor_fuel(), anchor_projectile(), anchor_scheme()
    )


def test_the_target_radius_is_converted_exactly_once() -> None:
    """Micrometres become centimetres here and nowhere else."""
    assert target_radius_cm(anchor_configuration()) == pytest.approx(
        PRINTED_MARSHALL_SPHERE_RADIUS_UM / 1.0e4, rel=1e-15
    )
    assert anchor_record().operating_point.sphere_radius_cm == target_radius_cm(
        anchor_configuration()
    )


def test_the_plate_anchors_come_back_through_the_composition() -> None:
    """The printed plate values survive the composed record.

    The areal density is exact; the two megajoule quantities are bounds,
    measured as such before they were written.
    """
    point = anchor_record().operating_point
    assert (
        point.projectile_areal_density_g_cm2
        == PRINTED_CHRISTIANSEN_PLATE_AREAL_DENSITY_G_CM2
    )
    assert point.projectile_energy_per_area_mj_per_cm2 == pytest.approx(
        PRINTED_CHRISTIANSEN_ENERGY_PER_AREA_MJ_PER_CM2,
        rel=PRINTED_MEGAJOULE_TOLERANCE,
    )
    assert point.projectile_energy_per_area_mj_per_cm2 != (
        PRINTED_CHRISTIANSEN_ENERGY_PER_AREA_MJ_PER_CM2
    )
    assert two_significant_figure_floor(
        point.projectile_thickness_cm, -3
    ) == pytest.approx(PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM, rel=1e-15)


def test_the_kinetic_energy_and_the_delivered_energy_are_one_quantity() -> None:
    """Over the printed face the two agree bit for bit.

    They are computed by two different routes — the parameter model's
    ``m v^2 / 2`` and this package's areal density times ``v^2 / 2`` —
    and over a face of one square centimetre they must not diverge.
    """
    point = anchor_record().operating_point
    assert point.projectile_kinetic_energy_mj == (
        point.projectile_energy_per_area_mj_per_cm2
    )


def test_the_slab_anchors_come_back_through_the_composition() -> None:
    """The printed compressed thickness survives as its truncation."""
    point = anchor_record().operating_point
    assert point.slab_compression_ratio == pytest.approx(420.0, rel=1e-13)
    assert two_significant_figure_floor(
        point.compressed_slab_thickness_cm, -3
    ) == pytest.approx(PRINTED_CHRISTIANSEN_COMPRESSED_THICKNESS_CM, rel=1e-15)
    assert point.initial_fuel_density_g_cm3 == pytest.approx(2.13e-3, rel=1e-15)
    assert point.slab_fuel_mass_mg == pytest.approx(2.13, rel=1e-15)


def test_the_sphere_areal_density_is_the_convergent_paper_s_one_anchor() -> None:
    """Its printed 2 g/cm2 comes back; its printed mass does not.

    Both statements are about the same sphere in the same sentence of
    the same paper, and only one of them reproduces on the cryogenic
    density the volume prints elsewhere. The record carries both
    quantities and this test states which is which.
    """
    point = anchor_record().operating_point
    assert point.sphere_areal_density_g_cm2 == pytest.approx(2.13, rel=1e-12)
    assert math.floor(point.sphere_areal_density_g_cm2) == (
        PRINTED_MARSHALL_AREAL_DENSITY_G_CM2
    )
    assert point.sphere_fuel_mass_mg > NOT_REPRODUCED_MARSHALL_SPHERE_MASS_MG
    assert point.sphere_fuel_mass_mg == pytest.approx(0.8922123, rel=1e-6)


def test_the_convergent_target_beats_the_plane_one_by_a_thousand() -> None:
    """The two schemes' areal densities differ by three orders.

    That ratio is the quantitative content of the convergent paper's
    verdict on the plane scheme, and it is a property of these two
    declared targets rather than a general result.
    """
    point = anchor_record().operating_point
    assert point.convergence_areal_density_ratio == pytest.approx(1000.0, rel=1e-13)
    assert point.sphere_areal_density_g_cm2 > point.slab_areal_density_g_cm2


def test_the_plate_outweighs_the_fuel_it_drives() -> None:
    """The plate carries more mass per unit area than the fuel does.

    The volume solves its own equation for exactly this quantity, and
    states in words that the plate must have "sufficient mass of the
    projectile for a given mass of DT". The ratio is reported and not
    enforced: the volume's criterion is an equation this repository does
    not carry, and refusing on a threshold it never printed would be an
    invention.
    """
    point = anchor_record().operating_point
    assert point.driven_areal_density_ratio == pytest.approx(24.4131, rel=1e-5)
    assert point.driven_areal_density_ratio == pytest.approx(
        point.projectile_areal_density_g_cm2 / point.slab_areal_density_g_cm2,
        rel=1e-15,
    )


def test_the_full_burn_energies_bound_both_inventories() -> None:
    """Each inventory's complete burn, and nothing about what burns."""
    point = anchor_record().operating_point
    assert point.slab_full_burn_energy_mj == pytest.approx(718.8192, rel=1e-6)
    assert point.sphere_full_burn_energy_mj == pytest.approx(301.0983, rel=1e-6)
    assert point.slab_full_burn_energy_mj > point.sphere_full_burn_energy_mj


def test_the_anchor_velocity_clears_the_configuration_s_own_floor() -> None:
    """The printed 200 km/s raises no consistency finding.

    The configuration flags a projectile below the impact-fusion entry
    scale. The worked case's plate is twice that scale, so the record is
    composed on a configuration the repository's own advisory instrument
    is content with.
    """
    assert anchor_configuration().consistency_report() == ()


def test_the_record_carries_the_configuration_it_was_built_from() -> None:
    """The record names the exact configuration digest."""
    configuration = anchor_configuration()
    record = level0_physics(
        configuration, anchor_fuel(), anchor_projectile(), anchor_scheme()
    )
    assert record.configuration_digest_sha256 == configuration.digest_sha256()


def test_the_record_serialises_canonically_and_identifies_itself() -> None:
    """Sorted keys, one trailing newline, and a digest of those bytes."""
    record = anchor_record()
    data = record.canonical_bytes()
    assert data.endswith(b"\n")
    assert b"NaN" not in data
    assert b"Infinity" not in data
    decoded = json.loads(data.decode("utf-8"))
    assert list(decoded) == sorted(decoded)
    assert decoded["schema"] == LEVEL0_SCHEMA
    assert decoded["schema_version"] == LEVEL0_SCHEMA_VERSION
    assert decoded["non_claims"] == list(LEVEL0_NON_CLAIMS)
    assert record.digest_sha256() == anchor_record().digest_sha256()


def test_the_record_projects_every_declaration_it_was_given() -> None:
    """Each declaration appears in the record under its own key."""
    decoded = json.loads(anchor_record().canonical_bytes().decode("utf-8"))
    assert decoded["fuel"] == anchor_fuel().to_record()
    assert decoded["projectile"] == anchor_projectile().to_record()
    assert decoded["scheme"] == anchor_scheme().to_record()
    assert set(decoded["operating_point"]) == set(
        anchor_record().operating_point.to_record()
    )


def test_a_different_target_moves_the_digest() -> None:
    """A record identifies its inputs, not merely its schema."""
    configuration = anchor_configuration()
    other = replace(
        configuration,
        target=replace(configuration.target, target_radius_um=2.0e3),
    )
    moved = level0_physics(other, anchor_fuel(), anchor_projectile(), anchor_scheme())
    assert moved.digest_sha256() != anchor_record().digest_sha256()
    assert moved.operating_point.sphere_fuel_mass_mg > (
        anchor_record().operating_point.sphere_fuel_mass_mg
    )


def test_the_non_claims_say_the_two_schemes_are_not_one_design() -> None:
    """The boundary that matters most is stated in the record itself.

    A reader who finds a plate and a sphere in one record must be able
    to learn from the record that no filed source pairs them, rather
    than inferring a design that no paper describes.
    """
    joined = " ".join(LEVEL0_NON_CLAIMS)
    assert "no filed source pairs them" in joined
    assert "prints no projectile for it" in joined
    assert "no shock is solved" in joined
    assert "burn-up fraction" in joined
    assert "consistency instrument" in joined


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("cryogenic_density_g_cm3", 0.0),
        ("cryogenic_density_g_cm3", math.nan),
        ("initial_pressure_bar", -10.0),
        ("initial_temperature_k", 0.0),
        ("initial_density_ratio", 0.0),
    ],
)
def test_the_fuel_declaration_refuses_an_unusable_value(
    field: str, value: float
) -> None:
    """Every declared fuel field is validated where it is declared."""
    with pytest.raises(DeviceConfigurationError, match=field):
        replace(anchor_fuel(), **{field: value})


def test_the_fuel_declaration_refuses_a_gas_at_the_cryogenic_density() -> None:
    """A gas ratio at or above one is not the declared gas.

    Refused where it is declared, so a record can never be composed from
    a state the relations would reject one at a time.
    """
    with pytest.raises(DeviceConfigurationError, match=r"below 1\.0"):
        replace(anchor_fuel(), initial_density_ratio=1.0)


@pytest.mark.parametrize("compressed", [0.01, 0.001])
def test_the_fuel_declaration_refuses_a_state_that_is_not_a_compression(
    compressed: float,
) -> None:
    """A final state at or below the initial one is refused."""
    with pytest.raises(
        DeviceConfigurationError, match="must exceed initial_density_ratio"
    ):
        replace(anchor_fuel(), compressed_density_ratio=compressed)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("material_density_g_cm3", 0.0),
        ("material_density_g_cm3", -18.8),
        ("impact_area_cm2", 0.0),
        ("impact_area_cm2", math.inf),
    ],
)
def test_the_projectile_declaration_refuses_an_unusable_value(
    field: str, value: float
) -> None:
    """Every declared plate field is validated where it is declared."""
    with pytest.raises(DeviceConfigurationError, match=field):
        replace(anchor_projectile(), **{field: value})


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("slab_thickness_cm", 0.0, "slab_thickness_cm"),
        ("slab_thickness_cm", math.nan, "slab_thickness_cm"),
        ("radial_compression_factor", 1.0, "must exceed 1.0"),
        ("radial_compression_factor", 0.5, "must exceed 1.0"),
    ],
)
def test_the_scheme_declaration_refuses_an_unusable_value(
    field: str, value: float, message: str
) -> None:
    """Every declared dimension is validated where it is declared."""
    with pytest.raises(DeviceConfigurationError, match=message):
        replace(anchor_scheme(), **{field: value})


@pytest.mark.parametrize(
    ("declaration", "field"),
    [
        (anchor_fuel(), "cryogenic_density_g_cm3"),
        (anchor_projectile(), "impact_area_cm2"),
        (anchor_scheme(), "slab_thickness_cm"),
    ],
)
def test_the_declarations_are_frozen(declaration: object, field: str) -> None:
    """A composed record cannot be edited out from under its digest.

    Each declaration is tested on a field it actually owns, so that the
    refusal comes from the declaration being frozen and not from the
    field being absent.
    """
    with pytest.raises(AttributeError):
        setattr(declaration, field, 2.0)


def test_the_declarations_accept_the_printed_values() -> None:
    """The anchor declarations are built without a refusal."""
    assert isinstance(anchor_fuel(), FuelDeclaration)
    assert isinstance(anchor_projectile(), ProjectileDeclaration)
    assert isinstance(anchor_scheme(), SchemeDeclaration)
