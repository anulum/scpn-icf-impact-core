<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Impact Core — Architecture
-->

# Architecture

## Purpose and evidence state

`SCPN-ICF-IMPACT-CORE` is the device-family owner for projectile- and
impact-driven inertial confinement fusion systems in the SCPN Reactor
Systems Research Group portfolio. The
repository owns two implemented capabilities at
`computational_prototype` in `src/scpn_icf_impact_core/`: the device
configuration model (design record ADR 0002, evidence record
`VALIDATION.md#device-configuration-model`) and the diagnostic and
clock semantics model (design record ADR 0003, evidence record
`VALIDATION.md#diagnostic-and-clock-semantics`). Every other
section below describes boundaries and contracts. The claim inventory is
empty; capability and claim inventories are generated and drift-checked.

## The five-surface boundary

1. **Governing confinement physics** — the `projectile_or_impact_icf`
   configuration (impact-driven target, `inertial` registry family):
   inertial compression and heating of a fuel-bearing target by the
   impact of a macroscopic projectile at hypervelocity. The driver-side
   physics is kinetic — projectile integrity under acceleration, impact
   shock generation, and the conversion of kinetic energy into target
   compression — distinct from both radiation/ablation coupling (laser
   ICF) and charged-particle deposition (beam ICF). Liner-on-magnetised-
   plasma compression belongs to the magneto-inertial owners.
2. **Primary driver and energy delivery** — hypervelocity launchers as a
   declared class space (electromagnetic railgun/coilgun launchers,
   staged light-gas guns, or gradient-field accelerators), with projectile
   design and integrity contracts as first-class configuration facets.
3. **Plant and shot lifecycle** — discrete shot lifecycle: projectile and
   target metrology acceptance, launcher preparation and charge, launch
   and in-flight tracking, impact and burn window, and post-shot
   recovery. Device-level hazard semantics cover projectile break-up,
   trajectory deviation, launcher erosion, and chamber debris loading.
4. **Diagnostic, reference-frame, and clock model** — launcher-axis and
   target-chamber coordinate conventions, in-flight velocimetry and
   tracking channels, impact-timing anchors, burn diagnostics (yield,
   bang time), and microsecond-flight/nanosecond-burn clock identities
   declared separately.
5. **Solver, evidence, and control-contract boundary** — versioned seams
   towards `SCPN-FUSION-CORE`, review-only semantics towards
   `SCPN-PHASE-ORCHESTRATOR`, and the device-owned CONTROL adapter
   specification towards `SCPN-CONTROL`.

## Position in the SCPN ecosystem

```text
SCPN-ICF-IMPACT-CORE (device truth: launcher/projectile policy, shot
                      lifecycle, tracking/burn diagnostics, safety
                      envelope, adapter spec)
   │  optional versioned solver seams (none active)
   ├──────────────► SCPN-FUSION-CORE      (solver mathematics, evidence)
   │  typed review-only semantics
   ├──────────────► SCPN-PHASE-ORCHESTRATOR (semantics, comparability)
   │  device-owned adapter (specification only; no implementation)
   ├──────────────► SCPN-CONTROL          (admission; sole ControlAction author)
   │  derived portfolio descriptor (not_federated)
   └──────────────► SCPN-STUDIO           (catalogue, evidence UI, gating)

SCPN-CONTROL ──admitted ControlAction──► independent machine protection
                                          (final veto) ─► plant actuators
```

## Repository layout

| Path | Role |
|---|---|
| `reactor-domain.json` | portable source of project identity and contracts |
| `studio/portfolio-descriptor.json` | derived Studio descriptor, `not_federated` |
| `capability-inventory.json` | generated, truthfully empty inventory |
| `docs/CONTROL_ADAPTER_SPECIFICATION.md` | device-owned adapter contract |
| `docs/THREAT_MODEL.md` | assets, trust boundaries, misuse paths |
| `docs/adr/0001-repository-boundary.md` | boundary decision record |
| `tools/` | validators, derivation tools, preflight orchestrator |
| `tests/` | statement- and branch-complete tests for `tools/` |
| `.github/workflows/` | read-only CI definitions (no publication) |

## Contract surfaces and versioning

- `reactor-domain.json` follows schema `scpn.reactor-domain.v1`; unknown
  schemas are rejected by consumers.
- The Studio descriptor is derived deterministically and embeds the
  manifest's SHA-256; manual edits are detected as drift.
- The CONTROL adapter contract is specification-only at `0.1.0-spec`.
- SPO binding is fixed to reactor registry `1.0.0`, digest
  `786d9542ce76c56dd7748fa948b17efed6c073525e527ce90e6d5e29a2d00090`.

## What would change this architecture

Acceptance of a FUSION solver seam through the family migration gate,
ratification of an SPO `ControlIntent`-class contract, or Studio federation
after a real capability passes producer and consumer gates — each recorded
as a versioned contract change in a new ADR.
