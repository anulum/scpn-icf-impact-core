# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tier-G2 device model tests

"""Every branch of the tier-G2 models, and the two faceting regimes.

The passing builds are cached: each costs seconds, and rebuilding one
per test buys no evidence a single build does not already carry. The
builds that are supposed to fail are not cached, because the failure is
what they assert.

**Both regimes are exercised against something that trips them.** A
tolerance nothing can violate is not a gate, so the planar tolerance is
shown to refuse a prism wrong by one part in ten thousand and the
curved bound is shown to refuse the deflection one step below its
threshold.
"""

from __future__ import annotations

import dataclasses
import functools
import json
import math

import pytest
from scpn_reactor_kernels.cad import (
    PLANAR_FACETING_TOLERANCE,
    BodyEvidence,
    BrepBody,
    assembly_evidence,
    rectangular_prism_brep,
)
from scpn_reactor_kernels.errors import CadError
from scpn_reactor_kernels.geometry import TriangleMesh, rectangular_prism

from geometry_fixtures import (
    ANCHOR_CROSS_SECTION_SIDE_M,
    ANCHOR_RINGS,
    ANCHOR_SEGMENTS,
    ANCHOR_SPHERE_RADIUS_M,
    BELOW_PLATEAU_ANGULAR_DEFLECTION_RAD,
    FIRST_REFUSED_RINGS,
    LINEAR_DEFLECTION_ABOVE_THRESHOLD_M,
    LINEAR_DEFLECTION_BELOW_THRESHOLD_M,
    MEASURED_CONVERGENT_DEFICIT,
    MEASURED_CONVERGENT_THRESHOLD_M,
    NEXT_EXACT_RINGS,
    PLANAR_ACCEPTED_ANGULAR_DEFLECTIONS_RAD,
    PLANAR_ACCEPTED_LINEAR_DEFLECTIONS_M,
    PLANAR_FACET_COUNTS,
    PLATEAU_ANGULAR_DEFLECTIONS_RAD,
    anchor_configuration,
    anchor_projectile,
    anchor_scheme,
)
from scpn_icf_impact_core.errors import DeviceGeometryError
from scpn_icf_impact_core.geometry import (
    BODY_DRIVER_PLATE,
    BODY_FUEL_SLAB,
    BODY_FUEL_SPHERE,
    BODY_NAMES_BY_SCHEME,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS_BY_SCHEME,
    DEFAULT_CONVERGENT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_CONVERGENT_LINEAR_DEFLECTION_M,
    DEFAULT_CONVERGENT_RINGS,
    DEFAULT_CONVERGENT_SEGMENTS,
    DEFAULT_PLANE_ANGULAR_DEFLECTION_RAD,
    DEFAULT_PLANE_LINEAR_DEFLECTION_M,
    MATERIAL_FUEL_GAS,
    MATERIAL_URANIUM_PLATE,
    ROLE_DRIVER,
    ROLE_FUEL,
    SCHEME_PLANE,
    DeviceModelCAD,
    build_convergent_cad,
    build_plane_cad,
    plane_extents_m,
)

#: Relative error deliberately introduced into a reference prism, to
#: prove the planar tolerance still refuses something. One part in ten
#: thousand is twelve orders above the tolerance and eight orders below
#: anything a reader would notice by eye.
WRONG_BY_ONE_PART_IN_TEN_THOUSAND = 1.0e-4
#: Segment counts the mesh-difference margin was measured across. The
#: absolute margin is the faceted deficit at every one of them.
REFERENCE_SEGMENT_COUNTS = (8, 16, 24, 32)


@functools.cache
def plane_cad() -> DeviceModelCAD:
    """Build and cache the plane scheme's B-rep model.

    Returns
    -------
    DeviceModelCAD
        The checked two-prism model.
    """
    return build_plane_cad(anchor_configuration(), anchor_projectile(), anchor_scheme())


@functools.cache
def convergent_cad() -> DeviceModelCAD:
    """Build and cache the convergent scheme's B-rep model.

    Returns
    -------
    DeviceModelCAD
        The checked one-sphere model.
    """
    return build_convergent_cad(anchor_configuration())


def evidence_of(model: DeviceModelCAD, name: str) -> BodyEvidence:
    """Return the checked evidence of one body.

    Parameters
    ----------
    model
        The built model.
    name
        Body name.

    Returns
    -------
    BodyEvidence
        That body's checked evidence.
    """
    return next(body for body in model.bodies if body.name == name)


