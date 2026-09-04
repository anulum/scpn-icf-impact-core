<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Impact Core — VALIDATION
-->

# Validation

Every gate currently active in this repository, with its exact scope,
followed by the evidence record of each implemented capability.

## Local gates

| Gate | Command | Scope |
|---|---|---|
| Lint | `ruff check .` | all Python under `src/`, `tools/`, and `tests/` |
| Format | `ruff format --check .` | same scope |
| Typing | `mypy --strict src tools tests` | zero errors, strict mode |
| Tests + coverage | `pytest -q --cov=src --cov=tools --cov-branch --cov-fail-under=100` | 100 % statement and branch coverage of `src/` and `tools/` |
| Domain manifest | `python3 tools/validate_reactor_domain.py reactor-domain.json` | schema, registry version/digest, exact configuration set, capability inventory shape and ceiling rule, safety boundary |
| Studio descriptor | `python3 tools/derive_studio_descriptor.py --check` | committed descriptor byte-identical to a fresh derivation |
| Capability inventory | `python3 tools/generate_capability_inventory.py --check` | committed inventory byte-identical to a fresh generation |
| Licensing | `reuse lint` | REUSE 3.x compliance of the full tree |
| Workflow lint | `actionlint` | all files under `.github/workflows/` |
| Workflow modularity | `python3 tools/audit_workflows.py` | distributed workflow inventory: single ownership per job, coordinator/gate contract, action pinning, size ceilings |
| Documentation | `python3 tools/preflight.py --only docs` | UTF-8 readability and relative-link integrity of every Markdown file |
| Orchestrated | `python3 tools/preflight.py` | fail-closed run of all gates above |

## Workflow gates

Definitions are present in-repository; they run on the hosted platform
only once a remote exists under separate owner authority.

The hosted surface is modular: `ci.yml` is a coordinator that carries
only trigger policy, two reusable-workflow calls, and one stable
fail-closed `gate` job aggregating every category (failure,
cancellation, and unexpected skips all fail the gate). Every job is
declared and owned exactly once in the versioned inventory
`.github/workflow-inventory.json`, which the workflow-modularity guard
verifies locally and in hosted CI.

| Workflow | Purpose |
|---|---|
| `ci.yml` | coordinator and stable required gate |
| `reusable-static-policy.yml` | lint, format, typing, domain policy, workflow guard |
| `reusable-tests.yml` | tests with complete statement and branch coverage |
| `pre-commit.yml` | exact pre-commit parity |
| `codeql.yml` | Python code scanning |
| `security-audit.yml` | secrets, dependency, licence, and workflow policy |
| `docs.yml` | strict documentation and link validation, no deployment |
| `sbom.yml` | reproducible dependency inventory, no release |
| `scorecard.yml` | read-only supply-chain analysis |

## Shared ecosystem gate

From the monorepo root:

```bash
python3 agentic-shared/scripts/repository_tier0_scaffold_audit.py \
  03_CODE/SCPN-ICF-IMPACT-CORE --json
```

proves the Tier-0 local-scaffold machine profile (required and forbidden
paths, Git/remote boundary, workflow pins and permissions, badge non-claims,
JSON integrity, defensive ignore rules).

## Device configuration model

