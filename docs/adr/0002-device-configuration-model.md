<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Impact Core — ADR 0002: device configuration model
-->

# ADR 0002 — Device configuration model and evidence-maturity semantics

**Status:** accepted (2026-08-31)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The repository was established architecture-only (ADR 0001). The first
capability lane is the device configuration model for the single
registry configuration this repository owns
(`projectile_or_impact_icf`). The claim boundary and repository-level
`evidence_maturity` semantics follow the family pilot.

## Decision

1. The package `scpn_icf_impact_core` implements the device
   configuration model as frozen, strictly typed value objects: the
   projectile (mass, velocity) and the target declaration.
2. Claim boundary — identical to the family pilot: internal-consistency
   validation, cited textbook estimates with documented bounds,
   canonical serialisation with SHA-256 digest, and the data-only SPO
   registry pin. No claim about any real machine; every exercised
   parameter set is a synthetic test fixture.
3. Derived quantities from standard mechanics: the projectile kinetic
   energy ``E = m v^2 / 2`` and the specific kinetic energy
   ``e = v^2 / 2``.
4. Advisory finding, reported by `consistency_report()` and never
   clamped: a projectile velocity below a declared ``100 km/s`` floor.
   The filed Proceedings of the Impact Fusion Workshop, Los Alamos
   report LA-8000-C (1979), print a minimum projectile velocity of
   200 km/s (PDF p. 3) and 130 km/s for three-dimensional compression
   at a gain above 100 (PDF p. 4); the declared floor lies below both.
5. Repository-level `evidence_maturity` = the highest state claimed by
   any capability entry; per-capability states are the authoritative
   claim surface.
6. Everything else is unchanged: review-only/non-actionable SPO
   profile, no adapter implementation, empty solver seams,
   `not_federated` Studio state, independent machine-protection veto,
   all non-claims.

## Consequences

- The Studio descriptor's `capabilities` array carries its first item
  (schema 1.1.0 data change only).
- The reactor-domain validator gains the populated-capabilities branch
  with the ceiling rule.
- Later lanes (launcher/tracking/burn diagnostic semantics with dual
  clock identities, safety envelope) build on these types; maturity
  advances per capability only with the evidence the family standard
  requires.

## Amendment 2026-10-31

The ``~100 km/s`` floor was described as the scale that impact-fusion
studies identify as the entry regime, credited to LA-8000-C. The filed
proceedings print a minimum projectile velocity of 200 km/s (PDF p. 3)
and 130 km/s for three-dimensional compression (PDF p. 4), not 100 km/s.
The floor is now named declared, with those values quoted. Whether the
floor should move to a printed value is a separate decision; no value or
check changed here.
