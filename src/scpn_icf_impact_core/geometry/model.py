# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tier-G1 device model

"""Tier-G1 tessellated models of the two published impact-fusion schemes.

**This family draws two schemes and never one machine.** The filed
proceedings describe a plane target struck by a flying plate and a
convergent target of solid fuel, in two different papers, and no filed
source pairs them. The level-0 record already carries both side by side
and says so in its non-claims; this tier carries both as two separate
models rather than as one body set, because placing them in a common
frame would assert a relationship no source states.

The plane scheme is two rectangular prisms. The worked case prints a
square cross-section, a fuel thickness and a plate thickness, and its
own figure shows the plate against the target against a rigid wall, so
the two bodies meet at the impact face and the plate lies behind it.

The convergent scheme is one solid sphere of the radius the other paper
prints. **No projectile is drawn for it**, because no filed source
prints one for any three-dimensional scheme, and no cone is drawn,
because the one conical scheme in the volume is four hand-drawn
schematics without a single dimension.

**Only one of the two schemes has a resolution at all.** A sphere is
tessellated by an inscribed polyhedron that converges as the counts
rise, so its model carries the segment and ring counts it was built at.
A prism has no curved surface: twelve triangles are the body exactly, at
every scale, and there is no count that could refine it. The plane
model's counts are therefore ``None`` rather than a number nothing
consumes, and a sweep over a resolution on that scheme would be
measuring nothing.

**The bodies of the convergent scheme are inscribed polyhedra of
revolution, not ideal spheres.** A consumer comparing a volume here to
``4/3 pi r^3`` would be comparing two different solids; the profile
volume of the body actually built is the reference. The prisms carry no
such caveat, and that asymmetry is the point of stating it.

Design record: ADR 0006.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Final

from scpn_reactor_kernels.errors import GeometryError
from scpn_reactor_kernels.geometry import (
    TriangleMesh,
    rectangular_prism,
    require_rings,
    require_segments,
    sphere_solid,
)

from scpn_icf_impact_core.configuration import DeviceConfiguration
from scpn_icf_impact_core.errors import DeviceGeometryError
from scpn_icf_impact_core.physics.level0 import (
    ProjectileDeclaration,
    SchemeDeclaration,
    target_radius_cm,
)
from scpn_icf_impact_core.physics.projectile import (
    areal_density_g_cm2,
    plate_thickness_cm,
)

MODEL_SCHEMA: Final = "scpn.impact-icf-3d-model.v1"
MODEL_SCHEMA_VERSION: Final = "1.0.0"

#: One centimetre in metres. The level-0 relations carry centimetres and
#: every body is built in metres; this is the only place the two meet.
#: The configuration's own micrometres are converted by the level-0
#: relation that owns them, never a second time here.
CENTIMETRE_M: Final = 1.0e-2

SCHEME_PLANE: Final = "plane"
SCHEME_CONVERGENT: Final = "convergent"

ROLE_DRIVER: Final = "driver"
ROLE_FUEL: Final = "fuel"
MATERIAL_URANIUM_PLATE: Final = "uranium_plate"
MATERIAL_FUEL_GAS: Final = "fuel_gas"
MATERIAL_SOLID_FUEL: Final = "solid_fuel_ice"

BODY_DRIVER_PLATE: Final = "driver_plate"
BODY_FUEL_SLAB: Final = "fuel_slab"
BODY_FUEL_SPHERE: Final = "fuel_sphere"

PLANE_BODY_NAMES: Final = (BODY_DRIVER_PLATE, BODY_FUEL_SLAB)
CONVERGENT_BODY_NAMES: Final = (BODY_FUEL_SPHERE,)

BODY_NAMES_BY_SCHEME: Final = {
    SCHEME_PLANE: PLANE_BODY_NAMES,
    SCHEME_CONVERGENT: CONVERGENT_BODY_NAMES,
}
"""The body set of each published scheme, in build order."""

SCHEMES_BY_IDENTIFIER: Final = {
    "projectile_or_impact_icf": (SCHEME_PLANE, SCHEME_CONVERGENT),
}
"""The schemes each owned configuration draws. The single owned
identifier draws both, because the proceedings dimension one target of
each kind and pair neither with the other."""

REFINABLE_SCHEMES: Final = frozenset({SCHEME_CONVERGENT})
"""Schemes whose bodies have a curved surface and therefore a
resolution. The plane scheme is faceted exactly at every deflection the
back-end accepts, so it has none and carries ``None``."""

SCHEMES_CONSUMING_DECLARATIONS: Final = frozenset({SCHEME_PLANE})
"""Schemes whose geometry needs a declaration beyond the configuration.
The plane scheme's plate thickness follows from the declared plate
material and face, and its fuel thickness is declared outright. The
convergent scheme needs only the target radius the configuration
carries, so it binds no declaration and says so with a null digest
rather than borrowing one it does not consume."""

MODEL_UNITS_BY_SCHEME: Final = {
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
            "z is the polar axis of the tessellation and carries no physical "
            "meaning: the target is a sphere and no source prints a drive "
            "direction for it"
        ),
        "origin": "the centre of the target",
    },
}
"""The frame each scheme is built in. They differ because the schemes
differ: the plane case has a direction the plate travels along and the
convergent case has none that any source prints."""

MODEL_NON_CLAIMS: Final = (
    (
        "analytic surfaces tessellated from a declared configuration and, for "
        "the plane scheme, declared plate and target dimensions; nothing here "
        "is integrated in time"
    ),
    (
        "the plane and the convergent scheme come from two different papers "
        "of one proceedings and no filed source pairs them; they are two "
        "models here for that reason and are never one machine"
    ),
    (
        "no projectile is drawn for the convergent scheme: the paper that "
        "prints that target prints no projectile for it, and no filed "
        "source in this family prints projectile geometry for any "
        "three-dimensional scheme"
    ),
    (
        "no cone is drawn: the one conical scheme the volume describes is "
        "four hand-drawn schematics with no cone angle and no dimension of "
        "any kind"
    ),
    (
        "no rigid wall, tamper, holder, standoff or vacuum enclosure is "
        "drawn; the worked case names a rigid wall and dimensions none of "
        "these"
    ),
    (
        "the plate and the target touch at the impact face because the "
        "worked case's own figure places them so; no filed source prints a "
        "standoff, and none is invented"
    ),
    (
        "the square cross-section is printed, and it is the only place "
        "squareness enters: the level-0 relations use the face area alone "
        "and never a side"
    ),
    (
        "the convergent scheme's bodies are inscribed polyhedra of "
        "revolution, never ideal spheres; the profile volume of the body "
        "built is its own reference"
    ),
    (
        "no body describes a target during a shot: these are the dimensions "
        "before the drive begins, and both schemes change all of them"
    ),
    "no body is a CAD solid or an engineering model",
    "no material property, load, field, dose or activation quantity is carried",
    "no value describes or validates any real machine or shot",
)


def _declaration_digest(record: dict[str, Any]) -> str:
    """Identify a declaration by the canonical bytes of its record.

    Parameters
    ----------
    record
        The declaration's JSON-serialisable record.

    Returns
    -------
    str
        SHA-256 of the canonical bytes as lowercase hex. The bytes are
        formed the way every other record in this repository is formed:
        sorted keys, minimal separators, one trailing newline, and no
        NaN or infinity anywhere.
    """
    text = json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()


def square_side_cm(impact_area_cm2: float) -> float:
    """Return the side of the printed square face, in centimetres.

    Parameters
    ----------
    impact_area_cm2
        Area of the face the plate presents, from the declaration.

    Returns
    -------
    float
        The side of a square of that area.

    Notes
    -----
    **The squareness is printed, and it enters here and nowhere else.**
    The worked case states a one-centimetre-by-one-centimetre
    cross-section and calls it sufficient for edge losses to be
    negligible. Every level-0 relation needs only the area, so the
    declaration carries only the area; a body needs two sides, and this
    is where the printed shape supplies the second one. A declaration
    whose area came from a face that was not square would build a body
    of the right area and the wrong outline, which is why this function
    exists rather than a bare square root at the call site.
    """
    return math.sqrt(impact_area_cm2)


def plane_extents_m(
    configuration: DeviceConfiguration,
    projectile: ProjectileDeclaration,
    scheme: SchemeDeclaration,
) -> tuple[float, float, float]:
    """Return the plane scheme's three extents in metres.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration carrying the plate's mass.
    projectile
        Declared plate material and the face it presents.
    scheme
        Declared dimensions carrying the target's fuel thickness.

    Returns
    -------
    (side, plate_thickness, slab_thickness)
        The side of the shared square cross-section, the thickness the
        declared plate material must have to carry the configuration's
        mass over that face, and the target's fuel thickness.

    Notes
    -----
    The plate thickness is not stored anywhere: it is obtained from the
    level-0 relations that own it, so a geometry and a physics record
    built from the same declaration cannot disagree about how thick the
    plate is.
    """
    side = square_side_cm(projectile.impact_area_cm2) * CENTIMETRE_M
    plate = (
        plate_thickness_cm(
            areal_density_g_cm2(
                configuration.projectile.mass_mg, projectile.impact_area_cm2
            ),
            projectile.material_density_g_cm3,
        )
        * CENTIMETRE_M
    )
    return side, plate, scheme.slab_thickness_cm * CENTIMETRE_M


def convergent_radius_m(configuration: DeviceConfiguration) -> float:
    """Return the convergent target's radius in metres.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration.

    Returns
    -------
    float
        The radius the configuration declares, converted from
        micrometres by the level-0 relation that owns that conversion
        and then once more into metres here.
    """
    return target_radius_cm(configuration) * CENTIMETRE_M


@dataclass(frozen=True, slots=True)
class DeviceModel3D:
    """The tessellated model of one configuration under one scheme.

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
    segments, rings
        Counts the curved bodies were tessellated at, or ``None`` for a
        scheme whose bodies have no curvature to refine.
    meshes
        The bodies, in the fixed order for that scheme.

    Raises
    ------
    DeviceGeometryError
        If the identifier or the scheme is unknown, if the identifier
        does not draw the scheme, if the body names or their order
        differ from the set the scheme owns, or if the resolutions or
        the declaration digests do not match what the scheme consumes.
    """

    identifier: str
    scheme: str
    configuration_digest_sha256: str
    projectile_digest_sha256: str | None
    scheme_digest_sha256: str | None
    segments: int | None
    rings: int | None
    meshes: tuple[TriangleMesh, ...]

    def __post_init__(self) -> None:
        """Validate the scheme, its body set and what it carries.

        Raises
        ------
        DeviceGeometryError
            If the identifier or the scheme is unknown, if the
            identifier does not draw the scheme, if the body names or
            their order differ from the set the scheme owns, or if the
            resolutions or the declaration digests do not match what
            the scheme consumes.
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
        names = tuple(mesh.name for mesh in self.meshes)
        if names != expected:
            raise DeviceGeometryError(
                f"meshes: bodies of the {self.scheme!r} scheme must be "
                f"exactly {expected!r} in order, got {names!r}"
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
        carried = (self.segments, self.rings)
        if refinable and None in carried:
            raise DeviceGeometryError(
                f"segments, rings: the {self.scheme!r} scheme has curved "
                f"bodies and must carry both counts, got {carried!r}"
            )
        if not refinable and carried != (None, None):
            raise DeviceGeometryError(
                f"segments, rings: the {self.scheme!r} scheme has no curved "
                f"surface and nothing to refine, so both must be None, got "
                f"{carried!r}"
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
            "schema": MODEL_SCHEMA,
            "schema_version": MODEL_SCHEMA_VERSION,
            "units": dict(MODEL_UNITS_BY_SCHEME[self.scheme]),
            "non_claims": list(MODEL_NON_CLAIMS),
            "identifier": self.identifier,
            "scheme": self.scheme,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "projectile_digest_sha256": self.projectile_digest_sha256,
            "scheme_digest_sha256": self.scheme_digest_sha256,
            "segments": self.segments,
            "rings": self.rings,
            "bodies": [
                {
                    "name": mesh.name,
                    "role": mesh.role,
                    "material_identifier": mesh.material_identifier,
                    "vertex_count": mesh.vertex_count,
                    "face_count": mesh.face_count,
                    "volume_m3": mesh.signed_volume_m3(),
                    "surface_area_m2": mesh.surface_area_m2(),
                }
                for mesh in self.meshes
            ],
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


def build_plane_model(
    configuration: DeviceConfiguration,
    projectile: ProjectileDeclaration,
    scheme: SchemeDeclaration,
) -> DeviceModel3D:
    """Tessellate the plane scheme's plate and target.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration supplying the plate's mass.
    projectile
        Declared plate material and the face it presents.
    scheme
        Declared dimensions supplying the target's fuel thickness.

    Returns
    -------
    DeviceModel3D
        The two-body model, plate first.

    Raises
    ------
    DeviceGeometryError
        If an extent is rejected by the library; its refusals are
        re-raised under the device error type with their messages.
    DeviceConfigurationError
        If a declared value leaves its documented interval.

    Notes
    -----
    **No count is taken and none is stored.** Both bodies are prisms and
    twelve triangles are each of them exactly; a caller that wanted to
    refine one would be asking a question with no answer, so there is no
    argument here to ask it with.
    """
    side, plate, slab = plane_extents_m(configuration, projectile, scheme)
    specification = (
        (BODY_DRIVER_PLATE, ROLE_DRIVER, MATERIAL_URANIUM_PLATE, -plate, 0.0),
        (BODY_FUEL_SLAB, ROLE_FUEL, MATERIAL_FUEL_GAS, 0.0, slab),
    )
    try:
        bodies = tuple(
            (name, role, material, rectangular_prism(side, side, low, high))
            for name, role, material, low, high in specification
        )
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    meshes = tuple(
        TriangleMesh(
            name=name,
            role=role,
            material_identifier=material,
            vertices=vertices,
            faces=faces,
        )
        for name, role, material, (vertices, faces) in bodies
    )
    return DeviceModel3D(
        identifier=configuration.identifier,
        scheme=SCHEME_PLANE,
        configuration_digest_sha256=configuration.digest_sha256(),
        projectile_digest_sha256=_declaration_digest(projectile.to_record()),
        scheme_digest_sha256=_declaration_digest(scheme.to_record()),
        segments=None,
        rings=None,
        meshes=meshes,
    )


def build_convergent_model(
    configuration: DeviceConfiguration, segments: int, rings: int
) -> DeviceModel3D:
    """Tessellate the convergent scheme's target.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration supplying the target radius.
    segments
        Circumferential segments; at least 8, multiple of 8.
    rings
        Polar steps from pole to pole. Independent of ``segments``: this
        one sets the profile, the other sets what the revolution keeps
        of it.

    Returns
    -------
    DeviceModel3D
        The one-body model.

    Raises
    ------
    DeviceGeometryError
        If a count or the radius is rejected by the library; its
        refusals are re-raised under the device error type with their
        messages.

    Notes
    -----
    **No declaration is consumed and none is identified.** The radius is
    the configuration's own and nothing else about this target is
    printed anywhere; the record's null declaration digests say exactly
    that.
    """
    try:
        require_segments(segments)
        require_rings(rings)
        vertices, faces = sphere_solid(
            convergent_radius_m(configuration), 0.0, segments, rings
        )
    except GeometryError as exc:
        raise DeviceGeometryError(str(exc)) from exc
    return DeviceModel3D(
        identifier=configuration.identifier,
        scheme=SCHEME_CONVERGENT,
        configuration_digest_sha256=configuration.digest_sha256(),
        projectile_digest_sha256=None,
        scheme_digest_sha256=None,
        segments=segments,
        rings=rings,
        meshes=(
            TriangleMesh(
                name=BODY_FUEL_SPHERE,
                role=ROLE_FUEL,
                material_identifier=MATERIAL_SOLID_FUEL,
                vertices=vertices,
                faces=faces,
            ),
        ),
    )
