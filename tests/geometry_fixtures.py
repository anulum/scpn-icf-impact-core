# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — device geometry anchors

"""Anchors shared by the two geometry tiers' tests.

Reproducing a printed value is an anchor, never a claim about that
machine.

**One printed value is new here and the rest are imported.** Every
dimension these tiers build from is already anchored by the level-0
record and lives in :mod:`physics_fixtures`; this module converts them
once, because a second copy would be a second place for them to drift.
The exception is the *side* of the plate's printed square face. The
level-0 relations need only its area and so the declaration carries only
the area, but a body needs two sides — and the worked case prints them,
so the side is an anchor here rather than a declaration.

**The plane scheme has no resolution and the convergent scheme's was
measured on this family's own body.** The counts below are not the
sibling families' and the sibling families' are not transferable; the
measurement is recorded in ADR 0006.
"""

from __future__ import annotations

from typing import Final

from physics_fixtures import (
    DERIVED_CHRISTIANSEN_PLATE_MASS_MG,
    PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3,
    PRINTED_CHRISTIANSEN_DENSITY_RATIOS,
    PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2,
    PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM,
    PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM,
    PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3,
    PRINTED_MARSHALL_SPHERE_RADIUS_UM,
    anchor_configuration,
    anchor_fuel,
    anchor_projectile,
    anchor_scheme,
    two_significant_figure_floor,
)
from scpn_icf_impact_core.geometry import CENTIMETRE_M
from scpn_icf_impact_core.physics.level0 import MICROMETRES_PER_CENTIMETRE

# --- Printed by the worked plane case, and needed only by geometry ---
#: Side of the plate's square cross-section, in centimetres. Christiansen,
#: printed p. 33 / PDF p. 46: a "1 cm x 1 cm" cross-section, stated to be
#: sufficient for edge losses to be negligible. The level-0 relations use
#: the area alone, so this is the one printed quantity the tiers add.
PRINTED_CHRISTIANSEN_CROSS_SECTION_SIDE_CM: Final = 1.0

# --- Tessellation resolutions, measured on this family's own bodies ---
#: Circumferential segments of the convergent scheme's reference mesh.
ANCHOR_SEGMENTS: Final = 8
#: Polar steps of the convergent scheme's profile: the top of the regime
#: in which every count is exact on this family's 1 mm target, found by
#: scanning every count from 4 to 80 rather than sampling.
ANCHOR_RINGS: Final = 33
#: The step immediately above it, which the back-end refuses. A refusal
#: test set comfortably above a boundary passes forever while locating
#: nothing, so this is the nearest failing case and not a safe one.
FIRST_REFUSED_RINGS: Final = 34
#: The next count above that, which is exact again: the band from 34 to
#: 54 alternates, and recording the alternation stops a reader from
#: reading the refusal as a ceiling.
NEXT_EXACT_RINGS: Final = 35

#: Angular deflections at which the convergent body's faceted volume
#: deficit is identical to every digit. The declared value sits inside
#: this plateau, where the deficit is at its maximum over the whole
#: range and does not depend on the exact value chosen.
PLATEAU_ANGULAR_DEFLECTIONS_RAD: Final = (1.0, 0.7, 0.5, 0.4, 0.3, 0.2)
#: An angular deflection below the plateau, where the deficit falls.
BELOW_PLATEAU_ANGULAR_DEFLECTION_RAD: Final = 0.05

#: Faceted volume relative deficit of the convergent body at the
#: declared counts and anywhere on the angular plateau.
MEASURED_CONVERGENT_DEFICIT: Final = 2.244500159e-04
#: Smallest linear deflection the convergent body clears, which is
#: ``deficit * radius / 2`` exactly and was computed rather than
#: searched for.
MEASURED_CONVERGENT_THRESHOLD_M: Final = 1.1222500795e-07
#: A linear deflection just above the threshold, which is accepted.
LINEAR_DEFLECTION_ABOVE_THRESHOLD_M: Final = 1.1223e-07
#: A linear deflection just below it, which is refused.
LINEAR_DEFLECTION_BELOW_THRESHOLD_M: Final = 1.1222e-07

#: Linear deflections at which both prisms are faceted identically. The
#: back-end refuses anything below 1e-7 at this family's scale, with a
#: numeric error of its own rather than a refusal from any bound.
PLANAR_ACCEPTED_LINEAR_DEFLECTIONS_M: Final = (1.0, 1.0e-2, 1.0e-4, 1.0e-6, 1.0e-7)
#: Angular deflections at which the same holds.
PLANAR_ACCEPTED_ANGULAR_DEFLECTIONS_RAD: Final = (1.0, 0.5, 0.1, 0.01)
#: Vertices and triangles the back-end returns for a prism, at every one
#: of those values.
PLANAR_FACET_COUNTS: Final = (8, 12)

# --- Derived from the printed values above, never typed ---
ANCHOR_CROSS_SECTION_SIDE_M: Final = (
    PRINTED_CHRISTIANSEN_CROSS_SECTION_SIDE_CM * CENTIMETRE_M
)
ANCHOR_SLAB_THICKNESS_M: Final = PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM * CENTIMETRE_M
ANCHOR_SPHERE_RADIUS_M: Final = (
    PRINTED_MARSHALL_SPHERE_RADIUS_UM / MICROMETRES_PER_CENTIMETRE * CENTIMETRE_M
)

__all__ = [
    "ANCHOR_CROSS_SECTION_SIDE_M",
    "ANCHOR_RINGS",
    "ANCHOR_SEGMENTS",
    "ANCHOR_SLAB_THICKNESS_M",
    "ANCHOR_SPHERE_RADIUS_M",
    "BELOW_PLATEAU_ANGULAR_DEFLECTION_RAD",
    "DERIVED_CHRISTIANSEN_PLATE_MASS_MG",
    "FIRST_REFUSED_RINGS",
    "LINEAR_DEFLECTION_ABOVE_THRESHOLD_M",
    "LINEAR_DEFLECTION_BELOW_THRESHOLD_M",
    "MEASURED_CONVERGENT_DEFICIT",
    "MEASURED_CONVERGENT_THRESHOLD_M",
    "NEXT_EXACT_RINGS",
    "PLANAR_ACCEPTED_ANGULAR_DEFLECTIONS_RAD",
    "PLANAR_ACCEPTED_LINEAR_DEFLECTIONS_M",
    "PLANAR_FACET_COUNTS",
    "PLATEAU_ANGULAR_DEFLECTIONS_RAD",
    "PRINTED_CHRISTIANSEN_CROSS_SECTION_SIDE_CM",
    "PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3",
    "PRINTED_CHRISTIANSEN_DENSITY_RATIOS",
    "PRINTED_CHRISTIANSEN_IMPACT_AREA_CM2",
    "PRINTED_CHRISTIANSEN_PLATE_THICKNESS_CM",
    "PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM",
    "PRINTED_CHRISTIANSEN_URANIUM_DENSITY_G_CM3",
    "PRINTED_MARSHALL_SPHERE_RADIUS_UM",
    "anchor_configuration",
    "anchor_fuel",
    "anchor_projectile",
    "anchor_scheme",
    "two_significant_figure_floor",
]
