<!--
SPDX-License-Identifier: AGPL-3.0-or-later
Commercial license available
© Concepts 1996–2026 Miroslav Šotek. All rights reserved.
© Code 2020–2026 Miroslav Šotek. All rights reserved.
ORCID: 0009-0009-3560-0851
Contact: www.anulum.li | protoscience@anulum.li
SCPN ICF Impact Core — CHANGELOG
-->

# Changelog

## [Unreleased]

### Added

- Device 3D and CAD models (`device_3d_model`, `device_cad_model`,
  `computational_prototype`, ADR 0006): tier-G1 tessellated and tier-G2
  B-rep models of **both** target schemes the cited proceedings
  describe, built on the shared kernel library. The two schemes are two
  models in two frames with no transformation between them, because no
  filed source pairs them; the plane scheme draws a driver plate and a
  fuel slab, the convergent scheme a fuel sphere, and neither a cone nor
  a projectile for the convergent target is drawn because nothing
  dimensions either. Every resolution was measured on this family's own
  bodies rather than inherited: the ring regime was scanned count by
  count, the first refusal is asserted at the step immediately above the
  default, and the linear deflection threshold is computed exactly and
  confirmed on both sides. The plane scheme carries no resolution at
  all, because a prism is faceted exactly at every deflection the
  back-end accepts, and its builders take no such argument. Consumer
  contract: `docs/DEVICE_3D_MODEL_CONTRACT.md`.
- Dependency on the shared kernel library `scpn-reactor-kernels`, pinned
  by commit in the project metadata, in `reactor-domain.json` with the
  kernel inventory digest, and in a repository contract test that holds
  all three to one commit. Tier G2 is behind an optional `cad` extra
  naming the same commit.

- Level-0 device physics (`level0_device_physics`,
  `computational_prototype`, ADR 0005): what a flying plate carries onto
  the target it strikes, what the fuel is in a plane slab and in a
  converging sphere, and where that fuel ends up when it is compressed.
  Anchored on the freely published workshop proceedings the repository
  cites, whose two geometry papers describe **two different schemes**;
  the record evaluates each on what its own paper prints and its
  non-claims state that no filed source pairs them. Nothing here solves
  a shock, and no burn-up fraction is invented: the record carries the
  energy a complete burn of each inventory would release, which is an
  upper bound and is named one. Two printed values are recorded as not
  reproduced rather than absorbed — the convergent target's mass, whose
  two printed statements do not use the same density, and the energy of
  a one-gram burn.

- Diagnostic-plan depth: per-channel signal inventories, frame
  transformations with a fixed kind-admissibility table and connectivity
  rule, and a clock topology partitioning the physical clocks into rooted
  domains with a star of relations to the reference root. Envelope
  `scpn.reactor-diagnostic-plan-envelope.v1` bumped to `1.2.0`; the
  fixture is regenerated from the public surface and re-pinned. All new
  members are declarations: no observation, phase, mapping, or control
  authority is created.
- Local gate parity with the wider ecosystem: the pre-commit chain now
  also runs REUSE licensing compliance and a typographical checker
  (`_typos.toml` carries the deliberate reactor vocabulary), and adds
  the upstream YAML, TOML, large-file and private-key guards. Licensing
  and spelling were previously verified only in hosted CI, so a broken
  REUSE annotation — including the aggregate annotation that covers the
  binary header images — could reach a push before being caught.
- Generated repository header artwork: `docs/assets/generate_header.py`
  renders three deterministic 1280x640 images from the repository's own
  domain surface (the launcher-projectile-target view used by the
  README, the velocity entry gate, and the momentum chain).
