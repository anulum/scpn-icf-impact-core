# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tier-G1 device model tests

"""Tier-G1 tessellated models of the two published schemes.

The anchor tests recover printed dimensions **from the built bodies**,
not from the configuration they were built out of: a value that only
round-trips through a declaration proves nothing about a body.
"""

from __future__ import annotations

import json
import math
from typing import Final

import pytest

from geometry_fixtures import (
    ANCHOR_CROSS_SECTION_SIDE_M,
    ANCHOR_RINGS,
    ANCHOR_SEGMENTS,
    ANCHOR_SLAB_THICKNESS_M,
    ANCHOR_SPHERE_RADIUS_M,
    DERIVED_CHRISTIANSEN_PLATE_MASS_MG,
    PRINTED_CHRISTIANSEN_CROSS_SECTION_SIDE_CM,
    PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2,
    PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM,
    PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3,
    PRINTED_MARSHALL_SPHERE_RADIUS_UM,
    anchor_configuration,
    anchor_fuel,
    anchor_projectile,
    anchor_scheme,
    two_significant_figure_floor,
)
from scpn_icf_impact_core.configuration import DeviceConfiguration
from scpn_icf_impact_core.errors import DeviceConfigurationError, DeviceGeometryError
from scpn_icf_impact_core.geometry import (
    BODY_DRIVER_PLATE,
    BODY_FUEL_SLAB,
    BODY_FUEL_SPHERE,
    BODY_NAMES_BY_SCHEME,
    CENTIMETRE_M,
    MATERIAL_FUEL_GAS,
    MATERIAL_SOLID_FUEL,
    MATERIAL_URANIUM_PLATE,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS_BY_SCHEME,
    REFINABLE_SCHEMES,
    ROLE_DRIVER,
    ROLE_FUEL,
    SCHEME_CONVERGENT,
    SCHEME_PLANE,
    SCHEMES_BY_IDENTIFIER,
    SCHEMES_CONSUMING_DECLARATIONS,
    DeviceModel3D,
    build_convergent_model,
    build_plane_model,
    convergent_radius_m,
    plane_extents_m,
    square_side_cm,
)
from scpn_icf_impact_core.parameters import Projectile
from scpn_icf_impact_core.physics.level0 import level0_physics

#: Milligrams in a gram, for turning a built volume and a printed
#: density back into the mass the configuration declares.
MILLIGRAMS_PER_GRAM: Final = 1.0e3
#: Cubic centimetres in a cubic metre.
CUBIC_CENTIMETRES_PER_CUBIC_METRE: Final = 1.0e6
#: Exponent of the printed plate thickness, for the volume's floor.
PLATE_THICKNESS_EXPONENT: Final = -3
#: How far the tier-G1 body falls short of an ideal sphere of the same
#: radius, at the declared counts. Measured: the inscribed polyhedron
#: is a tenth smaller, which is why the non-claim exists.
MEASURED_IDEAL_SPHERE_SHORTFALL: Final = 0.10172203483702759
#: A plate mass and a material density that are each individually
#: valid and whose quotient underflows to exactly zero.
UNDERFLOWING_PLATE_MASS_MG: Final = 1.0e-300
UNDERFLOWING_PLATE_DENSITY_G_CM3: Final = 1.0e300


def plane_model() -> DeviceModel3D:
    """Build the plane scheme's anchor model.

    Returns
    -------
    DeviceModel3D
        The two-body model of the worked plane case.
    """
    return build_plane_model(
        anchor_configuration(), anchor_projectile(), anchor_scheme()
    )


def convergent_model() -> DeviceModel3D:
    """Build the convergent scheme's anchor model.

    Returns
    -------
    DeviceModel3D
        The one-body model of the convergent target.
    """
    return build_convergent_model(anchor_configuration(), ANCHOR_SEGMENTS, ANCHOR_RINGS)


def extent(model: DeviceModel3D, name: str, axis: int) -> float:
    """Return one body's extent along one axis, from its vertices.

    Parameters
    ----------
    model
        The built model.
    name
        Body name.
    axis
        0 for ``x``, 1 for ``y``, 2 for ``z``.

    Returns
    -------
    float
        The difference between the largest and smallest coordinate of
        the body's vertices along that axis, in metres.
    """
    mesh = next(each for each in model.meshes if each.name == name)
    values = [vertex[axis] for vertex in mesh.vertices]
    return max(values) - min(values)


# --- The square face, which is the one shape geometry adds ---


