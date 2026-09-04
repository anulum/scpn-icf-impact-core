<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Impact Core — ADR 0006
-->

# ADR 0006 — Device 3D and CAD models of two published schemes

Status: accepted (2026-09-04). Builds on ADR 0005 (level-0 device
physics), which established that this family's filed proceedings
describe **two** target geometries and pair neither with the other.

## Context

ADR 0005 recorded the shape of the source. The dimensioned worked case
is a plane slab of square cross-section driven by a flying plate against
a rigid wall. The only anchored convergent target is a solid fuel sphere
in a different paper of the same volume, for which **no projectile is
printed anywhere**. The conical scheme the volume also describes is four
hand-drawn schematics with no cone angle and no dimension of any kind.

The level-0 record carries both dimensioned schemes side by side and
states in its non-claims that no filed source pairs them. The geometry
tiers face the same fact and must answer the same question, but they
face it in a harder form: a record can hold two sets of numbers side by
side, whereas a body has to be *placed somewhere*.

Until 2026-09-04 there was also a second obstacle. The shared kernel
library built only solids of revolution, so the one scheme this source
fully dimensions could not be drawn at all. The library gained a
rectangular prism at commit `4095aa8`, and this repository is its first
consumer.

## Decision

### Two schemes, two models, and no common frame

**Each scheme is its own model, with its own origin, its own body set
and its own export.** Neither model contains the other's bodies, and no
transformation between the two frames exists anywhere in this
repository.

The alternative — one assembly holding all three bodies — would have
required choosing where to put the sphere relative to the slab. Any
choice is a statement about a relationship that no filed source makes.
Two models make the absence structural rather than documentary: there is
no field in which a relative placement could be written down.

Within the plane scheme the bodies *are* placed relative to one another,
and that placement is printed: the worked case's own figure shows the
plate, then the target, then a rigid wall. The plate therefore lies
behind the impact face and the target ahead of it, meeting at the
origin, with no standoff, because none is printed.

### What is drawn and what is not

| Scheme | Bodies | Frame |
|---|---|---|
| `plane` | `driver_plate`, `fuel_slab` | z along the plate's travel; origin at the impact face |
| `convergent` | `fuel_sphere` | z is the tessellation's polar axis and carries no physical meaning |

Not drawn, each for a stated reason: the rigid wall, tamper, holder and
enclosure (nothing dimensions them); a projectile for the convergent
scheme (nothing prints one for any three-dimensional scheme); a cone
(nothing dimensions one); and any state during a shot (these are the
dimensions before the drive begins).

### The square cross-section enters once

The level-0 relations need only the plate's face **area**, so the
declaration carries only the area. A body needs two sides. The worked
case prints a one-centimetre-by-one-centimetre cross-section, so the
squareness is an anchor rather than a model choice, and it enters in
exactly one function — `square_side_cm` — whose docstring says so.

### Only one scheme has a resolution, and the models say which

`DeviceModel3D` and `DeviceModelCAD` carry `segments` and `rings` as
`int | None`, and both refuse the mismatch: the convergent scheme must
carry both counts and the plane scheme must carry neither. The plane
builders do not take the arguments at all, and a test asserts their
absence on the signature.

This is not tidiness. **A tier that sweeps a resolution over a prism is
measuring nothing**, and a parameter that changes no output is worse
than no parameter, because a reader assumes it does something.

The same rule governs provenance. The plane scheme consumes two
declarations and identifies both by digest; the convergent scheme
consumes none — its only dimension is the configuration's own target
radius — and identifies none. Carrying a digest a scheme does not
consume would be a false statement about where a body came from, so the
record refuses it.

## What was measured, on this family's own bodies

Every number below came from this family's bodies built against the
pinned library commit. None was inherited from a sibling.

### The convergent scheme: the ring regime was scanned, not sampled

Every count from **4 to 33** is exact on the 1 mm target. **34 refuses**,
reporting a volume relative error of 9.80e-5 against a 1e-9 tolerance.
From 34 to 54 the counts alternate — every even count refuses, every odd
count is exact — and from **55 upward every count refuses**.

The default is 33, the top of the first regime, and the refusal test
asserts 34, the step immediately above it. A second test asserts that 35
builds, so that a reader does not mistake the first refusal for a
ceiling.

The sibling families measured 39 at 1.503 mm and 41 at 1.8 mm. This
family's target is smaller and its boundary is lower, which is what the
group's radius sweep predicted and is exactly why each family measures
rather than inherits.

### The convergent scheme: the angular deflection binds here

This differs from the sibling beam family, whose bodies are larger, and
it is the reason the declared value is not simply copied.