# --- The plane scheme: nothing to refine, and a two-sided tolerance ---


def test_both_prisms_are_faceted_exactly_and_the_bound_is_the_tolerance() -> None:
    """A prism has no chord deficit, so its bound is a round-off one."""
    for name in BODY_NAMES_BY_SCHEME[SCHEME_PLANE]:
        body = evidence_of(plane_cad(), name)
        assert body.faceted_volume_deficit_bound == PLANAR_FACETING_TOLERANCE
        assert body.mesh_volume_difference_bound == PLANAR_FACETING_TOLERANCE
        assert abs(body.faceted_volume_relative_deficit) < PLANAR_FACETING_TOLERANCE


def test_the_two_prisms_deviate_in_opposite_directions() -> None:
    """The plate overshoots and the target undershoots, in one assembly.

    This is why the library's comparison is made in magnitude. A
    one-sided check would have admitted the target's deviation at any
    size whatever, and this family is the first consumer whose own
    bodies show both signs.
    """
    plate = evidence_of(plane_cad(), BODY_DRIVER_PLATE)
    target = evidence_of(plane_cad(), BODY_FUEL_SLAB)
    assert plate.faceted_volume_relative_deficit > 0.0
    assert target.faceted_volume_relative_deficit < 0.0


@pytest.mark.parametrize("linear", PLANAR_ACCEPTED_LINEAR_DEFLECTIONS_M)
def test_no_linear_deflection_changes_the_plane_scheme(linear: float) -> None:
    """Seven orders of deflection, and the model is the same model."""
    model = build_plane_cad(
        anchor_configuration(),
        anchor_projectile(),
        anchor_scheme(),
        linear_deflection_m=linear,
    )
    vertices, faces = PLANAR_FACET_COUNTS
    for mesh in model.faceted_meshes:
        assert (mesh.vertex_count, mesh.face_count) == (vertices, faces)
    for name in BODY_NAMES_BY_SCHEME[SCHEME_PLANE]:
        assert evidence_of(model, name).faceted_volume_relative_deficit == (
            evidence_of(plane_cad(), name).faceted_volume_relative_deficit
        )


@pytest.mark.parametrize("angular", PLANAR_ACCEPTED_ANGULAR_DEFLECTIONS_RAD)
def test_no_angular_deflection_changes_the_plane_scheme(angular: float) -> None:
    """Neither deflection is an accuracy knob on a body without curvature."""
    model = build_plane_cad(
        anchor_configuration(),
        anchor_projectile(),
        anchor_scheme(),
        angular_deflection_rad=angular,
    )
    for name in BODY_NAMES_BY_SCHEME[SCHEME_PLANE]:
        assert evidence_of(model, name).faceted_volume_relative_deficit == (
            evidence_of(plane_cad(), name).faceted_volume_relative_deficit
        )


def plane_solids() -> tuple[BrepBody, ...]:
    """Rebuild the plane scheme's two B-rep bodies.

    Returns
    -------
    tuple of BrepBody
        The same two solids the plane model is built from; the builder
        is deterministic, so these are that model's bodies.
    """
    side, plate, slab = plane_extents_m(
        anchor_configuration(), anchor_projectile(), anchor_scheme()
    )
    return (
        rectangular_prism_brep(
            side,
            side,
            -plate,
            0.0,
            BODY_DRIVER_PLATE,
            ROLE_DRIVER,
            MATERIAL_URANIUM_PLATE,
        ),
        rectangular_prism_brep(
            side, side, 0.0, slab, BODY_FUEL_SLAB, ROLE_FUEL, MATERIAL_FUEL_GAS
        ),
    )


def test_the_planar_tolerance_still_refuses_a_prism_that_is_wrong() -> None:
    """A reference prism off by one part in ten thousand is refused.

    Without this the tolerance would be decorative: every measured
    deviation is twelve orders inside it, so nothing in the passing
    builds shows that it can fail at all.
    """
    model = plane_cad()
    wrong_side = ANCHOR_CROSS_SECTION_SIDE_M * (1.0 + WRONG_BY_ONE_PART_IN_TEN_THOUSAND)
    references = []
    for mesh in model.faceted_meshes:
        low = min(vertex[2] for vertex in mesh.vertices)
        high = max(vertex[2] for vertex in mesh.vertices)
        vertices, faces = rectangular_prism(wrong_side, wrong_side, low, high)
        references.append(
            TriangleMesh(
                name=mesh.name,
                role=mesh.role,
                material_identifier=mesh.material_identifier,
                vertices=vertices,
                faces=faces,
            )
        )
    with pytest.raises(CadError, match=r"mesh_volume_relative_difference"):
        assembly_evidence(
            plane_solids(),
            (None, None),
            model.faceted_meshes,
            tuple(references),
            DEFAULT_PLANE_LINEAR_DEFLECTION_M,
            ANCHOR_SEGMENTS,
        )


