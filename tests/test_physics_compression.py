# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — tests for where the fuel ends up

"""Where the fuel ends up, in each of the two printed geometries."""

from __future__ import annotations

import math

import pytest

from physics_fixtures import (
    PRINTED_CHRISTIANSEN_COMPRESSED_THICKNESS_CM,
    PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3,
    PRINTED_CHRISTIANSEN_DENSITY_RATIOS,
    PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM,
    PRINTED_MARSHALL_RADIAL_COMPRESSION_FACTOR,
    two_significant_figure_floor,
)
from scpn_icf_impact_core.errors import DeviceConfigurationError
from scpn_icf_impact_core.physics.compression import (
    compression_ratio,
    planar_compressed_thickness_cm,
    require_compression_factor,
    spherical_compressed_radius_cm,
    spherical_density_ratio,
)
from scpn_icf_impact_core.physics.fuel import (
    density_from_ratio_g_cm3,
    slab_areal_density_g_cm2,
    sphere_areal_density_g_cm2,
)

INITIAL_RATIO = PRINTED_CHRISTIANSEN_DENSITY_RATIOS[0]
COMPRESSED_RATIO = PRINTED_CHRISTIANSEN_DENSITY_RATIOS[3]


def test_the_printed_states_compress_the_fuel_by_four_hundred_and_twenty() -> None:
    """The two printed end states set the compression exactly."""
    assert compression_ratio(INITIAL_RATIO, COMPRESSED_RATIO) == pytest.approx(
        420.0, rel=1e-13
    )


def test_the_compression_ratio_does_not_depend_on_the_reference() -> None:
    """Both states are quoted against one reference, which cancels.

    Scaling the reference is what a different fuel or a different
    convention would do, and the answer must not move.
    """
    plain = compression_ratio(INITIAL_RATIO, COMPRESSED_RATIO)
    scaled = compression_ratio(INITIAL_RATIO * 7.0, COMPRESSED_RATIO * 7.0)
    assert scaled == pytest.approx(plain, rel=1e-15)


def test_the_printed_compressed_thickness_is_a_truncation_not_a_rounding() -> None:
    """The volume truncates the compressed thickness too.

    Measured: mass conservation gives 2.3810e-3 cm, the volume prints
    2.3e-3, and rounding would have given 2.4e-3. This is the second
    independent value on which the volume truncates, which is what makes
    the truncation a convention rather than a coincidence.
    """
    compressed = planar_compressed_thickness_cm(
        PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM, INITIAL_RATIO, COMPRESSED_RATIO
    )
    assert compressed == pytest.approx(2.3809524e-3, rel=1e-7)
    assert two_significant_figure_floor(compressed, -3) == pytest.approx(
        PRINTED_CHRISTIANSEN_COMPRESSED_THICKNESS_CM, rel=1e-15
    )
    rounded = round(compressed * 1.0e3, 1) * 1.0e-3
    assert rounded != pytest.approx(
        PRINTED_CHRISTIANSEN_COMPRESSED_THICKNESS_CM, rel=1e-9
    )
    assert rounded == pytest.approx(2.4e-3, rel=1e-9)


def test_a_driven_slab_gains_no_areal_density_at_all() -> None:
    """One-axis compression leaves the areal density where it was.

    This is the whole of the convergent paper's objection to the plane
    scheme, stated as arithmetic: the density rises by exactly the
    factor the thickness falls by, so their product does not move.
    Measured as a bound rather than an equality, because the two routes
    to it differ in the last place of a double.
    """
    initial_density = density_from_ratio_g_cm3(
        INITIAL_RATIO, PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3
    )
    compressed_density = density_from_ratio_g_cm3(
        COMPRESSED_RATIO, PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3
    )
    compressed_thickness = planar_compressed_thickness_cm(
        PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM, INITIAL_RATIO, COMPRESSED_RATIO
    )
    before = slab_areal_density_g_cm2(
        PRINTED_CHRISTIANSEN_SLAB_THICKNESS_CM, initial_density
    )
    after = slab_areal_density_g_cm2(compressed_thickness, compressed_density)
    assert after == pytest.approx(before, rel=1e-15)


def test_a_converging_sphere_gains_the_square_of_its_radial_factor() -> None:
    """A sphere gains areal density where a slab gains none.

    The density rises as the cube of the radial factor and the radius
    falls as its first power, so the product rises as the square. At the
    printed factor of ten that is a hundredfold, and it is why the
    convergent paper reaches an ignition-scale areal density from a
    milligram of fuel.
    """
    factor = PRINTED_MARSHALL_RADIAL_COMPRESSION_FACTOR
    radius = 0.1
    density = PRINTED_CHRISTIANSEN_CRYOGENIC_DENSITY_G_CM3
    before = sphere_areal_density_g_cm2(radius, density)
    after = sphere_areal_density_g_cm2(
        spherical_compressed_radius_cm(radius, factor),
        density_from_ratio_g_cm3(spherical_density_ratio(factor), density),
    )
    assert after == pytest.approx(before * factor**2, rel=1e-13)
    assert after / before == pytest.approx(100.0, rel=1e-13)