Evidence record of the `device_configuration_model` capability
(`computational_prototype`; design record: `docs/adr/0002-device-configuration-model.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen parameter objects (`Projectile`, `TargetDeclaration`,
  `DeviceConfiguration`) rejecting non-finite values and non-positive
  extents — every rejection branch is tested.
- The standard-mechanics relations `E = m v^2 / 2` and `e = v^2 / 2` as
  documented derived quantities, with an advisory finding for projectile
  velocities below the documented impact-fusion entry scale ~100 km/s
  (Proc. Impact Fusion Workshop, LA-8000-C, 1979), reported and never
  clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.
- A data-only pin equality check binding the model to the SPO reactor
  registry version and digest declared in `reactor-domain.json`.

Bounded claims — what is NOT claimed:

- No parameter set describes, approximates, or validates any real
  machine; every exercised parameter set is a synthetic test fixture.
- The estimates are advisory regime checks, not launcher, impact, or
  yield results; no benchmark, dataset, solver, controller, or
  experimental correlation exists in this repository.

## Diagnostic and clock semantics

Evidence record of the `diagnostic_clock_semantics` capability
(`computational_prototype`; design record: `docs/adr/0003-diagnostic-clock-semantics.md`).

What is exercised, all under the 100 % statement-and-branch coverage gate:

- Validated frozen declaration objects (`ClockModel`,
  `DiagnosticChannelPlan`, `DeferredCandidate`, `DiagnosticPlan`)
  rejecting catalogue misalignment: inapplicable candidates,
  inadmissible carriers, evidence-vocabulary mismatches, incompatible
  clock kinds, Nyquist violations, unresolvable event-timing bounds,
  and incomplete candidate coverage — every rejection branch is tested.
- A data-only pin (`ObservabilityBinding`) to the SPO
  observability-profile catalogue release `1.0.0`
  (`d70c0de696534e5a77066ef8420cf7ca17bc4d7321984b0ac83523dbc1dce609`),
  bound in turn to reactor registry `1.0.0`; a plan pinned to any other
  release is rejected.
- A reference plan mirroring canonical practice with synthetic
  declarations: impact-timing train, trajectory radiography, asymmetry mode set, shot-outcome set, synthetic oscillator, each bound to its clock domain.
- Documented advisory band and timing checks with their sources stated
  in the code: impact-asymmetry bands of 0.1 MHz–1 GHz and ns-scale projectile timing (LA-8000-C 1979); findings are reported, never clamped.
- Canonical serialisation (sorted keys, NaN/infinity rejected on both
  emit and parse), SHA-256 digest identity, and a strict round-trip
  parser that refuses unknown fields.

Bounded claims — what is NOT claimed:

- No channel describes a real diagnostic, measurement, or facility;
  every plan is a synthetic declaration of HOW evidence slots would be
  bound, marked `synthetic=True` by hard invariant.
- No SPO semantic-profile ingress is declared; the profile registry
  `ingress_state` for this device family remains `not_declared`, and
  no adapter, producer, or handoff exists in this repository.

### Portable plan envelope

The `diagnostic_clock_semantics` capability additionally exercises a
producer-owned portable envelope
(`src/scpn_icf_impact_core/plan_envelope.py`,
`scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): one
canonically serialised object carrying the exact project identity and
owned configurations, the capability and its maturity, the
synthetic/review-only/non-actuating statements, both SPO registry pins,
the SHA-256 digest of the inner canonical plan, the producer revision,
and fixed no-observation/no-control non-claims. The committed immutable
fixture (`tests/data/plan_envelope_fixture.json`, byte hash pinned in
the tests) is verified together with positive, tamper, wrong-project,
wrong-configuration, registry-drift, duplicate-member, and non-finite
rejection paths, all under the 100 % coverage gate. The envelope claims
nothing beyond the enveloped synthetic declaration.

### Typed frames, clock relations, and acquisition geometry

The deepened model adds typed reference frames (per-repository allowed
`FrameKind` subset; every noncyclic `coordinate_frame` binding must
reference a declared frame), clock synchronisation relations
(synthetic offset/uncertainty BOUNDS between declared non-simulation
clocks with an explicit method statement — no correlation evidence is
claimed and no clock is mapped to physical wall time), and per-channel
acquisition windows and element counts with device-cited advisory
scales. Both decoders are hardened per the SPO intake architecture:
recursive exact-key refusal in every nested entry, duplicate-member
refusal, and byte-canonical refusal (a document that is not exactly
canonical bytes is rejected). The envelope is `1.1.0`, adding
`manifest_sha256` — the SHA-256 of the committed canonical
`reactor-domain.json` — verified in tests against the committed file.
All declarations remain synthetic; nothing here observes or controls
anything.

### Signal inventories, frame transformations, and clock topology

The depth slice (envelope `1.2.0`; a `1.1.0` document is refused by the
`1.2.0` codec and vice versa — no defaults, no cross-version coercion;
`1.1.0` remains historical custody at the consumer) adds three typed
declaration surfaces, every branch under the 100 % statement-and-branch
gate:

- A per-channel **signal inventory** (`SignalDeclaration`: identifier,
  quantity, unit, role, description). Hard rules: non-empty, unique and
  sorted; exactly one `carrier`; a `timing_marker` in `"s"` exactly for
  event-relative channels and forbidden otherwise; numerical-only
  channels declare a single `phase`/`rad` carrier. Quantity and unit are
  declared tokens — no SI or UCUM validation is performed or claimed —
  and no declaration creates or overrides a candidate, carrier,
  observation, or phase: the candidate profile stays authoritative. An
  advisory flags a multi-element cyclic array without an amplitude
  signal.
