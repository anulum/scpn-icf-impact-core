# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tier-G2 device model

"""Tier-G2 B-rep models of the two published impact-fusion schemes.

The same bodies as tier G1, built as exact solids through the shared
library's ``cad`` group, checked fail-closed by its evidence kernel
against their analytic closed forms and against their tier-G1 twins, and
exported as normalised STEP bytes with a digest. Two schemes, two
assemblies, two exports — for the reason tier G1 gives.

**This is the first family in the group whose two schemes are checked in
two different faceting regimes, and the difference is the whole content
of this module.** Everything below was measured on this family's own
bodies against the pinned library commit.

The plane scheme
----------------

**There is nothing to choose and nothing to sweep.** Both bodies are
rectangular prisms, and the back-end returns 8 vertices and 12 triangles
for each of them at every linear deflection it accepts — 1e-7 to 1.0,
measured, seven orders — and at every angular deflection from 0.01 to
1.0 radians. No deflection changes any measure. So the deflections here
are inputs the mesher requires, not the strength of a claim, and the
model carries no segment count and no ring count at all rather than a
number nothing consumes.

**The bound is a round-off tolerance and the comparison is two-sided,
and this family is where that matters.** The plate's faceted volume
deviates from its analytic form by ``+2.99e-16`` and the target's by
``-2.12e-16``: **opposite signs, in one assembly, on the first
consumer to build two prisms.** The library's earlier one-sided check
would have admitted the target's deviation at any magnitude whatever.
Both are far inside the declared ``1e-12``.

The back-end has a floor unrelated to either body: at this family's
scale it refuses a linear deflection of 1e-8 outright, with a numeric
error from the mesher rather than a refusal from any bound. The declared
value sits two orders above it.

The convergent scheme
---------------------

**The ring count was scanned, not sampled.** Every count from 4 to 33 is
exact on this family's 1 mm target; 34 refuses, reporting a volume
relative error of 9.8e-5 against a 1e-9 tolerance; 34 to 54 alternate,
with every even count refusing and every odd count exact; from 55 upward
every count refuses. The default is the top of the first regime and a
test asserts the refusal at the step immediately above it. The sibling
families measured 39 and 41 at their own larger radii; neither transfers
and neither was assumed.

**The angular deflection binds here, and it did not for the sibling.**
Measured at 33 rings: the faceted volume deficit is ``2.244500159e-04``
at every angular deflection from 0.2 to 1.0 radians — identical to every
digit — and then falls, to 2.2427e-4 at 0.1, 2.0433e-4 at 0.05 and
1.3329e-5 at 0.01. The declared value therefore sits **inside the
plateau**, where the deficit is at its maximum over the whole range and
does not depend on the exact value chosen. That is the conservative
side: a finer angular deflection can only shrink the deficit, and a
bound established on the plateau holds for all of them.

**The linear deflection is a threshold, not a rung on a ladder.** It
does not change the model — the deficit is identical at 5e-7, 3e-7,
2e-7, 1.5e-7, 1.2e-7 and 1.13e-7 — it changes only the bound, which is
``2 d / r``. So the smallest deflection this body clears is
``deficit * r / 2`` = **1.1222500795e-7 m** exactly, and it was computed
rather than searched for: 1.1223e-7 m passes at a ratio of 1.0000 and
1.1222e-7 m refuses. The declared 2e-7 m puts the body at 0.5611 of its
bound, which is a stated margin against back-end drift rather than the
strongest claim available, and a test asserts that a deflection below
the threshold is refused.

Design record: ADR 0006.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.cad import (
    MANIFEST_SCHEMA,
    BodyEvidence,
    BrepAssembly,
    BrepBody,
    assembly_evidence,
    backend_versions,
    facet_assembly,
    rectangular_prism_brep,
    sphere_brep,
    step_bytes,
    step_sha256,
)
from scpn_reactor_kernels.errors import CadError, GeometryError
from scpn_reactor_kernels.geometry import TriangleMesh

from scpn_icf_impact_core.configuration import DeviceConfiguration
from scpn_icf_impact_core.errors import DeviceGeometryError
from scpn_icf_impact_core.geometry.model import (
    BODY_DRIVER_PLATE,
    BODY_FUEL_SLAB,
    BODY_FUEL_SPHERE,
    BODY_NAMES_BY_SCHEME,
    MATERIAL_FUEL_GAS,
    MATERIAL_SOLID_FUEL,
    MATERIAL_URANIUM_PLATE,
    REFINABLE_SCHEMES,
    ROLE_DRIVER,
    ROLE_FUEL,
    SCHEME_CONVERGENT,
    SCHEME_PLANE,
    SCHEMES_BY_IDENTIFIER,
    SCHEMES_CONSUMING_DECLARATIONS,
    build_convergent_model,
    build_plane_model,
    convergent_radius_m,
    plane_extents_m,
)
from scpn_icf_impact_core.physics.level0 import (
    ProjectileDeclaration,
    SchemeDeclaration,
)

CAD_MODEL_SCHEMA: Final = "scpn.impact-icf-cad-model.v1"
CAD_MODEL_SCHEMA_VERSION: Final = "1.0.0"

#: Segment count handed to the library's evidence kernel for a body with
#: no curved surface. **The library ignores it**, and says so in the
#: kernel's own documentation; it is here only because the signature is
#: shared with curved bodies. It is deliberately not a parameter of this
#: module's plane builder: a knob that changes nothing is worse than no
#: knob, because a reader assumes it does something.
_PLANAR_EVIDENCE_SEGMENTS: Final = 8

#: Mesher deflections of the plane scheme. Both are inputs the back-end
#: requires and neither selects a bound: the prisms are faceted exactly
#: at every value the back-end accepts. The linear value sits two orders
#: above the measured floor at which the mesher itself refuses.
DEFAULT_PLANE_LINEAR_DEFLECTION_M: Final = 1.0e-6
DEFAULT_PLANE_ANGULAR_DEFLECTION_RAD: Final = 0.3

#: Circumferential segments of the convergent scheme's reference mesh.
DEFAULT_CONVERGENT_SEGMENTS: Final = 8
#: Polar steps of the convergent scheme's profile: the top of the regime
#: where every count is exact on this family's own 1 mm body, scanned
#: count by count. The first refusal is at 34.
DEFAULT_CONVERGENT_RINGS: Final = 33
#: Mesher deflections of the convergent scheme, both measured here. The
#: linear value carries a stated margin over the exact threshold of
#: 1.1222500795e-7 m; the angular value sits inside the plateau where
#: the deficit does not depend on it.
DEFAULT_CONVERGENT_LINEAR_DEFLECTION_M: Final = 2.0e-7
DEFAULT_CONVERGENT_ANGULAR_DEFLECTION_RAD: Final = 0.3

CAD_MODEL_UNITS_BY_SCHEME: Final = {
    SCHEME_PLANE: {
        "length": "metre",
        "handedness": "right",
        "axis": (
            "z along the plate's direction of travel; the impact face is the "
            "origin, the plate lies behind it and the target ahead of it"
        ),
        "origin": "the impact face",
    },
    SCHEME_CONVERGENT: {
        "length": "metre",
        "handedness": "right",
        "axis": (
            "z is the polar axis of the revolution and carries no physical "
            "meaning: the target is a sphere and no source prints a drive "
            "direction for it"
        ),
        "origin": "the centre of the target",
    },
}
"""The frame each scheme is built in, matching its tier-G1 twin."""

CAD_MODEL_NON_CLAIMS: Final = (
    (
        "exact solids of a declared configuration and, for the plane scheme, "
        "declared plate and target dimensions"
    ),
    (
        "the plane and the convergent scheme come from two different papers "
        "of one proceedings and no filed source pairs them; they are two "
        "assemblies here for that reason and are never one machine"
    ),
    (
        "the plane scheme's bodies have no curved surface and are faceted "
        "exactly; their deflections are mesher inputs and bound nothing, and "
        "no resolution over them would measure anything"
    ),
    (
        "the convergent scheme's body is a polyhedron of revolution, never "
        "an ideal sphere; the frustum stack of the profile built is its own "
        "analytic reference"
    ),
    (
        "no projectile is drawn for the convergent scheme and no cone is "
        "drawn at all: no filed source dimensions either"
    ),
    (
        "no rigid wall, tamper, holder, standoff or vacuum enclosure is "
        "drawn; the worked case names a rigid wall and dimensions none of "
        "these"
    ),
    (
        "determinism of the STEP bytes is claimed within one pinned "
        "back-end environment only, never across back-end versions"
    ),
    "no body is an engineering model and no fabrication tolerance is carried",
    "no value describes or validates any real machine or shot",
)


@dataclass(frozen=True, slots=True)
class DeviceModelCAD:
    """The B-rep model of one configuration under one scheme.

    Parameters
    ----------
    identifier
        Configuration identifier the scheme belongs to.
    scheme
        Which of the two published schemes this model draws.
    configuration_digest_sha256
        Digest of the configuration the model was built from.
    projectile_digest_sha256, scheme_digest_sha256
        Digests of the declarations the scheme consumes, or ``None``
        where it consumes none.
    reference_mesh_segments, rings
        Tier-G1 reference the bodies were checked against and the polar
        step count both tiers share, or ``None`` for a scheme whose
        bodies have no curvature to refine.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison.
    backend_versions
        Versions of the pinned back-ends that produced the solids.
    assembly_manifest
        The library's assembly manifest of the bodies.
    step_sha256
        Digest of the normalised STEP bytes.
    bodies
        Checked evidence of each body, in the fixed order.
    step_data
        The normalised STEP bytes themselves.
    faceted_meshes
        The faceted meshes the evidence was computed from.

    Raises
    ------
    DeviceGeometryError
        If the identifier or the scheme is unknown, if the identifier
        does not draw the scheme, if the manifest schema, the body count
        or the body order is wrong, or if the resolutions or the
        declaration digests do not match what the scheme consumes.
    """

    identifier: str
    scheme: str
    configuration_digest_sha256: str
    projectile_digest_sha256: str | None
    scheme_digest_sha256: str | None
    reference_mesh_segments: int | None
    rings: int | None
    linear_deflection_m: float
    angular_deflection_rad: float
    backend_versions: dict[str, str]
    assembly_manifest: dict[str, Any]
    step_sha256: str
    bodies: tuple[BodyEvidence, ...]
    step_data: bytes
    faceted_meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the scheme, its manifest, its bodies and what it carries.

        Raises
        ------
        DeviceGeometryError
            If the identifier or the scheme is unknown, if the
            identifier does not draw the scheme, if the manifest schema,
            the body count or the body order is wrong, or if the
            resolutions or the declaration digests do not match what the
            scheme consumes.
        """
        drawn = SCHEMES_BY_IDENTIFIER.get(self.identifier)
        if drawn is None:
            raise DeviceGeometryError(
                f"identifier: must be one of "
                f"{tuple(SCHEMES_BY_IDENTIFIER)!r}, got {self.identifier!r}"
            )
        if self.scheme not in drawn:
            raise DeviceGeometryError(
                f"scheme: {self.identifier!r} draws {drawn!r}, got {self.scheme!r}"
            )
        expected = BODY_NAMES_BY_SCHEME[self.scheme]
        if self.assembly_manifest.get("schema") != MANIFEST_SCHEMA:
            raise DeviceGeometryError(
                f"assembly_manifest.schema: must be {MANIFEST_SCHEMA!r}"
            )
        if self.assembly_manifest.get("body_count") != len(expected):
            raise DeviceGeometryError(
                f"assembly_manifest.body_count: must be {len(expected)}, got "
                f"{self.assembly_manifest.get('body_count')!r}"
            )
        names = tuple(body.name for body in self.bodies)
        if names != expected:
            raise DeviceGeometryError(
                f"bodies: of the {self.scheme!r} scheme must be exactly "
                f"{expected!r} in order, got {names!r}"
            )
        self._require_resolution_matches_scheme()
        self._require_declarations_match_scheme()

    def _require_resolution_matches_scheme(self) -> None:
        """Refuse a resolution the scheme has no use for, or a missing one.

        Raises
        ------
        DeviceGeometryError
            If a refinable scheme carries no counts, or a scheme whose
            bodies have no curvature carries any.
        """
        refinable = self.scheme in REFINABLE_SCHEMES
        carried = (self.reference_mesh_segments, self.rings)
        if refinable and None in carried:
            raise DeviceGeometryError(
                f"reference_mesh_segments, rings: the {self.scheme!r} scheme "
                f"has curved bodies and must carry both counts, got "
                f"{carried!r}"
            )
        if not refinable and carried != (None, None):
            raise DeviceGeometryError(
                f"reference_mesh_segments, rings: the {self.scheme!r} scheme "
                f"has no curved surface and nothing to refine, so both must "
                f"be None, got {carried!r}"
            )

    def _require_declarations_match_scheme(self) -> None:
        """Refuse a declaration digest the scheme does not consume.

        Raises
        ------
        DeviceGeometryError
            If a scheme that consumes declarations carries no digests,
            or a scheme that consumes none carries any.
        """
        consuming = self.scheme in SCHEMES_CONSUMING_DECLARATIONS
        carried = (self.projectile_digest_sha256, self.scheme_digest_sha256)
        if consuming and None in carried:
            raise DeviceGeometryError(
                f"projectile_digest_sha256, scheme_digest_sha256: the "
                f"{self.scheme!r} scheme consumes both declarations and must "
                f"identify them, got {carried!r}"
            )
        if not consuming and carried != (None, None):
            raise DeviceGeometryError(
                f"projectile_digest_sha256, scheme_digest_sha256: the "
                f"{self.scheme!r} scheme consumes neither declaration and "
                f"must not identify one, got {carried!r}"
            )

    def to_record(self) -> dict[str, Any]:
        """Project the model to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with one entry per body.
        """
        return {
            "schema": CAD_MODEL_SCHEMA,
            "schema_version": CAD_MODEL_SCHEMA_VERSION,
            "units": dict(CAD_MODEL_UNITS_BY_SCHEME[self.scheme]),
            "non_claims": list(CAD_MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "scheme": self.scheme,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "projectile_digest_sha256": self.projectile_digest_sha256,
            "scheme_digest_sha256": self.scheme_digest_sha256,
            "reference_mesh_segments": self.reference_mesh_segments,
            "rings": self.rings,
            "linear_deflection_m": self.linear_deflection_m,
            "angular_deflection_rad": self.angular_deflection_rad,
            "backend_versions": dict(self.backend_versions),
            "assembly_manifest": self.assembly_manifest,
            "step_sha256": self.step_sha256,
            "bodies": [body.to_record() for body in self.bodies],
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the model record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact model record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def _compose(
    reference_meshes: tuple[TriangleMesh, ...],
    solids: tuple[BrepBody, ...],
    smallest_radii: tuple[float | None, ...],
    segments: int,
    linear_deflection_m: float,
    angular_deflection_rad: float,
) -> tuple[BrepAssembly, tuple[TriangleMesh, ...], tuple[BodyEvidence, ...]]:
    """Facet an assembly and check it against its tier-G1 reference.

    Parameters
    ----------
    reference_meshes
        The tier-G1 meshes of the same bodies, in the same order.
    solids
        The B-rep bodies.
    smallest_radii
        Each body's smallest circular radius, or ``None`` where the body
        has no curved surface. The tuple is what makes the two schemes'
        faceting regimes explicit at the call site.
    segments
        Reference segment count; ignored by the library for a body
        without curvature.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections.

    Returns
    -------
    (assembly, faceted, evidence)
        The assembly, its faceted meshes and its checked evidence.

    Raises
    ------
    DeviceGeometryError
        If a body violates a declared evidence bound; the library's
        refusals are re-raised under the device error type with their
        messages.
    """
    try:
        assembly = BrepAssembly(solids)
        faceted = facet_assembly(assembly, linear_deflection_m, angular_deflection_rad)
        evidence = assembly_evidence(
            assembly.bodies,
            smallest_radii,
            faceted,
            reference_meshes,
            linear_deflection_m,
            segments,
        )
    except (CadError, GeometryError) as exc:
        raise DeviceGeometryError(str(exc)) from exc
    return assembly, faceted, evidence


def _step_extras(
    scheme: str,
    configuration: DeviceConfiguration,
    assembly: BrepAssembly,
    projectile_digest_sha256: str | None,
    scheme_digest_sha256: str | None,
) -> dict[str, Any]:
    """Build the metadata block embedded in the STEP export.

    Parameters
    ----------
    scheme
        Which of the two published schemes the assembly draws.
    configuration
        Validated impact-ICF configuration.
    assembly
        The assembly being exported.
    projectile_digest_sha256, scheme_digest_sha256
        Digests of the declarations the scheme consumes, or ``None``.

    Returns
    -------
    dict[str, Any]
        The metadata block, carrying the non-claims into the export so
        that a STEP file read on its own still states them.
    """
    return {
        "schema": CAD_MODEL_SCHEMA,
        "schema_version": CAD_MODEL_SCHEMA_VERSION,
        "identifier": configuration.identifier,
        "scheme": scheme,
        "configuration_digest_sha256": configuration.digest_sha256(),
        "projectile_digest_sha256": projectile_digest_sha256,
        "scheme_digest_sha256": scheme_digest_sha256,
        "assembly_manifest_sha256": assembly.manifest_sha256(),
        "units": dict(CAD_MODEL_UNITS_BY_SCHEME[scheme]),
        "non_claims": list(CAD_MODEL_NON_CLAIMS),
        "backend_versions": backend_versions(),
    }


def build_plane_cad(
    configuration: DeviceConfiguration,
    projectile: ProjectileDeclaration,
    scheme: SchemeDeclaration,
    linear_deflection_m: float = DEFAULT_PLANE_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_PLANE_ANGULAR_DEFLECTION_RAD,
) -> DeviceModelCAD:
    """Build the B-rep model of the plane scheme.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration supplying the plate's mass.
    projectile
        Declared plate material and the face it presents.
    scheme
        Declared dimensions supplying the target's fuel thickness.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections. **Neither bounds anything here**: both
        bodies are prisms and are faceted exactly at every value the
        back-end accepts. They remain parameters because the mesher
        requires them, and the record carries them so that a reader
        knows what was asked of the back-end.

    Returns
    -------
    DeviceModelCAD
        The composed, fail-closed checked model with its STEP export.

    Raises
    ------
    DeviceGeometryError
        If a deflection is invalid or a body violates its declared
        evidence bound; the library's refusals are re-raised under the
        device error type with their messages.
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        optional CAD back-end is absent.
    DeviceConfigurationError
        If a declared value leaves its documented interval.
    """
    reference = build_plane_model(configuration, projectile, scheme)
    side, plate, slab = plane_extents_m(configuration, projectile, scheme)
    solids = (
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
            side,
            side,
            0.0,
            slab,
            BODY_FUEL_SLAB,
            ROLE_FUEL,
            MATERIAL_FUEL_GAS,
        ),
    )
    assembly, faceted, bodies = _compose(
        reference.meshes,
        solids,
        (None, None),
        _PLANAR_EVIDENCE_SEGMENTS,
        linear_deflection_m,
        angular_deflection_rad,
    )
    step_data = step_bytes(
        assembly,
        _step_extras(
            SCHEME_PLANE,
            configuration,
            assembly,
            reference.projectile_digest_sha256,
            reference.scheme_digest_sha256,
        ),
    )
    return DeviceModelCAD(
        identifier=configuration.identifier,
        scheme=SCHEME_PLANE,
        configuration_digest_sha256=configuration.digest_sha256(),
        projectile_digest_sha256=reference.projectile_digest_sha256,
        scheme_digest_sha256=reference.scheme_digest_sha256,
        reference_mesh_segments=None,
        rings=None,
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        backend_versions=backend_versions(),
        assembly_manifest=assembly.manifest(),
        step_sha256=step_sha256(step_data),
        bodies=bodies,
        step_data=step_data,
        faceted_meshes=faceted,
    )


def build_convergent_cad(
    configuration: DeviceConfiguration,
    segments: int = DEFAULT_CONVERGENT_SEGMENTS,
    rings: int = DEFAULT_CONVERGENT_RINGS,
    linear_deflection_m: float = DEFAULT_CONVERGENT_LINEAR_DEFLECTION_M,
    angular_deflection_rad: float = DEFAULT_CONVERGENT_ANGULAR_DEFLECTION_RAD,
) -> DeviceModelCAD:
    """Build the B-rep model of the convergent scheme.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration supplying the target radius.
    segments
        Segment count of the tier-G1 reference mesh of the comparison.
    rings
        Polar steps of the profile, shared by both tiers.
    linear_deflection_m, angular_deflection_rad
        Mesher deflections of the faceting comparison. Unlike the plane
        scheme, both are load-bearing here: the linear one sets the
        bound the measured deficit is checked against, and the angular
        one sets the deficit itself once it falls below the plateau.

    Returns
    -------
    DeviceModelCAD
        The composed, fail-closed checked model with its STEP export.

    Raises
    ------
    DeviceGeometryError
        If a count or a deflection is invalid, or the body violates its
        declared evidence bound; the library's refusals are re-raised
        under the device error type with their messages.
        :class:`~scpn_reactor_kernels.errors.CadUnavailableError` if the
        optional CAD back-end is absent.
    """
    reference = build_convergent_model(configuration, segments, rings)
    radius = convergent_radius_m(configuration)
    solids = (
        sphere_brep(
            radius,
            0.0,
            rings,
            BODY_FUEL_SPHERE,
            ROLE_FUEL,
            MATERIAL_SOLID_FUEL,
        ),
    )
    assembly, faceted, bodies = _compose(
        reference.meshes,
        solids,
        (radius,),
        segments,
        linear_deflection_m,
        angular_deflection_rad,
    )
    step_data = step_bytes(
        assembly,
        _step_extras(SCHEME_CONVERGENT, configuration, assembly, None, None),
    )
    return DeviceModelCAD(
        identifier=configuration.identifier,
        scheme=SCHEME_CONVERGENT,
        configuration_digest_sha256=configuration.digest_sha256(),
        projectile_digest_sha256=None,
        scheme_digest_sha256=None,
        reference_mesh_segments=segments,
        rings=rings,
        linear_deflection_m=linear_deflection_m,
        angular_deflection_rad=angular_deflection_rad,
        backend_versions=backend_versions(),
        assembly_manifest=assembly.manifest(),
        step_sha256=step_sha256(step_data),
        bodies=bodies,
        step_data=step_data,
        faceted_meshes=faceted,
    )