def test_the_printed_radial_factor_raises_the_density_a_thousandfold() -> None:
    """The density factor is the cube of the radial one."""
    assert spherical_density_ratio(
        PRINTED_MARSHALL_RADIAL_COMPRESSION_FACTOR
    ) == pytest.approx(1000.0, rel=1e-15)
    assert spherical_density_ratio(2.0) == pytest.approx(8.0, rel=1e-15)


def test_the_printed_sphere_compresses_to_a_tenth_of_its_radius() -> None:
    """The compressed radius is the declared one over the factor."""
    assert spherical_compressed_radius_cm(
        0.1, PRINTED_MARSHALL_RADIAL_COMPRESSION_FACTOR
    ) == pytest.approx(0.01, rel=1e-15)


@pytest.mark.parametrize("value", [1.0000001, 10.0, 1.0e6])
def test_a_factor_above_one_is_accepted(value: float) -> None:
    """A factor that actually compresses passes through unchanged."""
    assert require_compression_factor("radial_compression_factor", value) == value


@pytest.mark.parametrize("value", [1.0, 0.5])
def test_a_factor_that_does_not_compress_is_refused(value: float) -> None:
    """A factor of one leaves the target alone and below one expands it."""
    with pytest.raises(DeviceConfigurationError, match=r"must exceed 1\.0"):
        require_compression_factor("radial_compression_factor", value)


@pytest.mark.parametrize("value", [0.0, -2.0, math.nan])
def test_a_factor_that_is_not_a_positive_number_is_refused(value: float) -> None:
    """Positivity and finiteness are checked before the compression test."""
    with pytest.raises(
        DeviceConfigurationError, match=r"strictly positive|must be finite"
    ):
        require_compression_factor("radial_compression_factor", value)


@pytest.mark.parametrize("compressed", [0.01, 0.005])
def test_a_state_that_is_not_denser_is_refused_as_a_compression(
    compressed: float,
) -> None:
    """A final state at or below the initial one is not a compression.

    The equal case matters as much as the smaller one: it would report a
    compression ratio of exactly one and a thickness that never moved.
    """
    with pytest.raises(
        DeviceConfigurationError, match="must exceed initial_density_ratio"
    ):
        compression_ratio(INITIAL_RATIO, compressed)


@pytest.mark.parametrize(
    ("initial", "compressed", "field"),
    [
        (0.0, 4.2, "initial_density_ratio"),
        (math.nan, 4.2, "initial_density_ratio"),
        (0.01, 0.0, "compressed_density_ratio"),
        (0.01, -4.2, "compressed_density_ratio"),
    ],
)
def test_the_compression_ratio_refuses_an_unusable_state(
    initial: float, compressed: float, field: str
) -> None:
    """Both states of the compression ratio are refused by name."""
    with pytest.raises(DeviceConfigurationError, match=field):
        compression_ratio(initial, compressed)


@pytest.mark.parametrize("thickness", [0.0, -1.0, math.inf])
def test_the_planar_thickness_refuses_an_unusable_slab(thickness: float) -> None:
    """A slab that is not a positive thickness is refused by name."""
    with pytest.raises(DeviceConfigurationError, match="initial_thickness_cm"):
        planar_compressed_thickness_cm(thickness, INITIAL_RATIO, COMPRESSED_RATIO)


def test_the_planar_thickness_refuses_a_state_pair_that_is_not_a_compression() -> None:
    """The refusal of the ratio reaches the caller of the thickness."""
    with pytest.raises(
        DeviceConfigurationError, match="must exceed initial_density_ratio"
    ):
        planar_compressed_thickness_cm(1.0, 4.2, 0.01)


@pytest.mark.parametrize("radius", [0.0, -0.1, math.nan])
def test_the_spherical_radius_refuses_an_unusable_sphere(radius: float) -> None:
    """A sphere that is not a positive radius is refused by name."""
    with pytest.raises(DeviceConfigurationError, match="radius_cm"):
        spherical_compressed_radius_cm(
            radius, PRINTED_MARSHALL_RADIAL_COMPRESSION_FACTOR
        )


def test_the_spherical_radius_refuses_a_factor_that_does_not_compress() -> None:
    """The factor is validated even when the radius is sound."""
    with pytest.raises(DeviceConfigurationError, match=r"must exceed 1\.0"):
        spherical_compressed_radius_cm(0.1, 1.0)
