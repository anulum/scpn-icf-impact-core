<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN Icf Impact Core — ADR 0005
-->

# ADR 0005 — Level-0 device physics of an impacted target, in two geometries

Status: accepted (2026-09-04). Builds on ADR 0002 (device configuration
model), which owns the projectile's mass and velocity, the target's
outer radius, and the kinetic-energy relations that follow from the
first two.

## Context

The proceedings this repository cites are on file and freely published:
*Proceedings of the Impact Fusion Workshop*, LA-8000-C (Los Alamos
Scientific Laboratory, 1979). Two of its papers carry geometry, and
**they describe two different schemes.**

**The dimensioned scheme is a plane slab.** Christiansen's worked case
(printed p. 33) drives a uranium plate at 200 km/s into fuel gas at
10 bar, through four states, to 4.2 times the cryogenic density. It
prints every dimension: the plate's areal density, its thickness, the
fuel thickness before and after, the energy per unit area, and a
1 cm × 1 cm cross-section stated as wide enough for edge losses to be
negligible.

**The convergent scheme is barely dimensioned at all.** Marshall
(printed p. 27) prints one target — a 1 mm radius sphere of solid fuel,
compressed by ten in radius to an areal density of 2 g/cm² — and **no
projectile for it**. His conclusion about the plane scheme is that
"simple one-dimensional shock heating is unsuitable for fusion power
production", because plane slab systems imply about a gram of fuel.
Christiansen's own conical variant (printed p. 40) is four hand-drawn
schematics with no cone angle and no dimension.

**The volume is a scan.** It carries an optical transcription, and the
scan duplicates some early leaves, so the printed-page to document-page
offset is not constant. Every value was read off pages rendered at
170 dpi and every citation gives both numbers.

## Decision

**Both schemes are carried, and the record says they are two.** The
repository owns one configuration and that configuration has one
projectile and one target radius, so a record that silently paired
Christiansen's plate with Marshall's sphere would describe a design no
paper contains. The record therefore evaluates each scheme on what its
own paper prints, and its non-claims state that no filed source pairs
them — in those words, asserted by a test.

**Three surfaces, split by subject rather than by geometry.**
`projectile` is what the flying plate carries onto whatever it strikes;
`fuel` is what the fuel is, in a slab and in a sphere; `compression` is
where that fuel ends up. Splitting by geometry instead would have put
the same areal density in two modules and the same specific energy in
both.

**The kinetic energy is not restated.** The configuration's own
projectile owns `E = m v² / 2` and `e = v² / 2`, and this package
consumes the second rather than recomputing it. A test asserts that
over the printed one-square-centimetre face the two routes agree bit for
bit, which is what shows the energy is not being counted twice.

**Nothing runs backwards**, which is the difference from the sibling
beam family. That family's sources print a yield and never a burn-up
fraction, so it implies one; here **no filed source prints either**. So
rather than invent a fraction, the record carries the energy a complete
burn of each inventory would release, which is an upper bound, is named
one, and needs no unsourced input. Marshall makes the same statement in
the same direction about one gram of fuel.

**No shock is solved.** The four printed states are connected by the
Rankine-Hugoniot relations and an equation of state, neither of which
this repository carries. The record takes the first and the fourth and
states what they imply for the dimension — which is the step the worked
case itself performs in one line. The two intermediate states stay in
the fixtures, where a test asserts only that the chain rises
monotonically.

**The refusals live on the declarations.** Unlike the sibling family,
no quantity here is built from a configuration field and a declaration
field at once in a way that can be geometrically impossible, so there is
no composition-level refusal to write and none is invented. What is
refused is a fuel gas at or above its own cryogenic liquid density —
which is not the gas the declared pressure and temperature describe — a
final state no denser than the initial one, and a radial compression
factor at or below one.

**The plate-to-fuel mass ratio is reported and not enforced.** The
worked case solves its own Eq. (6) for exactly this quantity and states
in words that there must be "sufficient mass of the projectile for a
given mass of DT". That criterion is an equation this repository does
not carry, so refusing on a threshold the volume never printed would be
an invention. The ratio goes in the record at 24.4 and the docstring
says why it is not a gate.

## What is printed, what is measured, what is not reproduced

Printed and reproduced:

- the plate's areal density, 0.052 g/cm², exactly, from the mass its
  printed face and areal density imply;
- the energy per unit area, 1.04 MJ/cm², to one unit in the last place
  of a double — a bound, asserted as one;
- the compression ratio of the printed end states, 420;
- the convergent target's areal density, 2.13 g/cm² against a printed
  2 g/cm² at the one significant figure that figure carries.

Measured, rather than assumed:

- **The volume truncates rather than rounds, on two independent
  values.** The plate thickness its own relation gives is 2.7659e-3 cm
  and it prints 2.7e-3; the compressed fuel thickness mass conservation
  gives is 2.3810e-3 cm and it prints 2.3e-3. Rounding would have given
  2.8e-3 and 2.4e-3, so a test asserting rounding would have failed on
  both. This is the third time in this rollout that a source has been
  found to floor rather than round, and the second where a test written
  the obvious way would have been wrong.
- **A driven slab gains no areal density at all.** Its density rises by
  exactly the factor its thickness falls by and the two cancel; a
  converging sphere gains the square of its radial factor. That is the
  convergent paper's objection to the plane scheme stated as arithmetic,
  and at these declared dimensions it is a factor of 1000 between the
  two targets.
- **The printed pressure, temperature and density ratio are mutually
  consistent to the one figure the ratio carries.** The ideal-gas law on
  10 bar and 300 K gives 0.009466 of the cryogenic density against a
  printed 0.01, 5.3 % apart. It is recorded as a consistency instrument
  and not an anchor, because it assumes an ideal gas of diatomic
  molecules and the volume states neither.

Printed and **not** reproduced, recorded rather than absorbed:

- **The convergent target's mass.** At the cryogenic density the volume
  prints elsewhere, a 1 mm sphere masses 0.8922 mg, not the printed
  0.84 mg; the printed value needs about 0.2005 g/cm³. The two printed
  statements about that sphere — its mass and its areal density — do not
  use the same density, and only the areal density reproduces. No input
  was adjusted to make the mass come out.
- **The energy of a one-gram burn.** The nuclear masses give 337.5 GJ
  against a printed "nearly 400 GJ", about 19 % apart. The volume's
  neighbouring "50 tons of TNT" is not in contradiction with it, because
  the sentence between them says that not all of the energy produces
  explosive yield.

## Consequences

- One capability is declared, `level0_device_physics`, at
  `computational_prototype` maturity.
- The projectile's mass is not printed by the volume and is derived from
  its printed areal density and its printed face, so recovering that
  areal density from it is a round trip. The fixture is named
  `DERIVED_` and the test that reproduces the areal density says which
  of the two is the anchor.
- The lint configuration's complexity note already anticipated level-0
  physics functions in this repository; as of this change that note
  describes something that exists.
- 100 % statement and branch coverage of the new package.
