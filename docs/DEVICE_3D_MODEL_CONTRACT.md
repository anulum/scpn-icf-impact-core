<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Impact Core — device model contract
-->

# Device model contract

What a consumer of this repository's geometry receives, and what it may
not conclude from it.

## The three things to read first

**This family draws two schemes and never one machine.** The filed
proceedings describe a plane target struck by a flying plate and a
convergent target of solid fuel, in two different papers, and **no filed
source pairs them**. They are two models here, each in its own frame,
with no transformation between them anywhere in this repository. A
consumer that places one relative to the other is asserting something no
source states.

**The convergent scheme's body is an inscribed polyhedron of
revolution**, not a sphere. Its own profile — the frustum stack it was
built from — is its analytic reference. Comparing its volume to
`4/3 π r³` compares two different solids: at the declared counts the
polyhedron is 10.17 % smaller, and that number is a property of the
comparison rather than of the model. **The plane scheme's bodies carry
no such caveat**: a prism is faceted exactly, and the asymmetry between
the two schemes is the point.

**Only one scheme has a resolution.** The convergent model carries the
segment and ring counts it was built at; the plane model carries
`None` for both, and its builders take no such argument. A consumer that
wants to sweep a resolution over the plane scheme is asking a question
with no answer.

## The two tiers

| Tier | Schema | Built by |
|---|---|---|
| G1, tessellated | `scpn.impact-icf-3d-model.v1` | `build_plane_model`, `build_convergent_model` |
| G2, B-rep | `scpn.impact-icf-cad-model.v1` | `build_plane_cad`, `build_convergent_cad` |

Both schemas are at version `1.0.0`. Tier G2 requires the optional
`cad` extra; every other capability of this package works without it.

## Units and frames

Length is the metre and the handedness is right in both schemes. The
frames differ, because the schemes do.

| Scheme | Axis | Origin |
|---|---|---|
| `plane` | `z` along the plate's direction of travel | the impact face |
| `convergent` | `z` is the tessellation's polar axis and carries **no** physical meaning | the centre of the target |

The convergent scheme's axis is a statement about the source: nothing
prints a drive direction for that target, so the polar axis is an
artefact of how a body of revolution is built and must not be read as
one.

The configuration carries **micrometres** and the level-0 relations
carry **centimetres**. The micrometres are converted by the level-0
relation that owns them (`target_radius_cm`), and the geometry converts
centimetres to metres once, at `CENTIMETRE_M`, and nowhere else.

## The bodies

| Scheme | Body | Role | Material token | Extent |
|---|---|---|---|---|
| `plane` | `driver_plate` | `driver` | `uranium_plate` | square face, `z` from `−t` to `0` |
| `plane` | `fuel_slab` | `fuel` | `fuel_gas` | square face, `z` from `0` to the declared thickness |
| `convergent` | `fuel_sphere` | `fuel` | `solid_fuel_ice` | the configuration's target radius |

The order is fixed and both tiers refuse any other.

## Where each dimension comes from

| Dimension | Source |
|---|---|
| square face, both plane bodies | **printed**: a 1 cm × 1 cm cross-section |
| plate thickness | **computed** from the configuration's plate mass, the declared face area and the declared material density, by the level-0 relations that own them; floors to the printed 2.7e-3 cm |
| target fuel thickness | **declared** in `SchemeDeclaration`, from the printed 1 cm |
| convergent target radius | **declared** in the configuration, from the printed 1 mm |

The plate thickness is stored nowhere. It is obtained from the level-0
relations every time, so a physics record and a geometry model built
from the same declaration cannot disagree about it.

## Resolutions

| Scheme | Segments | Rings | Linear deflection | Angular deflection |
|---|---|---|---|---|
| `plane` | — | — | `1e-6 m`, bounds nothing | `0.3 rad`, bounds nothing |
| `convergent` | 8 | 33 | `2e-7 m` | `0.3 rad` |

Every value was measured on this family's own bodies; see ADR 0006 for
the scans. The convergent ring count is the top of the regime in which
every count is exact, the first refusal is at 34, and 35 is exact again.
The linear threshold is `1.1222500795e-7 m` exactly and the declared
value sits at 0.5611 of its bound. The angular value sits inside the
plateau from 0.2 to 1.0 radians, where the deficit is at its maximum and
does not depend on the exact value.

## Exports and identity

Each model records the canonical SHA-256 of its own record, and each
tier-G2 model records the SHA-256 of its normalised STEP bytes. The two
schemes produce **two** exports with different digests; there is no
combined export and there is no assembly containing both.

Each record identifies the declarations its scheme actually consumes —
the plane scheme two, the convergent scheme none — and refuses to carry
a digest for one it does not.

Determinism of the STEP bytes is claimed within one pinned back-end
environment only, never across back-end versions.

## Declared limits

- The back-end refuses a linear deflection below about `1e-8 m` on these
  bodies, with a numeric error of its own that is unrelated to any
  declared bound.
- The convergent body's checked deficit bound is `2 d / r`; the plane
  bodies' is a round-off tolerance of `1e-12`, and both are compared in
  magnitude rather than one-sidedly.
- The mesh-difference bound and the faceted-volume bound are not
  independent: the absolute margin between the mesh difference and its
  bound is exactly the faceted deficit, at every segment count. Raising
  the segment count tightens both sides equally.
- A declaration whose every value is individually valid can still
  produce a plate of zero thickness by underflow; the geometry refuses
  it, because the level-0 relations validate their inputs and not their
  results.

## Non-claims

Both tiers carry their non-claims inside their records and inside the
STEP metadata, so a file read on its own still states them. In summary:
no source pairs the two schemes; no projectile is drawn for the
convergent scheme and no cone is drawn at all; no rigid wall, tamper,
holder, standoff or enclosure is drawn; no body describes a target
during a shot; no material property, load, field, dose or activation
quantity is carried; and no value describes or validates any real
machine or shot.
