"""Analytical, explicitly non-full-wave models for Atlas RF.

SI units internally. Nothing in this module calculates measured/validated S11,
realized gain, efficiency, mutual coupling, or a true near-field solution.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np

C0_M_S = 299_792_458.0


@dataclass(frozen=True)
class PatchEstimate:
    frequency_hz: float
    width_m: float
    effective_permittivity: float
    effective_length_m: float
    length_m: float
    free_space_wavelength_m: float


def estimate_patch(frequency_hz: float, eps_r: float, substrate_height_m: float) -> PatchEstimate:
    """First-order rectangular microstrip patch estimate; not fabrication-ready."""
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive")
    if eps_r <= 1:
        raise ValueError("eps_r must be greater than 1")
    if substrate_height_m <= 0:
        raise ValueError("substrate_height_m must be positive")
    wavelength = C0_M_S / frequency_hz
    width = C0_M_S / (2 * frequency_hz) * math.sqrt(2 / (eps_r + 1))
    eps_eff = ((eps_r + 1) / 2) + ((eps_r - 1) / 2) / math.sqrt(1 + 12 * substrate_height_m / width)
    length_eff = C0_M_S / (2 * frequency_hz * math.sqrt(eps_eff))
    ratio = width / substrate_height_m
    delta_l = 0.412 * substrate_height_m * (((eps_eff + 0.3) * (ratio + 0.264)) / ((eps_eff - 0.258) * (ratio + 0.8)))
    length = length_eff - 2 * delta_l
    if length <= 0:
        raise ValueError("Estimated patch length is non-positive; check inputs")
    return PatchEstimate(frequency_hz, width, eps_eff, length_eff, length, wavelength)


def array_positions(rows: int, cols: int, spacing_x_m: float, spacing_z_m: float) -> np.ndarray:
    """Element centers in the X-Z plane; boresight is +Y."""
    if rows < 1 or cols < 1 or spacing_x_m <= 0 or spacing_z_m <= 0:
        raise ValueError("rows/cols must be positive and spacings must be > 0")
    xs = (np.arange(cols) - (cols - 1) / 2) * spacing_x_m
    zs = (np.arange(rows) - (rows - 1) / 2) * spacing_z_m
    xx, zz = np.meshgrid(xs, zs)
    return np.column_stack((xx.ravel(), zz.ravel()))


def array_factor(rows: int, cols: int, frequency_hz: float, spacing_x_m: float,
                 spacing_z_m: float, theta_rad, phi_rad=0.0,
                 phase_weights_rad=None, amplitude_weights=None) -> np.ndarray:
    """Normalized array factor; theta is measured from +Y."""
    if frequency_hz <= 0:
        raise ValueError("frequency_hz must be positive")
    positions = array_positions(rows, cols, spacing_x_m, spacing_z_m)
    n = len(positions)
    theta = np.asarray(theta_rad, dtype=float)
    phi = np.asarray(phi_rad, dtype=float)
    ux = np.sin(theta) * np.cos(phi)
    uz = np.sin(theta) * np.sin(phi)
    k = 2 * np.pi * frequency_hz / C0_M_S
    phases = np.zeros(n) if phase_weights_rad is None else np.asarray(phase_weights_rad, dtype=float).reshape(-1)
    amps = np.ones(n) if amplitude_weights is None else np.asarray(amplitude_weights, dtype=float).reshape(-1)
    if len(phases) != n or len(amps) != n:
        raise ValueError("phase/amplitude weight count must equal number of elements")
    if np.any(amps < 0):
        raise ValueError("amplitude weights cannot be negative")
    phase = k * (positions[:, 0, None] * np.ravel(ux)[None, :] + positions[:, 1, None] * np.ravel(uz)[None, :]) + phases[:, None]
    field = np.sum(amps[:, None] * np.exp(1j * phase), axis=0)
    norm = max(float(np.sum(amps)), 1e-15)
    return (np.abs(field) / norm).reshape(theta.shape)


def array_pattern_grid(rows: int, cols: int, frequency_hz: float, spacing_x_m: float,
                       spacing_z_m: float, theta_deg=None, phi_deg=None):
    theta_deg = np.linspace(0, 90, 181) if theta_deg is None else np.asarray(theta_deg)
    phi_deg = np.linspace(-180, 180, 361) if phi_deg is None else np.asarray(phi_deg)
    TH, PH = np.meshgrid(np.radians(theta_deg), np.radians(phi_deg), indexing="ij")
    af = array_factor(rows, cols, frequency_hz, spacing_x_m, spacing_z_m, TH, PH)
    return theta_deg, phi_deg, 10 * np.log10(np.maximum(af**2, 1e-6))


def evaluate_design(rows: int, cols: int, frequency_hz: float, spacing_x_m: float,
                    spacing_z_m: float) -> dict:
    af_boresight = float(array_factor(rows, cols, frequency_hz, spacing_x_m, spacing_z_m, np.array(0.0)))
    wavelength = C0_M_S / frequency_hz
    return {
        "status": "ANALYTICAL_ESTIMATE_NOT_FULL_WAVE_VALIDATED",
        "elements": rows * cols, "frequency_hz": float(frequency_hz),
        "wavelength_m": wavelength, "spacing_x_lambda": spacing_x_m / wavelength,
        "spacing_z_lambda": spacing_z_m / wavelength,
        "normalized_array_factor_boresight": af_boresight,
        "s11_db": None, "realized_gain_dbi": None, "efficiency_percent": None,
        "front_to_back_db": None, "mutual_coupling": "not modelled",
    }


def cosine_power_pattern(theta_rad, exponent: float = 8.0):
    """Illustrative cosine pattern proxy only; not a validated element pattern."""
    return np.clip(np.cos(np.asarray(theta_rad, dtype=float)), 0.0, None) ** exponent


def back_to_front_ratio_db(front_power: float, back_power: float) -> float:
    """Return 10*log10(back/front), only for physically supplied powers."""
    if front_power <= 0 or back_power < 0:
        raise ValueError("front_power must be positive and back_power non-negative")
    if back_power == 0:
        return float("-inf")
    return 10 * math.log10(back_power / front_power)


def spacing_sweep(rows: int, cols: int, frequency_hz: float, spacing_fractions=None) -> list[dict]:
    """Analytical spacing sweep; not ML or EM optimization."""
    if spacing_fractions is None:
        spacing_fractions = np.linspace(0.30, 0.70, 17)
    if rows < 1 or cols < 2 or frequency_hz <= 0:
        raise ValueError("rows must be >=1, cols >=2 and frequency_hz > 0")
    wavelength = C0_M_S / frequency_hz
    theta = np.radians(np.linspace(0, 90, 1801))
    results = []
    for fraction in spacing_fractions:
        if fraction <= 0:
            continue
        spacing = float(fraction) * wavelength
        cut = array_factor(rows, cols, frequency_hz, spacing, spacing, theta, np.zeros_like(theta))
        power_db = 10 * np.log10(np.maximum(cut**2, 1e-9))
        null_arg = min(1.0, 1.0 / (cols * float(fraction)))
        first_null_deg = float(np.degrees(np.arcsin(null_arg)))
        mask = np.degrees(theta) >= min(90.0, first_null_deg + 1.0)
        peak = float(np.max(power_db[mask])) if np.any(mask) else float("nan")
        results.append({"spacing_lambda": float(fraction), "spacing_mm": spacing * 1000,
            "estimated_first_null_deg": first_null_deg, "beamwidth_proxy_deg": 2 * first_null_deg,
            "peak_sidelobe_cut_db": peak, "status": "ANALYTICAL_SWEEP_NOT_EM_VALIDATED"})
    return sorted(results, key=lambda r: r["peak_sidelobe_cut_db"])