def test_the_printed_side_comes_back_from_the_declared_area() -> None:
    """The declaration carries an area; the printed side is its root."""
    assert square_side_cm(PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2) == pytest.approx(
        PRINTED_CHRISTIANSEN_CROSS_SECTION_SIDE_CM, rel=0.0, abs=0.0
    )


def test_the_side_is_the_root_of_any_area_not_only_the_printed_one() -> None:
    """The relation is general; only the squareness is a printed fact."""
    assert square_side_cm(4.0) == 2.0
    assert square_side_cm(2.0) == pytest.approx(math.sqrt(2.0))


# --- Plane scheme anchors, recovered from the built bodies ---


def test_the_built_cross_section_is_the_printed_one_on_both_axes() -> None:
    """Both prisms are one printed centimetre square, in x and in y."""
    model = plane_model()
    for name in BODY_NAMES_BY_SCHEME[SCHEME_PLANE]:
        for axis in (0, 1):
            assert extent(model, name, axis) == pytest.approx(
                ANCHOR_CROSS_SECTION_SIDE_M, rel=1.0e-15
            )


def test_the_built_target_thickness_is_the_printed_one() -> None:
    """The fuel body is the printed one centimetre deep."""
    assert extent(plane_model(), BODY_FUEL_SLAB, 2) == pytest.approx(
        ANCHOR_SLAB_THICKNESS_M, rel=1.0e-15
    )


def test_the_built_plate_thickness_floors_to_the_printed_value() -> None:
    """The plate the relations give, floored, is the printed thickness.

    The volume truncates rather than rounds, measured on two independent
    values; rounding this one would give 2.8e-3 and disagree.
    """
    built_cm = extent(plane_model(), BODY_DRIVER_PLATE, 2) / CENTIMETRE_M
    assert two_significant_figure_floor(
        built_cm, PLATE_THICKNESS_EXPONENT
    ) == pytest.approx(PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM, rel=1.0e-12)


def test_the_built_plate_at_the_printed_density_masses_the_declared_plate() -> None:
    """Volume times the printed uranium density returns the plate's mass.

    This is the anchor that ties the body to the configuration: the
    thickness was obtained from the mass, and the mass comes back out of
    the body that thickness produced.
    """
    mesh = next(each for each in plane_model().meshes if each.name == BODY_DRIVER_PLATE)
    volume_cm3 = mesh.signed_volume_m3() * CUBIC_CENTIMETRES_PER_CUBIC_METRE
    mass_mg = (
        volume_cm3 * PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3 * MILLIGRAMS_PER_GRAM
    )
    assert mass_mg == pytest.approx(DERIVED_CHRISTIANSEN_PLATE_MASS_MG, rel=1.0e-12)


def test_the_built_target_carries_the_fuel_mass_the_level0_record_reports() -> None:
    """Volume times the initial fuel density returns the record's mass."""
    configuration, fuel = anchor_configuration(), anchor_fuel()
    projectile, scheme = anchor_projectile(), anchor_scheme()
    record = level0_physics(configuration, fuel, projectile, scheme)
    mesh = next(
        each
        for each in build_plane_model(configuration, projectile, scheme).meshes
        if each.name == BODY_FUEL_SLAB
    )
    volume_cm3 = mesh.signed_volume_m3() * CUBIC_CENTIMETRES_PER_CUBIC_METRE
    mass_mg = (
        volume_cm3
        * record.operating_point.initial_fuel_density_g_cm3
        * MILLIGRAMS_PER_GRAM
    )
    assert mass_mg == pytest.approx(
        record.operating_point.slab_fuel_mass_mg, rel=1.0e-12
    )


def test_the_plate_lies_behind_the_impact_face_and_the_target_ahead() -> None:
    """The origin is the impact face and the two bodies meet there."""
    model = plane_model()
    plate = next(each for each in model.meshes if each.name == BODY_DRIVER_PLATE)
    target = next(each for each in model.meshes if each.name == BODY_FUEL_SLAB)
    assert max(vertex[2] for vertex in plate.vertices) == 0.0
    assert min(vertex[2] for vertex in plate.vertices) < 0.0
    assert min(vertex[2] for vertex in target.vertices) == 0.0
    assert max(vertex[2] for vertex in target.vertices) > 0.0


def test_the_extents_agree_with_the_bodies_they_produced() -> None:
    """The published extents are the ones the bodies were built from."""
    configuration, projectile = anchor_configuration(), anchor_projectile()
    scheme = anchor_scheme()
    side, plate, slab = plane_extents_m(configuration, projectile, scheme)
    model = build_plane_model(configuration, projectile, scheme)
    assert side == pytest.approx(extent(model, BODY_DRIVER_PLATE, 0), rel=1.0e-15)
    assert plate == pytest.approx(extent(model, BODY_DRIVER_PLATE, 2), rel=1.0e-15)
    assert slab == pytest.approx(extent(model, BODY_FUEL_SLAB, 2), rel=1.0e-15)