def test_the_plane_model_carries_no_resolution() -> None:
    """There is no reference segment count and no ring count to carry."""
    model = plane_cad()
    assert model.reference_mesh_segments is None
    assert model.rings is None
    assert model.linear_deflection_m == DEFAULT_PLANE_LINEAR_DEFLECTION_M
    assert model.angular_deflection_rad == DEFAULT_PLANE_ANGULAR_DEFLECTION_RAD


# --- The convergent scheme: a scanned ring regime and an exact threshold ---


def test_the_declared_ring_count_is_the_top_of_the_exact_regime() -> None:
    """Thirty-three builds; the step immediately above it refuses."""
    assert DEFAULT_CONVERGENT_RINGS == ANCHOR_RINGS
    assert convergent_cad().rings == ANCHOR_RINGS
    with pytest.raises(DeviceGeometryError, match=r"volume_relative_error"):
        build_convergent_cad(anchor_configuration(), rings=FIRST_REFUSED_RINGS)


def test_the_refusal_is_not_a_ceiling_because_the_next_count_builds() -> None:
    """Thirty-five builds again, so thirty-four is not a ceiling.

    Above the first refusal the counts alternate by parity; recording
    that stops a reader from treating thirty-four as an upper bound.
    """
    model = build_convergent_cad(anchor_configuration(), rings=NEXT_EXACT_RINGS)
    assert model.rings == NEXT_EXACT_RINGS


@pytest.mark.parametrize("angular", PLATEAU_ANGULAR_DEFLECTIONS_RAD)
def test_the_angular_deflection_does_not_bind_on_the_plateau(
    angular: float,
) -> None:
    """From 0.2 to 1.0 radians the deficit is identical to every digit."""
    model = build_convergent_cad(anchor_configuration(), angular_deflection_rad=angular)
    assert evidence_of(
        model, BODY_FUEL_SPHERE
    ).faceted_volume_relative_deficit == pytest.approx(
        MEASURED_CONVERGENT_DEFICIT, rel=1.0e-9
    )


def test_below_the_plateau_the_angular_deflection_does_bind() -> None:
    """A finer angular deflection shrinks the deficit.

    So the declared value sits on the plateau, where the deficit is at
    its maximum over the whole range.
    """
    model = build_convergent_cad(
        anchor_configuration(),
        angular_deflection_rad=BELOW_PLATEAU_ANGULAR_DEFLECTION_RAD,
    )
    finer = evidence_of(model, BODY_FUEL_SPHERE).faceted_volume_relative_deficit
    assert finer < MEASURED_CONVERGENT_DEFICIT
    assert DEFAULT_CONVERGENT_ANGULAR_DEFLECTION_RAD in PLATEAU_ANGULAR_DEFLECTIONS_RAD


def test_the_linear_deflection_moves_the_bound_and_not_the_model() -> None:
    """It is the strength of the claim, never the accuracy of the body."""
    stronger = build_convergent_cad(
        anchor_configuration(),
        linear_deflection_m=LINEAR_DEFLECTION_ABOVE_THRESHOLD_M,
    )
    default = evidence_of(convergent_cad(), BODY_FUEL_SPHERE)
    tightest = evidence_of(stronger, BODY_FUEL_SPHERE)
    assert (
        tightest.faceted_volume_relative_deficit
        == default.faceted_volume_relative_deficit
    )
    assert tightest.faceted_volume_deficit_bound < default.faceted_volume_deficit_bound


def test_the_threshold_is_computed_and_the_step_below_it_is_refused() -> None:
    """``deficit * r / 2`` exactly, and the deflection below it fails."""
    deficit = evidence_of(
        convergent_cad(), BODY_FUEL_SPHERE
    ).faceted_volume_relative_deficit
    assert deficit * ANCHOR_SPHERE_RADIUS_M / 2.0 == pytest.approx(
        MEASURED_CONVERGENT_THRESHOLD_M, rel=1.0e-9
    )
    assert LINEAR_DEFLECTION_BELOW_THRESHOLD_M < MEASURED_CONVERGENT_THRESHOLD_M
    assert LINEAR_DEFLECTION_ABOVE_THRESHOLD_M > MEASURED_CONVERGENT_THRESHOLD_M
    with pytest.raises(DeviceGeometryError, match=r"faceted_volume_relative_deficit"):
        build_convergent_cad(
            anchor_configuration(),
            linear_deflection_m=LINEAR_DEFLECTION_BELOW_THRESHOLD_M,
        )


