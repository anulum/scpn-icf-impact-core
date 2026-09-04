# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — level-0 physics record

"""Level-0 physics record of the owned impact-ICF configuration.

The configuration carries a projectile's mass and velocity and a
target's outer radius, and nothing else. Three things it does not carry
are declared here in three objects, each about one subject: what the
fuel is, what the projectile is made of and how wide a face it presents,
and the dimensions of the two target geometries.

The record then evaluates
:mod:`~scpn_icf_impact_core.physics.projectile` on the plate,
:mod:`~scpn_icf_impact_core.physics.fuel` on the fuel and
:mod:`~scpn_icf_impact_core.physics.compression` on where that fuel ends
up, in **both** geometries the filed proceedings describe.

**Both geometries are carried because the proceedings describe both, and
no filed source pairs them.** The dimensioned worked case is a plane
slab struck by a uranium plate; the only anchored convergent target is a
solid fuel sphere in a different paper of the same proceedings, which
prints no projectile at all. The record evaluates each on what its own
paper prints and states in its non-claims that the two are not one
design.

**Nothing here runs backwards**, which is the difference from the
sibling beam family. No filed source in this family prints a yield or a
burn-up fraction, so neither is implied from the other; what the record
carries instead is the energy a complete burn of each inventory would
release, which is an upper bound and is named as one.

Design record: ADR 0005.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from scpn_icf_impact_core.configuration import DeviceConfiguration
from scpn_icf_impact_core.parameters import require_positive
from scpn_icf_impact_core.physics.compression import (
    compression_ratio,
    planar_compressed_thickness_cm,
    require_compression_factor,
    spherical_compressed_radius_cm,
    spherical_density_ratio,
)
from scpn_icf_impact_core.physics.fuel import (
    density_from_ratio_g_cm3,
    full_burn_energy_mj,
    ideal_gas_density_g_cm3,
    require_below_unity,
    slab_areal_density_g_cm2,
    slab_mass_mg,
    sphere_areal_density_g_cm2,
    sphere_mass_mg,
)
from scpn_icf_impact_core.physics.projectile import (
    areal_density_g_cm2,
    energy_per_area_mj_per_cm2,
    plate_thickness_cm,
)

LEVEL0_SCHEMA: Final = "scpn.impact-icf-level0-physics.v1"
LEVEL0_SCHEMA_VERSION: Final = "1.0.0"
#: Micrometres in a centimetre. The configuration carries the target
#: radius in micrometres and every relation here is stated in
#: centimetres; this is the only place the two meet.
MICROMETRES_PER_CENTIMETRE: Final = 1.0e4
#: Kilojoules in a megajoule. The projectile's kinetic energy is owned
#: by the parameter model in kilojoules and reported here in megajoules.
KILOJOULES_PER_MEGAJOULE: Final = 1.0e3
LEVEL0_NON_CLAIMS: Final = (
    (
        "closed-form evaluation of published impact-fusion relations on a "
        "declared fuel, a declared projectile material and declared target "
        "dimensions; nothing here is integrated in time"
    ),
    (
        "no shock is solved, no equation of state is evaluated, no "
        "hydrodynamics is performed and no burn calculation is attempted "
        "anywhere here"
    ),
    (
        "the fuel densities before and at peak compression are declared "
        "inputs taken from a published worked case; the four-state chain "
        "that produced them, and the equation of state it rests on, are not "
        "carried and could not be checked"
    ),
    (
        "the plane and the convergent geometry come from two different "
        "papers of one proceedings and no filed source pairs them: the "
        "projectile belongs to the plane case, and the paper that prints "
        "the convergent target prints no projectile for it"
    ),
    (
        "the ideal-gas density is a consistency instrument, not a printed "
        "value; it assumes an ideal gas of diatomic molecules, which the "
        "source does not state, and agrees with the printed density ratio "
        "only to the one significant figure that ratio carries"
    ),
    (
        "the full-burn energies assume every atom of the inventory reacts, "
        "which no target achieves; no filed source in this family prints a "
        "burn-up fraction and none is invented here"
    ),
    (
        "the areal-density ratios compare declared targets to one another "
        "and say nothing about whether either would ignite"
    ),
    (
        "no value describes or validates any real machine or shot; an "
        "anchor reproduces a number a filed source prints and nothing "
        "further"
    ),
)


@dataclass(frozen=True, slots=True)
class FuelDeclaration:
    """Declared state of the fuel, before the plate arrives and at peak.

    Parameters
    ----------
    cryogenic_density_g_cm3
        Density of the fuel as a cryogenic liquid, which is the
        reference every declared ratio is taken against; strictly
        positive.
    initial_pressure_bar
        Pressure of the fuel gas before impact; strictly positive.
    initial_temperature_k
        Temperature of the fuel gas before impact; strictly positive.
    initial_density_ratio
        Gas density as a multiple of the cryogenic density; strictly
        positive and **below one**.
    compressed_density_ratio
        Fuel density at peak compression as a multiple of the cryogenic
        density; strictly positive and above the initial ratio.

    Raises
    ------
    DeviceConfigurationError
        If any value is non-finite or not strictly positive, if the
        initial ratio reaches the cryogenic density, or if the
        compressed state is not denser than the initial one.
    """

    cryogenic_density_g_cm3: float
    initial_pressure_bar: float
    initial_temperature_k: float
    initial_density_ratio: float
    compressed_density_ratio: float

    def __post_init__(self) -> None:
        """Validate the declared fuel states.

        Raises
        ------
        DeviceConfigurationError
            If any value is non-finite or not strictly positive, if the
            initial ratio reaches the cryogenic density, or if the
            compressed state is not denser than the initial one. The
            first refusal is what keeps the declaration a gas: fuel at
            or above its own cryogenic liquid density is not the gas the
            declared pressure and temperature describe.
        """
        require_positive("cryogenic_density_g_cm3", self.cryogenic_density_g_cm3)
        require_positive("initial_pressure_bar", self.initial_pressure_bar)
        require_positive("initial_temperature_k", self.initial_temperature_k)
        require_below_unity("initial_density_ratio", self.initial_density_ratio)
        compression_ratio(self.initial_density_ratio, self.compressed_density_ratio)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "cryogenic_density_g_cm3": self.cryogenic_density_g_cm3,
            "initial_pressure_bar": self.initial_pressure_bar,
            "initial_temperature_k": self.initial_temperature_k,
            "initial_density_ratio": self.initial_density_ratio,
            "compressed_density_ratio": self.compressed_density_ratio,
        }


@dataclass(frozen=True, slots=True)
class ProjectileDeclaration:
    """Declared properties of the plate beyond its mass and velocity.

    Parameters
    ----------
    material_density_g_cm3
        Bulk density of the plate material; strictly positive.
    impact_area_cm2
        Area of the face the plate presents to the target; strictly
        positive.

    Raises
    ------
    DeviceConfigurationError
        If either value is non-finite or not strictly positive.

    Notes
    -----
    The mass and the velocity are not here. They belong to the
    configuration's own projectile, which owns them and the kinetic
    energy that follows.
    """

    material_density_g_cm3: float
    impact_area_cm2: float

    def __post_init__(self) -> None:
        """Validate the declared plate.

        Raises
        ------
        DeviceConfigurationError
            If either value is non-finite or not strictly positive.
        """
        require_positive("material_density_g_cm3", self.material_density_g_cm3)
        require_positive("impact_area_cm2", self.impact_area_cm2)

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "material_density_g_cm3": self.material_density_g_cm3,
            "impact_area_cm2": self.impact_area_cm2,
        }


@dataclass(frozen=True, slots=True)
class SchemeDeclaration:
    """Declared dimensions of the two target geometries.

    Parameters
    ----------
    slab_thickness_cm
        Fuel thickness of the plane target along the plate's direction
        of travel; strictly positive.
    radial_compression_factor
        Factor the convergent target's radius falls by; strictly above
        one.

    Raises
    ------
    DeviceConfigurationError
        If the thickness is non-finite or not strictly positive, or the
        factor does not exceed one.

    Notes
    -----
    The convergent target's uncompressed radius is not here: it is the
    target radius the configuration declares.
    """

    slab_thickness_cm: float
    radial_compression_factor: float

    def __post_init__(self) -> None:
        """Validate the declared dimensions.

        Raises
        ------
        DeviceConfigurationError
            If the thickness is non-finite or not strictly positive, or
            the factor does not exceed one.
        """
        require_positive("slab_thickness_cm", self.slab_thickness_cm)
        require_compression_factor(
            "radial_compression_factor", self.radial_compression_factor
        )

    def to_record(self) -> dict[str, Any]:
        """Project the declaration to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per declared field.
        """
        return {
            "slab_thickness_cm": self.slab_thickness_cm,
            "radial_compression_factor": self.radial_compression_factor,
        }


@dataclass(frozen=True, slots=True)
class OperatingPoint:
    """Composed level-0 operating point of one configuration.

    Parameters
    ----------
    projectile_kinetic_energy_mj
        Kinetic energy the configuration's projectile carries.
    projectile_specific_kinetic_energy_j_per_kg
        That energy per unit of the plate's mass.
    projectile_areal_density_g_cm2
        Plate mass per unit of the face it presents.
    projectile_thickness_cm
        How thick the declared material has to be to carry it.
    projectile_energy_per_area_mj_per_cm2
        Energy the face delivers per unit area.
    initial_fuel_density_g_cm3
        Fuel gas density before impact, from the declared ratio.
    ideal_gas_density_g_cm3
        What the ideal-gas law gives for the declared pressure and
        temperature; a consistency instrument, not a printed value.
    compressed_fuel_density_g_cm3
        Fuel density at peak compression, from the declared ratio.
    slab_compression_ratio
        How far the plane target's density rises.
    slab_fuel_mass_mg
        Fuel mass of the plane target over the plate's face.
    slab_areal_density_g_cm2
        Areal density along the plane target's axis, which one-axis
        compression leaves unchanged.
    compressed_slab_thickness_cm
        Thickness the plane target is compressed to.
    slab_full_burn_energy_mj
        Energy the plane target's inventory would release if all of it
        burned.
    driven_areal_density_ratio
        Plate areal density over the plane target's, which is the
        quantity the worked case's own equation is solved for.
    sphere_radius_cm
        Convergent target radius, from the configuration.
    sphere_fuel_mass_mg
        Fuel mass of the convergent target before compression.
    compressed_sphere_radius_cm
        Radius it is compressed to.
    compressed_sphere_density_g_cm3
        Density it reaches, which rises as the cube of the radial
        factor.
    sphere_areal_density_g_cm2
        Areal density from its centre outwards at peak compression.
    sphere_full_burn_energy_mj
        Energy its inventory would release if all of it burned.
    convergence_areal_density_ratio
        The convergent target's areal density over the plane target's.
    """

    projectile_kinetic_energy_mj: float
    projectile_specific_kinetic_energy_j_per_kg: float
    projectile_areal_density_g_cm2: float
    projectile_thickness_cm: float
    projectile_energy_per_area_mj_per_cm2: float
    initial_fuel_density_g_cm3: float
    ideal_gas_density_g_cm3: float
    compressed_fuel_density_g_cm3: float
    slab_compression_ratio: float
    slab_fuel_mass_mg: float
    slab_areal_density_g_cm2: float
    compressed_slab_thickness_cm: float
    slab_full_burn_energy_mj: float
    driven_areal_density_ratio: float
    sphere_radius_cm: float
    sphere_fuel_mass_mg: float
    compressed_sphere_radius_cm: float
    compressed_sphere_density_g_cm3: float
    sphere_areal_density_g_cm2: float
    sphere_full_burn_energy_mj: float
    convergence_areal_density_ratio: float

    def to_record(self) -> dict[str, Any]:
        """Project the operating point to a JSON-serialisable record.

        Returns
        -------
        dict[str, Any]
            One key per field, in the declaration order of the class.
        """
        return {
            "projectile_kinetic_energy_mj": self.projectile_kinetic_energy_mj,
            "projectile_specific_kinetic_energy_j_per_kg": (
                self.projectile_specific_kinetic_energy_j_per_kg
            ),
            "projectile_areal_density_g_cm2": self.projectile_areal_density_g_cm2,
            "projectile_thickness_cm": self.projectile_thickness_cm,
            "projectile_energy_per_area_mj_per_cm2": (
                self.projectile_energy_per_area_mj_per_cm2
            ),
            "initial_fuel_density_g_cm3": self.initial_fuel_density_g_cm3,
            "ideal_gas_density_g_cm3": self.ideal_gas_density_g_cm3,
            "compressed_fuel_density_g_cm3": self.compressed_fuel_density_g_cm3,
            "slab_compression_ratio": self.slab_compression_ratio,
            "slab_fuel_mass_mg": self.slab_fuel_mass_mg,
            "slab_areal_density_g_cm2": self.slab_areal_density_g_cm2,
            "compressed_slab_thickness_cm": self.compressed_slab_thickness_cm,
            "slab_full_burn_energy_mj": self.slab_full_burn_energy_mj,
            "driven_areal_density_ratio": self.driven_areal_density_ratio,
            "sphere_radius_cm": self.sphere_radius_cm,
            "sphere_fuel_mass_mg": self.sphere_fuel_mass_mg,
            "compressed_sphere_radius_cm": self.compressed_sphere_radius_cm,
            "compressed_sphere_density_g_cm3": self.compressed_sphere_density_g_cm3,
            "sphere_areal_density_g_cm2": self.sphere_areal_density_g_cm2,
            "sphere_full_burn_energy_mj": self.sphere_full_burn_energy_mj,
            "convergence_areal_density_ratio": (self.convergence_areal_density_ratio),
        }


@dataclass(frozen=True, slots=True)
class Level0Physics:
    """Composed level-0 record of one configuration.

    Parameters
    ----------
    configuration_digest_sha256
        Digest of the configuration the record was built from.
    fuel
        The declared fuel states.
    projectile
        The declared plate material and face.
    scheme
        The declared dimensions of the two geometries.
    operating_point
        The composed operating point.
    """

    configuration_digest_sha256: str
    fuel: FuelDeclaration
    projectile: ProjectileDeclaration
    scheme: SchemeDeclaration
    operating_point: OperatingPoint

    def to_record(self) -> dict[str, Any]:
        """Project the record to a JSON-serialisable object.

        Returns
        -------
        dict[str, Any]
            The schema-tagged record with its non-claims.
        """
        return {
            "schema": LEVEL0_SCHEMA,
            "schema_version": LEVEL0_SCHEMA_VERSION,
            "configuration_digest_sha256": self.configuration_digest_sha256,
            "fuel": self.fuel.to_record(),
            "projectile": self.projectile.to_record(),
            "scheme": self.scheme.to_record(),
            "operating_point": self.operating_point.to_record(),
            "non_claims": list(LEVEL0_NON_CLAIMS),
        }

    def canonical_bytes(self) -> bytes:
        """Serialise the record canonically.

        Returns
        -------
        bytes
            UTF-8 JSON with sorted keys, minimal separators and a
            trailing newline; NaN and infinity are never emitted.
        """
        text = json.dumps(
            self.to_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        return (text + "\n").encode("utf-8")

    def digest_sha256(self) -> str:
        """Identify the exact record.

        Returns
        -------
        str
            SHA-256 of :meth:`canonical_bytes` as lowercase hex.
        """
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def target_radius_cm(configuration: DeviceConfiguration) -> float:
    """Return the convergent target's radius in centimetres.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration.

    Returns
    -------
    float
        The radius the configuration declares, converted once.
    """
    return configuration.target.target_radius_um / MICROMETRES_PER_CENTIMETRE


def level0_physics(
    configuration: DeviceConfiguration,
    fuel: FuelDeclaration,
    projectile: ProjectileDeclaration,
    scheme: SchemeDeclaration,
) -> Level0Physics:
    """Compose the level-0 physics record of one validated configuration.

    Parameters
    ----------
    configuration
        Validated impact-ICF configuration supplying the plate's mass
        and velocity and the convergent target's radius.
    fuel
        Declared fuel states.
    projectile
        Declared plate material and face.
    scheme
        Declared dimensions of the two geometries.

    Returns
    -------
    Level0Physics
        The composed record.

    Raises
    ------
    DeviceConfigurationError
        If a declared value leaves its documented interval; the
        refusals name the field.
    """
    specific_energy = configuration.projectile.specific_kinetic_energy_j_kg()
    plate_areal = areal_density_g_cm2(
        configuration.projectile.mass_mg, projectile.impact_area_cm2
    )
    initial_density = density_from_ratio_g_cm3(
        fuel.initial_density_ratio, fuel.cryogenic_density_g_cm3
    )
    compressed_density = density_from_ratio_g_cm3(
        fuel.compressed_density_ratio, fuel.cryogenic_density_g_cm3
    )
    slab_areal = slab_areal_density_g_cm2(scheme.slab_thickness_cm, initial_density)
    slab_mass = slab_mass_mg(
        scheme.slab_thickness_cm, projectile.impact_area_cm2, initial_density
    )
    sphere_radius = target_radius_cm(configuration)
    sphere_mass = sphere_mass_mg(sphere_radius, fuel.cryogenic_density_g_cm3)
    compressed_sphere_radius = spherical_compressed_radius_cm(
        sphere_radius, scheme.radial_compression_factor
    )
    compressed_sphere_density = density_from_ratio_g_cm3(
        spherical_density_ratio(scheme.radial_compression_factor),
        fuel.cryogenic_density_g_cm3,
    )
    sphere_areal = sphere_areal_density_g_cm2(
        compressed_sphere_radius, compressed_sphere_density
    )
    return Level0Physics(
        configuration_digest_sha256=configuration.digest_sha256(),
        fuel=fuel,
        projectile=projectile,
        scheme=scheme,
        operating_point=OperatingPoint(
            projectile_kinetic_energy_mj=(
                configuration.projectile.kinetic_energy_kj() / KILOJOULES_PER_MEGAJOULE
            ),
            projectile_specific_kinetic_energy_j_per_kg=specific_energy,
            projectile_areal_density_g_cm2=plate_areal,
            projectile_thickness_cm=plate_thickness_cm(
                plate_areal, projectile.material_density_g_cm3
            ),
            projectile_energy_per_area_mj_per_cm2=energy_per_area_mj_per_cm2(
                plate_areal, specific_energy
            ),
            initial_fuel_density_g_cm3=initial_density,
            ideal_gas_density_g_cm3=ideal_gas_density_g_cm3(
                fuel.initial_pressure_bar, fuel.initial_temperature_k
            ),
            compressed_fuel_density_g_cm3=compressed_density,
            slab_compression_ratio=compression_ratio(
                fuel.initial_density_ratio, fuel.compressed_density_ratio
            ),
            slab_fuel_mass_mg=slab_mass,
            slab_areal_density_g_cm2=slab_areal,
            compressed_slab_thickness_cm=planar_compressed_thickness_cm(
                scheme.slab_thickness_cm,
                fuel.initial_density_ratio,
                fuel.compressed_density_ratio,
            ),
            slab_full_burn_energy_mj=full_burn_energy_mj(slab_mass),
            driven_areal_density_ratio=plate_areal / slab_areal,
            sphere_radius_cm=sphere_radius,
            sphere_fuel_mass_mg=sphere_mass,
            compressed_sphere_radius_cm=compressed_sphere_radius,
            compressed_sphere_density_g_cm3=compressed_sphere_density,
            sphere_areal_density_g_cm2=sphere_areal,
            sphere_full_burn_energy_mj=full_burn_energy_mj(sphere_mass),
            convergence_areal_density_ratio=sphere_areal / slab_areal,
        ),
    )