# --- Convergent scheme anchors ---


def test_the_built_target_radius_is_the_printed_one() -> None:
    """The convergent body reaches the printed one-millimetre radius."""
    mesh = convergent_model().meshes[0]
    reach = max(math.hypot(math.hypot(x, y), z) for x, y, z in mesh.vertices)
    assert reach == pytest.approx(ANCHOR_SPHERE_RADIUS_M, rel=1.0e-15)
    assert convergent_radius_m(anchor_configuration()) == pytest.approx(
        PRINTED_MARSHALL_SPHERE_RADIUS_UM * 1.0e-6, rel=1.0e-15
    )


def test_the_tessellated_target_is_not_an_ideal_sphere() -> None:
    """The inscribed body undershoots ``4/3 pi r^3``, and by how much.

    The non-claim says the bodies are inscribed polyhedra rather than
    ideal spheres. A test that only asserted the radius would leave that
    claim unexercised, so this one measures the gap.
    """
    volume = convergent_model().meshes[0].signed_volume_m3()
    ideal = 4.0 / 3.0 * math.pi * ANCHOR_SPHERE_RADIUS_M**3
    assert volume < ideal
    assert (ideal - volume) / ideal == pytest.approx(
        MEASURED_IDEAL_SPHERE_SHORTFALL, rel=1.0e-9
    )


def test_the_convergent_scheme_draws_one_body_and_no_projectile() -> None:
    """Nothing prints a projectile for this target, so none is drawn."""
    model = convergent_model()
    assert tuple(mesh.name for mesh in model.meshes) == (BODY_FUEL_SPHERE,)
    assert all(mesh.role == ROLE_FUEL for mesh in model.meshes)


# --- What each scheme carries, and what it refuses to carry ---


def test_the_plane_scheme_carries_no_resolution() -> None:
    """A prism has nothing to refine, so the model stores no count."""
    model = plane_model()
    assert model.segments is None
    assert model.rings is None
    assert SCHEME_PLANE not in REFINABLE_SCHEMES


def test_the_plane_builder_takes_no_resolution_either() -> None:
    """The absence is on the signature, not only in the record."""
    import inspect

    parameters = inspect.signature(build_plane_model).parameters
    assert "segments" not in parameters
    assert "rings" not in parameters


def test_the_convergent_scheme_carries_its_measured_counts() -> None:
    """A body of revolution has a resolution and the model states it."""
    model = convergent_model()
    assert model.segments == ANCHOR_SEGMENTS
    assert model.rings == ANCHOR_RINGS
    assert SCHEME_CONVERGENT in REFINABLE_SCHEMES


def test_the_plane_scheme_identifies_the_declarations_it_consumes() -> None:
    """Its plate and target dimensions come from two declarations."""
    model = plane_model()
    assert model.projectile_digest_sha256 is not None
    assert model.scheme_digest_sha256 is not None
    assert SCHEME_PLANE in SCHEMES_CONSUMING_DECLARATIONS


def test_the_convergent_scheme_identifies_none_because_it_consumes_none() -> None:
    """Its only dimension is the configuration's own target radius."""
    model = convergent_model()
    assert model.projectile_digest_sha256 is None
    assert model.scheme_digest_sha256 is None
    assert SCHEME_CONVERGENT not in SCHEMES_CONSUMING_DECLARATIONS


def test_a_changed_declaration_changes_the_plane_model_digest() -> None:
    """The declaration digests are load-bearing, not decorative."""
    configuration, projectile = anchor_configuration(), anchor_projectile()
    scheme = anchor_scheme()
    thicker = scheme.__class__(
        slab_thickness_cm=scheme.slab_thickness_cm * 2.0,
        radial_compression_factor=scheme.radial_compression_factor,
    )
    first = build_plane_model(configuration, projectile, scheme)
    second = build_plane_model(configuration, projectile, thicker)
    assert first.scheme_digest_sha256 != second.scheme_digest_sha256
    assert first.digest_sha256() != second.digest_sha256()


# --- The record ---