- **Frame transformations** (`FrameTransformation`) between declared
  frames: kind admissibility fixed by frame-kind pair (`flux_mapping`
  for machine↔flux, flux↔Boozer, field-line↔machine; `projection` for
  blanket↔machine; `rigid` for chamber↔beamline), `equilibrium_dependent`
  exactly for flux mappings, at most one transformation per frame pair,
  sorted by source then target, and — with two or more frames — a
  connected transformation graph. Methods are declarations;
  `evidence_claimed` is always `False`.
- A **clock topology** (`ClockDomain`, `ClockTopology`): every physical
  clock in exactly one domain, the simulation clock in none; a domain
  holding a facility clock is rooted there, otherwise at its shot-event
  epoch; every non-root member declares a relation to its root; every
  non-reference root declares a relation to the reference root (star);
  relations must not form a cycle. The reference plan declares one
  domain (`clk_facility` root, `clk_shot` member); multi-domain rules
  are exercised by test-constructed plans. Scopes are declarations;
  `mapping_state` stays `unmapped`.

## Level-0 device physics

Evidence record of the `level0_device_physics` capability
(`computational_prototype`; design record:
`docs/adr/0005-level0-device-physics.md`).

Every anchor below is read from the proceedings this repository cites,
*Proceedings of the Impact Fusion Workshop*, LA-8000-C (Los Alamos
Scientific Laboratory, 1979), which is on file and freely published. The
volume is a scan carrying an optical transcription, so every value was
read off pages rendered at 170 dpi rather than off the text layer, and
the scan duplicates some early leaves, so printed-page and document-page
numbers are both given throughout and do not differ by a constant.

**Two papers in the volume carry geometry and they describe two
different schemes**: a fully dimensioned plane slab driven by a uranium
plate, and a solid fuel sphere with no projectile printed for it
anywhere. The record evaluates each on what its own paper prints, and
its non-claims state that no filed source pairs them.

What is exercised, all under the 100 % statement-and-branch coverage
gate:

- What a flying plate carries: its mass per unit of the face it
  presents, the thickness a chosen material needs to carry that, and the
  energy the face delivers per unit area.
- The fuel in both geometries: absolute densities from the printed
  ratios, the mass and areal density of a slab and of a sphere, and the
  deuterium-tritium specific energy built from the two nuclear masses
  and the energy released per reaction rather than carried as a rounded
  constant.
- Where the fuel ends up: one-axis compression by conservation of mass,
  and convergent compression as the cube of a radial factor.
- A composed record over both schemes, with canonical serialisation
  (sorted keys, NaN and infinity rejected) and SHA-256 digest identity,
  naming the digest of the configuration it was built from.
- Every declared quantity validated where it is declared as well as
  inside the relation that consumes it.

Anchors — printed values reproduced, and nothing further:

- The plate's areal density, 0.052 g/cm², exactly.
- The energy the plate's face delivers, 1.04 MJ/cm², to one unit in the
  last place of a double. Asserted as a bound, because it is one.
- The compression ratio the two printed end states set, 420.
- The convergent target's areal density, 2.13 g/cm² against a printed
  2 g/cm², at the one significant figure that figure carries.

Measured, rather than assumed:

- **The volume truncates rather than rounds, on two independent
  values.** Its own relation gives a plate thickness of 2.7659e-3 cm and
  it prints 2.7e-3; mass conservation gives a compressed fuel thickness
  of 2.3810e-3 cm and it prints 2.3e-3. Rounding would have given
  2.8e-3 and 2.4e-3, so a test asserting rounding would have failed on
  both. Both tests assert the truncation and assert that the rounding is
  a different number.
- **A driven slab gains no areal density.** Its density rises by exactly
  the factor its thickness falls by. A converging sphere gains the
  square of its radial factor instead, and at these declared dimensions
  the two targets differ by a factor of 1000. That is the convergent
  paper's objection to the plane scheme, stated as arithmetic.
- **The printed gas state is self-consistent to one figure.** The
  ideal-gas law on the printed 10 bar and 300 K gives 0.009466 of the
  cryogenic density against a printed 0.01, 5.3 % apart. Recorded as a
  consistency instrument and used as an anchor nowhere, because it
  assumes an ideal gas of diatomic molecules and the volume states
  neither.

