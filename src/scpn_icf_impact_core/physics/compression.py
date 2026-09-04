# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — where the fuel ends up

"""Where the fuel ends up, in each of the two geometries.

Compression is stated here as conservation of mass and nothing else. A
slab driven along one axis keeps its cross-section, so its thickness
falls exactly as its density rises; a sphere converging on its centre
keeps nothing but its mass, so its density rises as the cube of the
factor its radius falls by. Both are geometry, and neither needs an
equation of state.

**Nothing here solves a shock.** The filed worked case reaches its final
density through four states connected by the Rankine-Hugoniot relations
and an equation of state, none of which this repository carries. What
this module does is take the initial and final densities that case
prints and state what they imply for the dimension — which is the step
that case itself performs in one line.

Design record: ADR 0005.
"""

from __future__ import annotations

from scpn_icf_impact_core.errors import DeviceConfigurationError
from scpn_icf_impact_core.parameters import require_positive


def require_compression_factor(name: str, value: float) -> float:
    """Return a compression factor when it is strictly above one.

    Parameters
    ----------
    name
        Field name reported in the rejection message.
    value
        Value under validation.

    Returns
    -------
    float
        The validated factor.

    Raises
    ------
    DeviceConfigurationError
        If the value is non-finite, not strictly positive, or at or
        below one. A factor of one leaves the target where it was and a
        factor below one expands it; neither is a compression, and
        naming either one would make the record say something it does
        not mean.
    """
    require_positive(name, value)
    if value <= 1.0:
        raise DeviceConfigurationError(
            f"{name}: must exceed 1.0 to be a compression, got {value!r}"
        )
    return value


def compression_ratio(
    initial_density_ratio: float, compressed_density_ratio: float
) -> float:
    """Return how far the fuel density rises between two declared states.

    Parameters
    ----------
    initial_density_ratio, compressed_density_ratio
        The two densities, each as a multiple of the same reference;
        both strictly positive, and the compressed one strictly the
        larger.

    Returns
    -------
    float
        The ratio of the two. Because both are quoted against the same
        reference, that reference cancels and the answer does not depend
        on it.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive, or the
        compressed state is not denser than the initial one.
    """
    require_positive("initial_density_ratio", initial_density_ratio)
    require_positive("compressed_density_ratio", compressed_density_ratio)
    if compressed_density_ratio <= initial_density_ratio:
        raise DeviceConfigurationError(
            "compressed_density_ratio: must exceed initial_density_ratio, got "
            f"{compressed_density_ratio!r} <= {initial_density_ratio!r}"
        )
    return compressed_density_ratio / initial_density_ratio


def planar_compressed_thickness_cm(
    initial_thickness_cm: float,
    initial_density_ratio: float,
    compressed_density_ratio: float,
) -> float:
    """Return the thickness a driven slab is compressed to.

    Parameters
    ----------
    initial_thickness_cm
        Slab thickness before the plate arrives, in centimetres;
        strictly positive.
    initial_density_ratio, compressed_density_ratio
        The fuel density before and at peak compression, each as a
        multiple of the same reference; the compressed one strictly the
        larger.

    Returns
    -------
    float
        Compressed thickness in centimetres.

    Raises
    ------
    DeviceConfigurationError
        If a value is non-finite or not strictly positive, or the
        compressed state is not denser than the initial one.

    Notes
    -----
    A slab driven along one axis keeps its cross-section, so the mass
    behind each unit of that cross-section is unchanged and the areal
    density is the same before and after. The thickness therefore falls
    by exactly the factor the density rises by.
    """
    require_positive("initial_thickness_cm", initial_thickness_cm)
    ratio = compression_ratio(initial_density_ratio, compressed_density_ratio)
    return initial_thickness_cm / ratio


def spherical_compressed_radius_cm(
    radius_cm: float, radial_compression_factor: float
) -> float:
    """Return the radius a converging sphere is compressed to.

    Parameters
    ----------
    radius_cm
        Sphere radius before compression, in centimetres; strictly
        positive.
    radial_compression_factor
        The factor the radius falls by; strictly above one.

    Returns
    -------
    float
        Compressed radius in centimetres.

    Raises
    ------
    DeviceConfigurationError
        If the radius is non-finite or not strictly positive, or the
        factor does not exceed one.
    """
    require_positive("radius_cm", radius_cm)
    require_compression_factor("radial_compression_factor", radial_compression_factor)
    return radius_cm / radial_compression_factor


def spherical_density_ratio(radial_compression_factor: float) -> float:
    """Return how far a converging sphere's density rises.

    Parameters
    ----------
    radial_compression_factor
        The factor the radius falls by; strictly above one.

    Returns
    -------
    float
        The factor the density rises by, which is the cube of the
        radial factor.

    Raises
    ------
    DeviceConfigurationError
        If the factor is non-finite or does not exceed one.

    Notes
    -----
    This is where the convergent scheme earns its advantage over the
    planar one. A slab gains areal density only by what its density
    gains, because its thickness falls by the same factor and the two
    cancel exactly; a sphere gains the cube in density while losing only
    the first power in radius, so its areal density rises as the square
    of the radial factor.
    """
    require_compression_factor("radial_compression_factor", radial_compression_factor)
    return radial_compression_factor**3