- Modular hosted-workflow surface per the ecosystem workflow-modularity
  standard: `ci.yml` reduced to a coordinator with a stable fail-closed
  `gate` job, single-responsibility reusable workflows for static
  analysis/repository policy and for tests, a versioned machine-readable
  inventory (`.github/workflow-inventory.json`,
  `scpn.workflow-inventory.v1` `1.0.0`), and a fail-closed modularity
  guard (`tools/audit_workflows.py`) enforced locally (preflight gate,
  pre-commit hook) and in hosted CI. The duplicate documentation-links
  step was removed from the CI chain; `docs.yml` remains the single
  owner of documentation validation.

- Typed reference frames, clock synchronisation relations (synthetic
  bounds only; no correlation evidence claimed), and per-channel
  acquisition windows and element counts in the diagnostic model;
  hardened decoders (recursive exact-key, duplicate-member, and
  byte-canonical refusal in both codecs); envelope `1.1.0` adding
  `manifest_sha256` over the committed canonical `reactor-domain.json`
  (fixture regenerated; byte hash re-pinned in tests).

- Portable diagnostic-plan envelope
  (`src/scpn_icf_impact_core/plan_envelope.py`,
  `scpn.reactor-diagnostic-plan-envelope.v1` version `1.0.0`): a
  producer-owned, canonically serialised wrapper carrying project
  identity, exact owned configurations, capability and maturity,
  synthetic/review-only/non-actuating statements, both SPO registry
  pins, the inner plan's SHA-256, the producer revision, and fixed
  no-observation/no-control non-claims; strict parsers refuse unknown,
  duplicate, and non-finite members, and an immutable committed fixture
  exercises the exchange end to end.

- Diagnostic and clock semantics model
  (`src/scpn_icf_impact_core/observability.py`), the second implemented
  capability at `computational_prototype`: frozen clock, channel,
  deferral, and plan objects aligned fail-closed with the pinned SPO
  observability-profile catalogue (candidate applicability, carrier
  admissibility, exact class-fixed evidence vocabularies, clock-kind
  compatibility, Nyquist and event-timing bounds); cited advisory band
  and timing checks; canonical serialisation with SHA-256 digests and
  strict NaN-rejecting round-trip parsing (design record
  `docs/adr/0003-diagnostic-clock-semantics.md`).

- Device configuration model (`src/scpn_icf_impact_core/`), the first implemented
  capability at `computational_prototype`: validated frozen parameter
  objects with device-specific invariants and documented, cited
  consistency estimates; canonical serialisation with SHA-256 digests
  and strict NaN-rejecting round-trip parsing; a data-only pin to the
  SPO reactor registry; and the reactor-domain validator branch
  enforcing populated capability inventories with the ADR 0002
  evidence-maturity ceiling rule (design record
  `docs/adr/0002-device-configuration-model.md`).

- Architecture-only repository scaffold: governance, security, licensing,
  REUSE metadata, contribution and support policies, and citation metadata.
- Machine-readable domain manifest `reactor-domain.json` binding the project
  to SCPN Phase Orchestrator reactor registry `1.0.0`
  (configuration `projectile_or_impact_icf`).
- Device-owned CONTROL adapter specification and threat model.
- Derived Studio portfolio descriptor (`not_federated`) and generated
  capability inventory (zero implemented capabilities).
- Validation tooling: domain-manifest validator, descriptor derivation and
  inventory generation with drift checks, and a fail-closed preflight
  orchestrator, each with statement- and branch-complete tests.
- Continuous-integration, code-scanning, security-audit, documentation,
  SBOM, pre-commit, and Scorecard workflow definitions (read-only
  permissions; no publication or deployment workflows).

### Changed

- Studio portfolio descriptor schema ratified at version 1.1.0 after
  downstream review, before any consumer adoption (1.0.0 superseded
  unconsumed): canonical JSON Schema published in-repository with a strict
  unknown-field policy, explicit source repository, nullable lifecycle
  evidence pointer, nullable versioned control-intent reference, ratified
  capability item shape, and a machine-protection object (independent
  final-veto owner with availability `not_assessed`) replacing the former
  boolean flag.
