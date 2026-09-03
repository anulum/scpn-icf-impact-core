# SPDX-License-Identifier: AGPL-3.0-or-later
# Commercial license available
# © Concepts 1996–2026 Miroslav Šotek. All rights reserved.
# © Code 2020–2026 Miroslav Šotek. All rights reserved.
# ORCID: 0009-0009-3560-0851
# Contact: www.anulum.li | protoscience@anulum.li
# SCPN ICF Impact Core — repository header artwork generator

"""Generate the three README header images (1280x640) for this repository.

Every image is original generated artwork derived from this repository's
own domain surface — the hypervelocity projectile on its target, the
velocity entry gate the configuration model checks, and the
momentum-to-implosion chain. The right-hand text panel states only
facts backed by the repository itself.

Outputs (written next to this script):

- ``repo_header.png`` — the launcher, projectile and impact-shock
  target (used by ``README.md``).
- ``repo_header_velocity_gate.png`` — the entry-scale threshold with
  flagged and documented regions.
- ``repo_header_momentum_chain.png`` — launch, free flight, impact and
  implosion as a sequence.

Generation-time tooling only: requires ``numpy`` and ``matplotlib``,
which are deliberately not part of the pinned development lock. Run as
``python3 docs/assets/generate_header.py`` from the repository root.
The output is deterministic (fixed geometry, no random input).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

OUT_DIR = Path(__file__).resolve().parent

BG = "#00050a"
CYAN = "#00ccff"
MAGENTA = "#ff00ff"
STEEL = "#334466"
PROBE = "#66aaff"
RED = "#ff3366"
GREEN = "#3ddc84"
GOLD = "#ffcc55"

WIDTH_IN, HEIGHT_IN, DPI = 12.8, 6.4, 100

TITLE_METRICS: list[tuple[str, str]] = [
    ("Device Configuration", "projectile_or_impact_icf"),
    ("Velocity Gate", "below impact-fusion entry scale flagged"),
    ("Reference", "Impact Fusion Workshop, LA-8000-C (1979)"),
    ("Diagnostics & Clocks", "fail-closed vs pinned SPO catalogue"),
    ("Plan Envelope", "v1.1.0 · synthetic · review-only"),
    ("Quality Gates", "100% branch cov · mypy --strict"),
]


def _pyplot() -> Any:
    """Return pyplot configured for headless Agg rendering."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _glow_cmap() -> Any:
    """Build the family glow colormap (deep navy to cyan)."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(
        "scpn_glow",
        ["#00050a", "#001428", "#002d55", "#005588", "#0088bb", "#00ccff"],
    )


def _text_panel(fig: Any, subtitle: str) -> None:
    """Draw the family right-hand text panel onto ``fig``."""
    ax = fig.add_axes([0.62, 0.0, 0.38, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.08,
        0.84,
        "SCPN",
        color="white",
        fontsize=36,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.745,
        "ICF IMPACT",
        color="white",
        fontsize=27,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.695,
        "CORE",
        color="white",
        fontsize=27,
        fontweight="bold",
        fontfamily="monospace",
        alpha=0.95,
    )
    ax.text(
        0.08,
        0.635,
        subtitle,
        color=CYAN,
        fontsize=11,
        fontfamily="monospace",
        alpha=0.85,
    )
    ax.plot([0.08, 0.85], [0.595, 0.595], color=STEEL, lw=0.8, alpha=0.5)
    y = 0.535
    for label, value in TITLE_METRICS:
        ax.text(
            0.08,
            y,
            f"▸ {label}",
            color="#6688aa",
            fontsize=9,
            fontfamily="monospace",
            alpha=0.9,
        )
        ax.text(
            0.10,
            y - 0.030,
            value,
            color="#99bbdd",
            fontsize=8,
            fontfamily="monospace",
            alpha=0.7,
        )
        y -= 0.072
    ax.text(
        0.08,
        0.06,
        "© 1996–2026 Miroslav Šotek",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.6,
    )
    ax.text(
        0.08,
        0.03,
        "anulum.li | AGPL-3.0",
        color="#445566",
        fontsize=7,
        fontfamily="monospace",
        alpha=0.5,
    )


def _art_axes(fig: Any) -> Any:
    """Return the borderless left-hand art axes of ``fig``."""
    ax = fig.add_axes([0.0, 0.0, 0.68, 1.0], facecolor=BG)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def _save(fig: Any, plt: Any, name: str) -> None:
    """Save ``fig`` to ``name`` inside the assets directory and close it."""
    target = OUT_DIR / name
    fig.savefig(target, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0)
    plt.close(fig)
    print(f"generated {target}")


def _target_glow(
    ax: Any,
    centre_x: float,
    centre_z: float,
    core_radius: float,
    halo_radius: float,
) -> None:
    """Draw a glowing spherical target."""
    grid_x = np.linspace(centre_x - halo_radius, centre_x + halo_radius, 140)
    grid_z = np.linspace(centre_z - halo_radius, centre_z + halo_radius, 140)
    mesh_x, mesh_z = np.meshgrid(grid_x, grid_z)
    rho = np.sqrt((mesh_x - centre_x) ** 2 + (mesh_z - centre_z) ** 2) / core_radius
    ax.contourf(
        mesh_x,
        mesh_z,
        np.exp(-rho * 1.8),
        levels=30,
        cmap=_glow_cmap(),
        alpha=0.95,
    )


def generate_projectile_device() -> None:
    """Generate ``repo_header.png``: launcher, projectile and target."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-2.6, 2.6)

    for stage_x in (0.8, 1.7, 2.6):
        ax.add_patch(
            plt.Rectangle(
                (stage_x - 0.22, -0.55),
                0.44,
                1.1,
                fill=False,
                ec=STEEL,
                lw=1.7,
                alpha=0.85,
            )
        )
    ax.text(
        1.7,
        0.95,
        "launcher stages",
        color="#667799",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    streaks = ((-0.22, 1.9, 0.35), (0.0, 2.6, 0.55), (0.22, 1.9, 0.35))
    for offset, length, alpha in streaks:
        ax.plot(
            [5.4 - length, 5.4],
            [offset, offset],
            color=GOLD,
            lw=1.6,
            alpha=alpha,
        )
    ax.add_patch(
        plt.Polygon(
            [[5.35, -0.3], [5.35, 0.3], [6.05, 0.0]],
            closed=True,
            fill=True,
            fc=GOLD,
            ec=GOLD,
            alpha=0.95,
        )
    )
    ax.text(
        5.35,
        -0.72,
        "macroscopic projectile",
        color=GOLD,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.text(
        4.35,
        0.55,
        "hypervelocity flight",
        color="#99bbdd",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )

    _target_glow(ax, 7.9, 0.0, 0.42, 1.15)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)
    ax.plot(
        7.9 + 0.42 * np.cos(theta),
        0.42 * np.sin(theta),
        color=CYAN,
        lw=1.9,
        alpha=0.95,
    )
    for radius, alpha in ((0.62, 0.7), (0.82, 0.5), (1.02, 0.3)):
        arc = np.linspace(-0.85, 0.85, 100)
        ax.plot(
            7.9 - radius * np.cos(arc * 0.9),
            radius * np.sin(arc),
            color="white",
            lw=1.0,
            alpha=alpha,
        )
    ax.text(
        6.7,
        -1.45,
        "impact shock · kinetic energy to compression",
        color="white",
        fontsize=7.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.8,
    )

    ax.text(
        5.0,
        -2.35,
        "stored momentum, delivered in one shot",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "Kinetic Energy As The Driver")
    _save(fig, plt, "repo_header.png")


def generate_velocity_gate() -> None:
    """Generate ``repo_header_velocity_gate.png``: the entry threshold."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)

    ax.plot([1.0, 9.2], [5.0, 5.0], color=STEEL, lw=1.6, alpha=0.8)
    for tick in np.linspace(1.4, 8.8, 8):
        ax.plot([tick, tick], [4.82, 5.18], color=STEEL, lw=1.0, alpha=0.7)
    ax.text(
        9.15,
        4.4,
        "projectile velocity",
        color="#8899bb",
        fontsize=9.5,
        fontfamily="monospace",
        ha="right",
    )

    x_entry = 4.2
    ax.plot(
        [x_entry, x_entry],
        [3.4, 6.6],
        color=MAGENTA,
        lw=1.6,
        alpha=0.9,
        ls=(0, (5, 3)),
    )
    ax.text(
        x_entry,
        6.95,
        "impact-fusion entry scale",
        color=MAGENTA,
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.fill_between([1.0, x_entry], 4.5, 5.5, color=RED, alpha=0.10)
    ax.text(
        (1.0 + x_entry) / 2,
        3.95,
        "declared velocity below scale · FLAGGED",
        color="#ff8899",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )
    ax.fill_between([x_entry, 9.0], 4.5, 5.5, color=GREEN, alpha=0.10)
    ax.text(
        (x_entry + 9.0) / 2,
        3.95,
        "documented workshop regime",
        color=GREEN,
        fontsize=8,
        fontfamily="monospace",
        ha="center",
        alpha=0.95,
    )

    ax.plot(2.6, 5.0, "x", color=RED, ms=10, mew=2.4, alpha=0.95)
    ax.plot(6.1, 5.0, "o", color=CYAN, ms=7, alpha=0.95)
    ax.plot(7.8, 5.0, "o", color=CYAN, ms=7, alpha=0.95)

    ax.add_patch(
        plt.Polygon(
            [[5.6, 7.9], [5.6, 8.5], [6.3, 8.2]],
            closed=True,
            fill=True,
            fc=GOLD,
            ec=GOLD,
            alpha=0.9,
        )
    )
    ax.plot([4.3, 5.55], [8.2, 8.2], color=GOLD, lw=1.4, alpha=0.5)

    ax.text(
        5.0,
        1.35,
        "the gate is one number: fast enough, or flagged · LA-8000-C (1979)",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "One Threshold, Honestly Enforced")
    _save(fig, plt, "repo_header_velocity_gate.png")


def generate_momentum_chain() -> None:
    """Generate ``repo_header_momentum_chain.png``: the four stages."""
    plt = _pyplot()
    fig = plt.figure(figsize=(WIDTH_IN, HEIGHT_IN), dpi=DPI, facecolor=BG)
    ax = _art_axes(fig)
    ax.set_xlim(0, 10)
    ax.set_ylim(-3.2, 3.2)
    theta = np.linspace(0.0, 2.0 * np.pi, 200)

    for stage_x, label in (
        (1.5, "launch"),
        (3.9, "free flight"),
        (6.3, "impact"),
        (8.6, "implosion"),
    ):
        ax.text(
            stage_x,
            -1.9,
            label,
            color="#99bbdd",
            fontsize=8.5,
            fontfamily="monospace",
            ha="center",
            alpha=0.95,
        )

    ax.add_patch(
        plt.Rectangle(
            (0.9, -0.5),
            1.0,
            1.0,
            fill=False,
            ec=STEEL,
            lw=1.7,
            alpha=0.85,
        )
    )
    ax.add_patch(
        plt.Polygon(
            [[1.25, -0.2], [1.25, 0.2], [1.7, 0.0]],
            closed=True,
            fill=True,
            fc=GOLD,
            ec=GOLD,
            alpha=0.95,
        )
    )

    streaks = ((-0.14, 0.8, 0.35), (0.0, 1.2, 0.55), (0.14, 0.8, 0.35))
    for offset, length, alpha in streaks:
        ax.plot(
            [3.75 - length, 3.75],
            [offset, offset],
            color=GOLD,
            lw=1.3,
            alpha=alpha,
        )
    ax.add_patch(
        plt.Polygon(
            [[3.7, -0.2], [3.7, 0.2], [4.15, 0.0]],
            closed=True,
            fill=True,
            fc=GOLD,
            ec=GOLD,
            alpha=0.95,
        )
    )

    _target_glow(ax, 6.55, 0.0, 0.3, 0.75)
    ax.plot(
        6.55 + 0.3 * np.cos(theta),
        0.3 * np.sin(theta),
        color=CYAN,
        lw=1.5,
        alpha=0.95,
    )
    for radius, alpha in ((0.48, 0.7), (0.64, 0.45)):
        arc = np.linspace(-0.85, 0.85, 100)
        ax.plot(
            6.55 - radius * np.cos(arc * 0.9),
            radius * np.sin(arc),
            color="white",
            lw=0.9,
            alpha=alpha,
        )

    _target_glow(ax, 8.6, 0.0, 0.16, 0.55)
    ax.plot(
        8.6 + 0.16 * np.cos(theta),
        0.16 * np.sin(theta),
        color=CYAN,
        lw=1.6,
        alpha=0.95,
    )
    for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        outer = (8.6 + 0.5 * np.cos(angle), 0.5 * np.sin(angle))
        inner = (8.6 + 0.26 * np.cos(angle), 0.26 * np.sin(angle))
        ax.annotate(
            "",
            xy=inner,
            xytext=outer,
            arrowprops={"arrowstyle": "->", "color": PROBE, "lw": 1.0, "alpha": 0.8},
        )

    for arrow_x in (2.15, 4.5, 7.35):
        ax.annotate(
            "",
            xy=(arrow_x + 0.75, 0.0),
            xytext=(arrow_x, 0.0),
            arrowprops={"arrowstyle": "->", "color": STEEL, "lw": 1.3, "alpha": 0.7},
        )

    ax.text(
        5.0,
        2.5,
        "momentum becomes compression",
        color="#667799",
        fontsize=8.5,
        fontfamily="monospace",
        ha="center",
        alpha=0.9,
    )
    ax.text(
        5.0,
        -2.85,
        "declared projectile and target · validated, never fired",
        color="#445566",
        fontsize=8,
        fontfamily="monospace",
        ha="center",
    )
    _text_panel(fig, "From Momentum To Implosion")
    _save(fig, plt, "repo_header_momentum_chain.png")


if __name__ == "__main__":
    generate_projectile_device()
    generate_velocity_gate()
    generate_momentum_chain()