def test_the_record_is_schema_tagged_and_carries_its_non_claims() -> None:
    """Every model states what it is and what it is not."""
    for model in (plane_model(), convergent_model()):
        record = model.to_record()
        assert record["schema"] == MODEL_SCHEMA
        assert record["schema_version"] == MODEL_SCHEMA_VERSION
        assert record["non_claims"] == list(MODEL_NON_CLAIMS)
        assert record["units"] == MODEL_UNITS_BY_SCHEME[model.scheme]
        assert record["scheme"] == model.scheme
        assert len(record["bodies"]) == len(BODY_NAMES_BY_SCHEME[model.scheme])


def test_the_non_claims_say_no_source_pairs_the_two_schemes() -> None:
    """The boundary the level-0 record states is stated here too."""
    assert any("no filed source pairs them" in claim for claim in MODEL_NON_CLAIMS)


def test_the_non_claims_say_no_projectile_and_no_cone_is_drawn() -> None:
    """Both absences are decisions and both are written down."""
    assert any(
        "no projectile is drawn for the convergent scheme" in claim
        for claim in MODEL_NON_CLAIMS
    )
    assert any("no cone is drawn" in claim for claim in MODEL_NON_CLAIMS)


def test_the_canonical_bytes_are_sorted_and_newline_terminated() -> None:
    """The record serialises the way every record here serialises."""
    data = plane_model().canonical_bytes()
    assert data.endswith(b"\n")
    text = data.decode("utf-8")
    assert json.loads(text)["schema"] == MODEL_SCHEMA
    assert text.rstrip("\n") == json.dumps(
        json.loads(text), sort_keys=True, separators=(",", ":")
    )


def test_the_digest_identifies_the_record_and_the_two_schemes_differ() -> None:
    """Two schemes of one configuration are two different records."""
    first, second = plane_model(), convergent_model()
    assert first.digest_sha256() != second.digest_sha256()
    assert first.digest_sha256() == plane_model().digest_sha256()


def test_the_bodies_carry_their_roles_and_materials() -> None:
    """Body identity is fixed, not incidental to build order."""
    plane = {mesh.name: mesh for mesh in plane_model().meshes}
    assert plane[BODY_DRIVER_PLATE].role == ROLE_DRIVER
    assert plane[BODY_DRIVER_PLATE].material_identifier == MATERIAL_URANIUM_PLATE
    assert plane[BODY_FUEL_SLAB].role == ROLE_FUEL
    assert plane[BODY_FUEL_SLAB].material_identifier == MATERIAL_FUEL_GAS
    sphere = convergent_model().meshes[0]
    assert sphere.material_identifier == MATERIAL_SOLID_FUEL


# --- Refusals ---


def test_an_unknown_identifier_is_refused() -> None:
    """A model of a configuration this repository does not own."""
    model = plane_model()
    with pytest.raises(DeviceGeometryError, match=r"identifier: must be one of"):
        DeviceModel3D(
            identifier="not_owned",
            scheme=SCHEME_PLANE,
            configuration_digest_sha256=model.configuration_digest_sha256,
            projectile_digest_sha256=model.projectile_digest_sha256,
            scheme_digest_sha256=model.scheme_digest_sha256,
            segments=None,
            rings=None,
            meshes=model.meshes,
        )


def test_a_scheme_the_identifier_does_not_draw_is_refused() -> None:
    """The identifier owns its scheme list and the model honours it."""
    model = plane_model()
    with pytest.raises(DeviceGeometryError, match=r"scheme: .* draws"):
        DeviceModel3D(
            identifier=model.identifier,
            scheme="conical",
            configuration_digest_sha256=model.configuration_digest_sha256,
            projectile_digest_sha256=model.projectile_digest_sha256,
            scheme_digest_sha256=model.scheme_digest_sha256,
            segments=None,
            rings=None,
            meshes=model.meshes,
        )


def test_bodies_out_of_order_are_refused() -> None:
    """The plate is first and the target second, always."""
    model = plane_model()
    with pytest.raises(DeviceGeometryError, match=r"meshes: bodies of the"):
        DeviceModel3D(
            identifier=model.identifier,
            scheme=SCHEME_PLANE,
            configuration_digest_sha256=model.configuration_digest_sha256,
            projectile_digest_sha256=model.projectile_digest_sha256,
            scheme_digest_sha256=model.scheme_digest_sha256,
            segments=None,
            rings=None,
            meshes=tuple(reversed(model.meshes)),
        )


def test_a_resolution_on_the_plane_scheme_is_refused() -> None:
    """A count on a body with nothing to refine is a false statement."""
    model = plane_model()
    with pytest.raises(DeviceGeometryError, match=r"nothing to refine"):
        DeviceModel3D(
            identifier=model.identifier,
            scheme=SCHEME_PLANE,
            configuration_digest_sha256=model.configuration_digest_sha256,
            projectile_digest_sha256=model.projectile_digest_sha256,
            scheme_digest_sha256=model.scheme_digest_sha256,
            segments=ANCHOR_SEGMENTS,
            rings=ANCHOR_RINGS,
            meshes=model.meshes,
        )


