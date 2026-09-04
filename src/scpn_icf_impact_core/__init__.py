# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — device capability package

"""Device capability models of the SCPN impact-ICF device family.

Public surface of the ``device_configuration_model``,
``diagnostic_clock_semantics``, ``level0_device_physics``,
``device_3d_model`` and ``device_cad_model`` capabilities at
``computational_prototype`` maturity: validated parameter objects,
synthetic diagnostic and clock declarations aligned with the pinned SPO
observability catalogue, what a flying plate carries onto the target it
strikes and where the fuel of each published target geometry ends up
when it is compressed, the tessellated and B-rep models of **both**
published schemes on the shared kernel library, documented consistency
estimates, canonical serialisation with SHA-256 digests, and data-only
pins to the SPO registries. The two schemes come from two papers of one
proceedings and no filed source pairs them, so they are carried side by
side and never as one machine. No claim about any real machine or
diagnostic is made anywhere in this package.
"""

from __future__ import annotations

from typing import Final

from scpn_icf_impact_core.configuration import (
    IMPACT_VELOCITY_FLOOR_KM_S,
    OWNED_CONFIGURATIONS,
    ConsistencyFinding,
    DeviceConfiguration,
    RegistryBinding,
    configuration_from_bytes,
    configuration_from_record,
)
from scpn_icf_impact_core.errors import (
    DeviceConfigurationError,
    DeviceGeometryError,
    DiagnosticPlanError,
)
from scpn_icf_impact_core.geometry import (
    BODY_DRIVER_PLATE,
    BODY_FUEL_SLAB,
    BODY_FUEL_SPHERE,
    BODY_NAMES_BY_SCHEME,
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    SCHEME_CONVERGENT,
    SCHEME_PLANE,
    SCHEMES_BY_IDENTIFIER,
    DeviceModel3D,
    DeviceModelCAD,
    build_convergent_cad,
    build_convergent_model,
    build_plane_cad,
    build_plane_model,
)
from scpn_icf_impact_core.observability import (
    APPLICABLE_CANDIDATES,
    CATALOGUE_BINDING,
    CandidateProfile,
    ClockKind,
    ClockModel,
    ClockRelation,
    DeferredCandidate,
    DiagnosticChannelPlan,
    DiagnosticPlan,
    FrameKind,
    ObservabilityBinding,
    ObservabilityClass,
    ReferenceFrame,
    SemanticCarrier,
    plan_from_bytes,
    plan_from_record,
)
from scpn_icf_impact_core.parameters import Projectile, TargetDeclaration
from scpn_icf_impact_core.physics import (
    LEVEL0_NON_CLAIMS,
    LEVEL0_SCHEMA,
    LEVEL0_SCHEMA_VERSION,
    FuelDeclaration,
    Level0Physics,
    OperatingPoint,
    ProjectileDeclaration,
    SchemeDeclaration,
    compression_ratio,
    dt_specific_energy_j_per_g,
    full_burn_energy_mj,
    level0_physics,
    planar_compressed_thickness_cm,
    spherical_density_ratio,
    target_radius_cm,
)
from scpn_icf_impact_core.plan_envelope import (
    PlanEnvelope,
    envelope_for_plan,
    envelope_from_bytes,
    envelope_from_record,
    verify_envelope,
)

__version__: Final = "0.1.0.dev0"

__all__ = [
    "APPLICABLE_CANDIDATES",
    "BODY_DRIVER_PLATE",
    "BODY_FUEL_SLAB",
    "BODY_FUEL_SPHERE",
    "BODY_NAMES_BY_SCHEME",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CATALOGUE_BINDING",
    "IMPACT_VELOCITY_FLOOR_KM_S",
    "LEVEL0_NON_CLAIMS",
    "LEVEL0_SCHEMA",
    "LEVEL0_SCHEMA_VERSION",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "OWNED_CONFIGURATIONS",
    "SCHEMES_BY_IDENTIFIER",
    "SCHEME_CONVERGENT",
    "SCHEME_PLANE",
    "CandidateProfile",
    "ClockKind",
    "ClockModel",
    "ClockRelation",
    "ConsistencyFinding",
    "DeferredCandidate",
    "DeviceConfiguration",
    "DeviceConfigurationError",
    "DeviceGeometryError",
    "DeviceModel3D",
    "DeviceModelCAD",
    "DiagnosticChannelPlan",
    "DiagnosticPlan",
    "DiagnosticPlanError",
    "FrameKind",
    "FuelDeclaration",
    "Level0Physics",
    "ObservabilityBinding",
    "ObservabilityClass",
    "OperatingPoint",
    "PlanEnvelope",
    "Projectile",
    "ProjectileDeclaration",
    "ReferenceFrame",
    "RegistryBinding",
    "SchemeDeclaration",
    "SemanticCarrier",
    "TargetDeclaration",
    "__version__",
    "build_convergent_cad",
    "build_convergent_model",
    "build_plane_cad",
    "build_plane_model",
    "compression_ratio",
    "configuration_from_bytes",
    "configuration_from_record",
    "dt_specific_energy_j_per_g",
    "envelope_for_plan",
    "envelope_from_bytes",
    "envelope_from_record",
    "full_burn_energy_mj",
    "level0_physics",
    "plan_from_bytes",
    "plan_from_record",
    "planar_compressed_thickness_cm",
    "spherical_density_ratio",
    "target_radius_cm",
    "verify_envelope",
]