Printed and **not** reproduced, recorded rather than absorbed into a
tolerance:

- **The convergent target's mass.** At the cryogenic density the volume
  prints elsewhere, its 1 mm sphere masses 0.8922 mg against a printed
  0.84 mg; the printed value needs about 0.2005 g/cm³ instead. The two
  printed statements about that one sphere do not use the same density,
  and only its areal density reproduces. No input was adjusted to reach
  the printed mass, and it anchors nothing.
- **The energy of a one-gram burn.** The nuclear masses give 337.5 GJ
  against a printed "nearly 400 GJ", about 19 % apart.

Boundaries:

- **No filed source pairs the two schemes.** The projectile belongs to
  the plane case; the paper that prints the convergent target prints no
  projectile for it. A test asserts the record's non-claims say so.
- **No shock is solved.** The four printed states are connected by
  relations and an equation of state this repository does not carry. The
  record takes the first and the fourth; a test asserts only that the
  printed chain rises monotonically.
- **No burn-up fraction exists anywhere here.** No filed source prints
  one and none is invented. What the record carries is the energy a
  complete burn of each inventory would release, which is an upper bound
  no target reaches.
- **The plate-to-fuel mass ratio is reported, not enforced.** The volume
  solves its own equation for that quantity and states in words that the
  plate must have sufficient mass; that equation is not carried here, so
  refusing on a threshold the volume never printed would be an
  invention.
- No value describes, approximates or validates any real machine or
  shot; an anchor reproduces a number a filed source prints and nothing
  further.

## Device 3D model

`src/scpn_icf_impact_core/geometry/model.py`. Tier G1: analytic surfaces
tessellated on the shared kernel library, in **two** models, because the
filed proceedings describe two schemes and pair neither with the other.
Design record: ADR 0006. Consumer contract:
`docs/DEVICE_3D_MODEL_CONTRACT.md`.

### What is built

| Scheme | Bodies | Frame origin |
|---|---|---|
| `plane` | `driver_plate`, `fuel_slab` | the impact face |
| `convergent` | `fuel_sphere` | the centre of the target |

Neither model contains the other's bodies, and no transformation between
the two frames exists anywhere in this repository. Within the plane
scheme the plate lies behind the impact face and the target ahead of it,
meeting at the origin, because the worked case's own figure places them
so and prints no standoff.

### What is anchored, recovered from the built bodies

Each of these is measured on the tessellated body, not read back out of
the declaration it was built from.

| Quantity | Built body gives | Printed | Status |
|---|---|---|---|
| cross-section, both plane bodies, both axes | 1.0 cm | 1 cm × 1 cm | exact |
| target fuel thickness | 1.0 cm | 1 cm | exact |
| plate thickness | 2.7659574e-3 cm | 2.7e-3 cm | **floor** (rounding gives 2.8e-3) |
| plate mass at the printed uranium density | 52.0 mg | — | returns the configuration's own plate mass |
| target fuel mass at the initial density | — | — | agrees with the level-0 record's `slab_fuel_mass_mg` |
| convergent target radius | 1.0e-3 m | 1 mm | exact |

### What is declared and said to be declared

- The **squareness** of the plate's face is printed; the level-0
  relations use only its area, so the shape enters in exactly one
  function and its docstring says so.
- The **plate thickness** is computed, never stored: it is obtained from
  the level-0 relations that own it, so a physics record and a geometry
  model built from one declaration cannot disagree.
- The **convergent scheme's polar axis** carries no physical meaning. No
  source prints a drive direction for that target; the axis is an
  artefact of building a body of revolution.

### Non-claims, each asserted by a test

- **The two schemes are never one machine.** No filed source pairs them,
  and they are two models with no common frame for that reason.
- **No projectile is drawn for the convergent scheme.** The paper that
  prints that target prints none, and no filed source in this family
  prints projectile geometry for any three-dimensional scheme.
- **No cone is drawn.** The volume's conical scheme is four hand-drawn
  schematics with no cone angle and no dimension of any kind.
- **No rigid wall, tamper, holder, standoff or enclosure is drawn.** The
  worked case names a rigid wall and dimensions none of them.