At 33 rings the faceted volume relative deficit is **2.244500159e-04** at
every angular deflection from **0.2 to 1.0 radians** — identical to every
digit, at 27 616 triangles — and then falls: 2.2427e-4 at 0.1, 2.0433e-4
at 0.05, 1.3329e-5 at 0.01.

**The declared value sits inside the plateau**, at 0.3. On the plateau
the deficit is at its maximum over the whole range and does not depend
on the exact value chosen, so the bound established there holds for
every finer setting too. Choosing a value below the plateau would have
bought a smaller deficit at the price of a claim that depends on a
mesher parameter in a region where it is still moving.

### The convergent scheme: the linear deflection is a threshold

It does not change the model. The deficit is identical at 5e-7, 3e-7,
2e-7, 1.5e-7, 1.2e-7 and 1.13e-7 metres. What moves is the declared
bound, which is `2 d / r`.

So the smallest deflection this body clears is `deficit * r / 2` =
**1.1222500795e-7 m**, computed rather than searched for and then
confirmed: 1.1223e-7 m passes at a ratio of 1.0000 and 1.1222e-7 m
refuses. The declared **2e-7 m** puts the body at **0.5611** of its
bound — a stated margin against back-end drift rather than the strongest
claim available.

### The two bounds are not independent, and the ratio misleads

The mesh-difference ratio looks alarming at the reference segment count:
0.9977 of its bound at eight segments. Measured at 8, 16, 24 and 32
segments, the **absolute** margin is `2.2445e-4` at every one of them —
that is, exactly the faceted volume deficit, because the difference is
the inscribed-polygon deficit minus the faceting deficit. Raising the
segment count tightens both sides equally and buys nothing. A reader who
saw only the ratio would tighten the wrong knob, so a test states the
identity.

### The plane scheme: there is nothing to choose

The back-end returns **8 vertices and 12 triangles** for each prism at
every linear deflection it accepts — 1e-7 to 1.0, seven orders — and at
every angular deflection from 0.01 to 1.0 radians. No deflection changes
any measure. The declared values are mesher inputs and bound nothing.

Below 1e-8 metres the mesher refuses outright with a numeric error of
its own, unrelated to any body or bound. The declared 1e-6 m sits two
orders above it.

### The plane scheme is why the library's comparison is two-sided

The plate's faceted volume deviates from its analytic form by
**+2.99e-16** and the target's by **−2.12e-16**: **opposite signs, in one
assembly**. This is the first consumer in the group whose own bodies
show both.

The library's earlier one-sided check — `deficit > bound` — would have
admitted the target's deviation at any magnitude whatever. It was made a
magnitude comparison in `4095aa8`, and this family's assembly is the
concrete case that would have slipped through.

Both deviations are far inside the declared `1e-12` planar tolerance. A
tolerance nothing can violate is not a gate, so a test shows that this
family's own prisms are still refused when a reference is wrong by one
part in ten thousand.

### The geometry catches an underflow the physics does not

The level-0 relations validate their **inputs**, not their results. A
plate mass of 1e-300 mg and a material density of 1e300 g/cm³ each pass
every declaration and then divide to exactly zero thickness. The library
refuses the degenerate prism and this tier re-raises the refusal. The
handler is therefore live code with a test, not an unreachable branch
kept for appearance.

## Becoming a consumer of the shared kernel library

This repository had no dependency on `scpn-reactor-kernels` before this
change. It now pins **`4095aa8`** — the commit that added the prism — in
`pyproject.toml` (both the dependency and the `cad` extra), in
`reactor-domain.json` (with the kernel inventory digest
`704bcca7…`) and in a repository contract test that holds all three to
one commit.

**It is pinned one commit ahead of every other consumer, deliberately.**
Ten families pin an older digest and have no reason to move; each
repository holds its own pin against its own manifest, so mixed pins are
structurally fine. Moving pins that had no reason to move is what broke
six repositories earlier in this rollout.

Twelve kernels are named, reached by following what the two geometry
modules import rather than by copying a sibling's list. The list matches
the laser family's twelve and is not the beam family's eleven: both this
family and the laser family draw a body with no curved surface and so
consume the primitives kernel, while the beam family draws only spheres.

**This repository widens an open audit finding by joining it.** The
manifest validator does not inspect the `kernel_library` field, so
nothing but the contract test makes the pin and the dependency agree.
That gap is fleet-wide, it is recorded here and in the contract test's
own docstring, and it is not resolved locally: resolving it changes the
shared standard and is owner-authorised.

## Consequences

- Two capabilities are declared: `device_3d_model` and
  `device_cad_model`, each with its own `VALIDATION.md` section.
- Three workflows gain an install step, one of which also installs the
  system library the mesher links against.
- 100 % statement and branch coverage of both new modules, with no
  suppression and no unreachable handler.
- Every declared tolerance and count in this family has a test proving
  it still refuses something.