def test_a_missing_resolution_on_the_convergent_scheme_is_refused() -> None:
    """A body of revolution without its counts is not identified."""
    model = convergent_model()
    with pytest.raises(DeviceGeometryError, match=r"must carry both counts"):
        DeviceModel3D(
            identifier=model.identifier,
            scheme=SCHEME_CONVERGENT,
            configuration_digest_sha256=model.configuration_digest_sha256,
            projectile_digest_sha256=None,
            scheme_digest_sha256=None,
            segments=ANCHOR_SEGMENTS,
            rings=None,
            meshes=model.meshes,
        )


def test_a_declaration_digest_on_the_convergent_scheme_is_refused() -> None:
    """Identifying a declaration it does not consume is a false claim."""
    model = convergent_model()
    with pytest.raises(DeviceGeometryError, match=r"consumes neither declaration"):
        DeviceModel3D(
            identifier=model.identifier,
            scheme=SCHEME_CONVERGENT,
            configuration_digest_sha256=model.configuration_digest_sha256,
            projectile_digest_sha256=model.configuration_digest_sha256,
            scheme_digest_sha256=None,
            segments=ANCHOR_SEGMENTS,
            rings=ANCHOR_RINGS,
            meshes=model.meshes,
        )


def test_a_missing_declaration_digest_on_the_plane_scheme_is_refused() -> None:
    """Its dimensions come from declarations and must be identified."""
    model = plane_model()
    with pytest.raises(DeviceGeometryError, match=r"must identify them"):
        DeviceModel3D(
            identifier=model.identifier,
            scheme=SCHEME_PLANE,
            configuration_digest_sha256=model.configuration_digest_sha256,
            projectile_digest_sha256=None,
            scheme_digest_sha256=model.scheme_digest_sha256,
            segments=None,
            rings=None,
            meshes=model.meshes,
        )


@pytest.mark.parametrize(
    ("segments", "rings"),
    [(0, ANCHOR_RINGS), (12, ANCHOR_RINGS), (ANCHOR_SEGMENTS, 1)],
)
def test_an_invalid_count_is_refused_under_the_device_error(
    segments: int, rings: int
) -> None:
    """The library's refusals arrive as this package's own error type."""
    with pytest.raises(DeviceGeometryError):
        build_convergent_model(anchor_configuration(), segments, rings)


def test_a_non_positive_extent_is_refused_under_the_device_error() -> None:
    """A declaration the physics would refuse cannot reach a body."""
    projectile = anchor_projectile()
    with pytest.raises(DeviceConfigurationError):
        build_plane_model(
            anchor_configuration(),
            projectile.__class__(
                material_density_g_cm3=projectile.material_density_g_cm3,
                impact_area_cm2=0.0,
            ),
            anchor_scheme(),
        )


def test_a_plate_that_underflows_to_no_thickness_is_refused() -> None:
    """Every declared value is valid and the body is still impossible.

    The level-0 relations validate their inputs and not their results,
    so a mass small enough and a density large enough pass every
    declaration and then divide to exactly zero. The library refuses the
    degenerate prism, and this layer is where that refusal is caught.
    """
    configuration = anchor_configuration()
    underflowing = DeviceConfiguration(
        identifier=configuration.identifier,
        projectile=Projectile(
            mass_mg=UNDERFLOWING_PLATE_MASS_MG,
            velocity_km_s=configuration.projectile.velocity_km_s,
        ),
        target=configuration.target,
        registry=configuration.registry,
    )
    projectile = anchor_projectile()
    with pytest.raises(DeviceGeometryError, match=r"z_high: must exceed z_low"):
        build_plane_model(
            underflowing,
            projectile.__class__(
                material_density_g_cm3=UNDERFLOWING_PLATE_DENSITY_G_CM3,
                impact_area_cm2=projectile.impact_area_cm2,
            ),
            anchor_scheme(),
        )


def test_every_owned_identifier_draws_both_schemes() -> None:
    """The map is a statement about the sources, so it is asserted."""
    assert SCHEMES_BY_IDENTIFIER == {
        "projectile_or_impact_icf": (SCHEME_PLANE, SCHEME_CONVERGENT)
    }
    assert set(BODY_NAMES_BY_SCHEME) == {SCHEME_PLANE, SCHEME_CONVERGENT}
