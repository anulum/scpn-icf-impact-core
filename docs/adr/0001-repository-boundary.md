<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Impact Core — ADR 0001: repository boundary
-->

# ADR 0001 — Repository boundary and ownership

**Status:** accepted (2026-08-30)

**Deciders:** project owner; SCPN Reactor Systems Research Group standard

## Context

The SCPN reactor portfolio assigns every built-in configuration of the SCPN
Phase Orchestrator reactor registry (version `1.0.0`, 32 configurations) to
exactly one device-family repository. Impact-driven fusion borders the
other inertial owners (shared implosion endpoint) and the liner-MIF owner
(macroscopic-driver heritage); a boundary decision was needed on both
edges.

## Decision

1. `SCPN-ICF-IMPACT-CORE` owns exactly one registry configuration:
   `projectile_or_impact_icf` (impact-driven target).
2. The repository owns device-level truth only: launcher and projectile
   configuration policy (launcher classes, projectile integrity and
   metrology contracts), shot lifecycle semantics with in-flight tracking
   and impact-timing declarations, diagnostic and clock declarations,
   actuator-response model boundaries, the safety-envelope declaration,
   and the device-owned CONTROL adapter specification.
3. Solver mathematics remains in `SCPN-FUSION-CORE` until an exact surface
   passes the family migration gate. No solver code is copied here.
4. Typed semantics remain in `SCPN-PHASE-ORCHESTRATOR` (review-only).
   Admission and `ControlAction` formation remain exclusively in
   `SCPN-CONTROL`. Machine protection remains independent with the final
   veto. Presentation remains in `SCPN-STUDIO`; this project is
   `not_federated`.
5. The repository starts, and remains until evidenced otherwise, at
   `architecture_only` with empty capability and claim inventories.

## Alternatives considered

- **Folding impact ICF into a combined inertial repository** (shared
  implosion endpoint): rejected — the kinetic driver surface (launcher
  physics, projectile integrity, in-flight tracking, impact conversion)
  shares nothing with laser optics or accelerator transport; lifecycle
  and hazards differ accordingly (surfaces 2–4).
- **Grouping with mechanical/liquid liner MIF** (macroscopic drivers):
  rejected — liner MIF compresses a preformed magnetised plasma on slower
  timescales; impact ICF is unmagnetised inertial compression by a free
  projectile; the portfolio map separates the owners.
- **Absorbing solver code at scaffold time**: rejected — violates the
  migration gate.

## Consequences

- Downstream consumers get one stable identity for the impact-ICF
  configuration and a manifest to bind against.
- The validator fails on any capability or claim entry while maturity is
  `architecture_only`.
- Boundary changes require a portfolio-level map change first; a future
  ADR records any such change here.
