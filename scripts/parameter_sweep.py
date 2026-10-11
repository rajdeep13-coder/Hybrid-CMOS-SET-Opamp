"""parameter_sweep.py

Automates parameter sweeps (e.g., gate capacitance, tunneling resistance,
temperature, bias currents) for hybrid CMOS-SET op-amp characterization.
Can be executed as standalone or interfaced with MATLAB Engine API.
"""

import argparse
import json
from pathlib import Path

def run_parameter_sweep(param_name: str, start: float, stop: float, steps: int):
    print(f"Configuring parameter sweep for '{param_name}' from {start} to {stop} across {steps} points.")
    step_size = (stop - start) / max(steps - 1, 1)
    values = [start + i * step_size for i in range(steps)]
    
    results = []
    for val in values:
        print(f"Simulating point: {param_name} = {val:.4e}")
        # Placeholder for MATLAB Engine or SPICE/Simulink batch simulation execution
        results.append({
            param_name: val,
            "status": "pending_simulation"
        })
    
    output_path = Path(__file__).resolve().parent / "sweep_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Sweep definition saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sweep parameters for Hybrid CMOS-SET Op-Amp")
    parser.add_argument("--param", type=str, default="Cg", help="Parameter name to sweep (e.g. Cg, Temp, Ibias)")
    parser.add_argument("--start", type=float, default=1e-19, help="Start value")
    parser.add_argument("--stop", type=float, default=5e-18, help="Stop value")
    parser.add_argument("--steps", type=int, default=10, help="Number of sweep points")
    args = parser.parse_args()

    run_parameter_sweep(args.param, args.start, args.stop, args.steps)