def test_the_declared_deflection_keeps_a_stated_margin() -> None:
    """The declared value is not the strongest claim available.

    The ratio it does claim is stated here rather than left to a reader
    to compute.
    """
    body = evidence_of(convergent_cad(), BODY_FUEL_SPHERE)
    ratio = body.faceted_volume_relative_deficit / body.faceted_volume_deficit_bound
    assert ratio == pytest.approx(0.5611, rel=1.0e-3)
    assert DEFAULT_CONVERGENT_LINEAR_DEFLECTION_M > MEASURED_CONVERGENT_THRESHOLD_M


@pytest.mark.parametrize("segments", REFERENCE_SEGMENT_COUNTS)
def test_the_mesh_difference_margin_is_the_faceted_deficit(segments: int) -> None:
    """The two bounds are not independent, measured at four counts.

    The mesh-difference ratio looks alarming at a low segment count —
    0.998 of its bound at eight — and the absolute margin is the same
    number at every count, because it *is* the faceted deficit. A reader
    who only saw the ratio would tighten the wrong knob.
    """
    model = build_convergent_cad(anchor_configuration(), segments=segments)
    body = evidence_of(model, BODY_FUEL_SPHERE)
    margin = body.mesh_volume_difference_bound - body.mesh_volume_relative_difference
    assert margin == pytest.approx(body.faceted_volume_relative_deficit, rel=1.0e-9)


def test_the_convergent_body_is_checked_against_a_curved_bound() -> None:
    """Its bound is the chord deficit, never the planar tolerance."""
    body = evidence_of(convergent_cad(), BODY_FUEL_SPHERE)
    assert body.faceted_volume_deficit_bound == pytest.approx(
        2.0 * DEFAULT_CONVERGENT_LINEAR_DEFLECTION_M / ANCHOR_SPHERE_RADIUS_M
    )
    assert body.faceted_volume_deficit_bound > PLANAR_FACETING_TOLERANCE


# --- The records ---


def test_each_record_is_schema_tagged_and_carries_its_non_claims() -> None:
    """Every model states what it is and what it is not."""
    for model in (plane_cad(), convergent_cad()):
        record = model.to_record()
        assert record["schema"] == CAD_MODEL_SCHEMA
        assert record["schema_version"] == CAD_MODEL_SCHEMA_VERSION
        assert record["non_claims"] == list(CAD_MODEL_NON_CLAIMS)
        assert record["units"] == CAD_MODEL_UNITS_BY_SCHEME[model.scheme]
        assert record["scheme"] == model.scheme
        assert len(record["bodies"]) == len(BODY_NAMES_BY_SCHEME[model.scheme])
        assert record["backend_versions"] == model.backend_versions


def test_the_non_claims_say_the_plane_deflections_bound_nothing() -> None:
    """The reader is told which knobs do nothing before they turn one."""
    assert any(
        "their deflections are mesher inputs and bound nothing" in claim
        for claim in CAD_MODEL_NON_CLAIMS
    )


def test_the_canonical_bytes_are_sorted_and_newline_terminated() -> None:
    """The record serialises the way every record here serialises."""
    data = convergent_cad().canonical_bytes()
    assert data.endswith(b"\n")
    text = data.decode("utf-8")
    assert text.rstrip("\n") == json.dumps(
        json.loads(text), sort_keys=True, separators=(",", ":")
    )


def test_the_two_schemes_are_two_records_and_two_exports() -> None:
    """One configuration, two schemes, and nothing shared between them."""
    first, second = plane_cad(), convergent_cad()
    assert first.digest_sha256() != second.digest_sha256()
    assert first.step_sha256 != second.step_sha256
    assert first.assembly_manifest["body_count"] == 2
    assert second.assembly_manifest["body_count"] == 1


