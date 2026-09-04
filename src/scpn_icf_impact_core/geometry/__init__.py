# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — device geometry package

"""The two geometry tiers of the impact-driven ICF family.

**This package declares nothing.** Every dimension either lives in the
configuration — the plate's mass and velocity, the convergent target's
radius — or in a level-0 declaration the physics record already owns.
The one thing this package supplies that no other module needs is the
*shape* of the plate's printed face, and it is printed too: the worked
case states a square cross-section, and the level-0 relations use only
its area.

So this package is four builders, two per scheme, and the constants that
identify what they build. Design record: ADR 0006.
"""

from __future__ import annotations

from scpn_icf_impact_core.geometry.cad import (
    CAD_MODEL_NON_CLAIMS,
    CAD_MODEL_SCHEMA,
    CAD_MODEL_SCHEMA_VERSION,
    CAD_MODEL_UNITS_BY_SCHEME,
    DEFAULT_CONVERGENT_ANGULAR_DEFLECTION_RAD,
    DEFAULT_CONVERGENT_LINEAR_DEFLECTION_M,
    DEFAULT_CONVERGENT_RINGS,
    DEFAULT_CONVERGENT_SEGMENTS,
    DEFAULT_PLANE_ANGULAR_DEFLECTION_RAD,
    DEFAULT_PLANE_LINEAR_DEFLECTION_M,
    DeviceModelCAD,
    build_convergent_cad,
    build_plane_cad,
)
from scpn_icf_impact_core.geometry.model import (
    BODY_DRIVER_PLATE,
    BODY_FUEL_SLAB,
    BODY_FUEL_SPHERE,
    BODY_NAMES_BY_SCHEME,
    CENTIMETRE_M,
    CONVERGENT_BODY_NAMES,
    MATERIAL_FUEL_GAS,
    MATERIAL_SOLID_FUEL,
    MATERIAL_URANIUM_PLATE,
    MODEL_NON_CLAIMS,
    MODEL_SCHEMA,
    MODEL_SCHEMA_VERSION,
    MODEL_UNITS_BY_SCHEME,
    PLANE_BODY_NAMES,
    REFINABLE_SCHEMES,
    ROLE_DRIVER,
    ROLE_FUEL,
    SCHEME_CONVERGENT,
    SCHEME_PLANE,
    SCHEMES_BY_IDENTIFIER,
    SCHEMES_CONSUMING_DECLARATIONS,
    DeviceModel3D,
    build_convergent_model,
    build_plane_model,
    convergent_radius_m,
    plane_extents_m,
    square_side_cm,
)

__all__ = [
    "BODY_DRIVER_PLATE",
    "BODY_FUEL_SLAB",
    "BODY_FUEL_SPHERE",
    "BODY_NAMES_BY_SCHEME",
    "CAD_MODEL_NON_CLAIMS",
    "CAD_MODEL_SCHEMA",
    "CAD_MODEL_SCHEMA_VERSION",
    "CAD_MODEL_UNITS_BY_SCHEME",
    "CENTIMETRE_M",
    "CONVERGENT_BODY_NAMES",
    "DEFAULT_CONVERGENT_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_CONVERGENT_LINEAR_DEFLECTION_M",
    "DEFAULT_CONVERGENT_RINGS",
    "DEFAULT_CONVERGENT_SEGMENTS",
    "DEFAULT_PLANE_ANGULAR_DEFLECTION_RAD",
    "DEFAULT_PLANE_LINEAR_DEFLECTION_M",
    "MATERIAL_FUEL_GAS",
    "MATERIAL_SOLID_FUEL",
    "MATERIAL_URANIUM_PLATE",
    "MODEL_NON_CLAIMS",
    "MODEL_SCHEMA",
    "MODEL_SCHEMA_VERSION",
    "MODEL_UNITS_BY_SCHEME",
    "PLANE_BODY_NAMES",
    "REFINABLE_SCHEMES",
    "ROLE_DRIVER",
    "ROLE_FUEL",
    "SCHEMES_BY_IDENTIFIER",
    "SCHEMES_CONSUMING_DECLARATIONS",
    "SCHEME_CONVERGENT",
    "SCHEME_PLANE",
    "DeviceModel3D",
    "DeviceModelCAD",
    "build_convergent_cad",
    "build_convergent_model",
    "build_plane_cad",
    "build_plane_model",
    "convergent_radius_m",
    "plane_extents_m",
    "square_side_cm",
]