- **The convergent body is an inscribed polyhedron, not a sphere.** At
  the declared counts it is 10.17 % smaller than `4/3 π r³`, and a test
  measures that gap rather than leaving the caveat unexercised. The
  plane bodies carry no such caveat, because a prism is faceted exactly.
- **Only the convergent scheme has a resolution.** The plane model
  carries `None` for both counts, its builder takes neither argument,
  and a test asserts the absence on the signature itself.
- No body describes a target during a shot, and no value describes or
  validates any real machine or shot.

## Device CAD model

`src/scpn_icf_impact_core/geometry/cad.py`. Tier G2: the same bodies as
exact B-rep solids through the library's `cad` group, checked
fail-closed against their analytic closed forms and against their
tier-G1 twins, and exported as normalised STEP bytes with a digest. Two
schemes, two assemblies, two exports. Requires the optional `cad` extra.

**Every number below was measured on this family's own bodies against
the pinned library commit `4095aa8`.** No value was inherited from a
sibling family.

### The convergent scheme: two regimes, both located

| Quantity | Measured |
|---|---|
| ring counts that are exact | every count from 4 to 33 |
| first refusal | **34**, at a volume relative error of 9.80e-5 against a 1e-9 tolerance |
| above it | 34–54 alternate by parity; from 55 upward every count refuses |
| declared count | **33**, the top of the first regime |
| faceted volume relative deficit | 2.244500159e-04 |
| angular plateau | identical to every digit from 0.2 to 1.0 rad; falls below 0.2 |
| declared angular deflection | **0.3 rad**, inside the plateau |
| linear threshold | `deficit · r / 2` = **1.1222500795e-7 m** exactly |
| declared linear deflection | **2e-7 m**, at 0.5611 of its bound |

The refusal test asserts 34, the step immediately above the default; a
second test asserts that 35 builds, so the first refusal is not read as
a ceiling. The threshold was computed and then confirmed at both sides:
1.1223e-7 m passes at a ratio of 1.0000 and 1.1222e-7 m refuses.

**The angular deflection binds here and did not for the sibling beam
family**, whose bodies are larger. The declared value sits on the
plateau, where the deficit is at its maximum over the whole range, so
the bound established there holds for every finer setting too.

### The plane scheme: nothing to choose, and a two-sided tolerance

The back-end returns **8 vertices and 12 triangles** for each prism at
every linear deflection it accepts — 1e-7 to 1.0, seven orders — and at
every angular deflection from 0.01 to 1.0 rad. No deflection changes any
measure, so both declared values are mesher inputs and bound nothing,
and the record says so in its non-claims. Below 1e-8 m the mesher
refuses outright with a numeric error of its own, unrelated to any body
or bound; the declared 1e-6 m sits two orders above that floor.

**This family's two prisms deviate in opposite directions** — the plate
by `+2.99e-16` and the target by `−2.12e-16`, in one assembly. It is the
first consumer in the group whose own bodies show both signs, and it is
the concrete case that the library's earlier one-sided comparison would
have admitted at any magnitude. Both are far inside the declared `1e-12`
planar tolerance, and a test shows that tolerance still refuses a prism
wrong by one part in ten thousand.

### Two bounds that are not independent

Measured at 8, 16, 24 and 32 reference segments: the absolute margin
between the mesh difference and its bound is `2.2445e-4` at every one of
them — exactly the faceted volume deficit. The ratio looks tight at a
low segment count (0.9977 at eight) and raising the count tightens both
sides equally. A test states the identity so that nobody tightens the
wrong knob.

### A refusal the physics cannot make

The level-0 relations validate their inputs, not their results. A plate
mass of 1e-300 mg with a material density of 1e300 g/cm³ passes every
declaration and divides to exactly zero thickness. The library refuses
the degenerate prism and the geometry re-raises it under this package's
own error type; the handler is live code with a test behind it.

### Non-claims, each asserted by a test

- The plane scheme's deflections bound nothing, and the record says so.
- The convergent body is a polyhedron of revolution, never an ideal
  sphere; the frustum stack of its profile is its own analytic
  reference.
- Determinism of the STEP bytes is claimed within one pinned back-end
  environment only, never across back-end versions.
- Each record identifies only the declarations its scheme actually
  consumes — the plane scheme two, the convergent scheme none — and
  refuses to carry a digest for one it does not.
- No body is an engineering model, no fabrication tolerance is carried,
  and no value describes or validates any real machine or shot.
