"""Command-line entry point."""
import argparse
import json
from pathlib import Path
from .model import estimate_patch
from .plots import make_plots


def main():
    parser = argparse.ArgumentParser(description="ATLAS-RF first-order patch estimator")
    parser.add_argument("--config", default="config/default.json")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    substrate = config["element_model"]["substrate"]
    frequency_hz = config["simulation"]["receive_frequency_hz"]
    est = estimate_patch(frequency_hz, substrate["relative_permittivity_nominal"], substrate["thickness_m"])
    print("ATLAS-RF — first-order RX element estimate (not fabrication validated)")
    array = config.get("array", {})
    print(f"Array: {array.get('rows',1)} x {array.get('columns',1)} = {array.get('elements',1)} elements")
    print(f"Frequency: {est.frequency_hz/1e9:.6f} GHz")
    print(f"Free-space wavelength: {est.free_space_wavelength_m*1e3:.3f} mm")
    print(f"Patch width W: {est.width_m*1e3:.3f} mm")
    print(f"Patch length L: {est.length_m*1e3:.3f} mm")
    print(f"Effective permittivity: {est.effective_permittivity:.4f}")
    print("No S11, gain, efficiency or real EM field solution is calculated.")
    make_plots(args.output, est.frequency_hz)
    print(f"Illustrative plots written to: {args.output}")


if __name__ == "__main__":
    main()