def test_the_step_export_is_deterministic_within_this_environment() -> None:
    """The same inputs give the same bytes; nothing across versions."""
    rebuilt = build_convergent_cad(anchor_configuration())
    assert rebuilt.step_data
    assert rebuilt.step_sha256 == convergent_cad().step_sha256
    assert math.isclose(
        rebuilt.bodies[0].brep_volume_m3,
        convergent_cad().bodies[0].brep_volume_m3,
        rel_tol=0.0,
        abs_tol=0.0,
    )


def test_the_export_carries_the_scheme_and_the_declarations_it_binds() -> None:
    """A STEP file read on its own still says which scheme it is."""
    assert b"convergent" in convergent_cad().step_data
    assert b"plane" in plane_cad().step_data


def test_the_plane_model_binds_its_declarations_and_the_other_does_not() -> None:
    """Provenance follows what each scheme actually consumes."""
    assert plane_cad().projectile_digest_sha256 is not None
    assert plane_cad().scheme_digest_sha256 is not None
    assert convergent_cad().projectile_digest_sha256 is None
    assert convergent_cad().scheme_digest_sha256 is None


# --- Refusals of the record's own invariants ---


def test_an_unknown_identifier_is_refused() -> None:
    """A model of a configuration this repository does not own."""
    with pytest.raises(DeviceGeometryError, match=r"identifier: must be one of"):
        dataclasses.replace(plane_cad(), identifier="not_owned")


def test_a_scheme_the_identifier_does_not_draw_is_refused() -> None:
    """The identifier owns its scheme list and the model honours it."""
    with pytest.raises(DeviceGeometryError, match=r"scheme: .* draws"):
        dataclasses.replace(plane_cad(), scheme="conical")


def test_a_wrong_manifest_schema_is_refused() -> None:
    """The manifest is the library's, and the tag is checked."""
    manifest = dict(plane_cad().assembly_manifest)
    manifest["schema"] = "scpn.something-else.v1"
    with pytest.raises(DeviceGeometryError, match=r"assembly_manifest\.schema"):
        dataclasses.replace(plane_cad(), assembly_manifest=manifest)


def test_a_wrong_manifest_body_count_is_refused() -> None:
    """A manifest that counts a different assembly is not this one."""
    manifest = dict(plane_cad().assembly_manifest)
    manifest["body_count"] = 3
    with pytest.raises(DeviceGeometryError, match=r"assembly_manifest\.body_count"):
        dataclasses.replace(plane_cad(), assembly_manifest=manifest)


def test_bodies_out_of_order_are_refused() -> None:
    """The plate is first and the target second, always."""
    with pytest.raises(DeviceGeometryError, match=r"bodies: of the"):
        dataclasses.replace(plane_cad(), bodies=tuple(reversed(plane_cad().bodies)))


def test_a_resolution_on_the_plane_scheme_is_refused() -> None:
    """A count on a body with nothing to refine is a false statement."""
    with pytest.raises(DeviceGeometryError, match=r"nothing to refine"):
        dataclasses.replace(
            plane_cad(),
            reference_mesh_segments=DEFAULT_CONVERGENT_SEGMENTS,
            rings=DEFAULT_CONVERGENT_RINGS,
        )


def test_a_missing_resolution_on_the_convergent_scheme_is_refused() -> None:
    """A body of revolution without its counts is not identified."""
    with pytest.raises(DeviceGeometryError, match=r"must carry both counts"):
        dataclasses.replace(convergent_cad(), rings=None)


def test_a_declaration_digest_on_the_convergent_scheme_is_refused() -> None:
    """Identifying a declaration it does not consume is a false claim."""
    with pytest.raises(DeviceGeometryError, match=r"consumes neither declaration"):
        dataclasses.replace(
            convergent_cad(),
            projectile_digest_sha256=convergent_cad().configuration_digest_sha256,
        )


def test_a_missing_declaration_digest_on_the_plane_scheme_is_refused() -> None:
    """Its dimensions come from declarations and must be identified."""
    with pytest.raises(DeviceGeometryError, match=r"must identify them"):
        dataclasses.replace(plane_cad(), scheme_digest_sha256=None)


def test_an_invalid_deflection_is_refused_under_the_device_error() -> None:
    """The library's refusals arrive as this package's own error type."""
    with pytest.raises(DeviceGeometryError):
        build_convergent_cad(anchor_configuration(), linear_deflection_m=0.0)


def test_an_invalid_count_is_refused_under_the_device_error() -> None:
    """A segment count the mesh contract does not admit."""
    with pytest.raises(DeviceGeometryError):
        build_convergent_cad(anchor_configuration(), segments=12)
