"""Command-line entry point for the CCR analytics project."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .exposure import compute_exposure_paths
from .market import simulate_market_paths
from .metrics import exposure_profile, scalar_metrics
from .reporting import write_reports
from .stress import stress_exposures


def run(portfolio_path: str, market_path: str, output_dir: str, scenarios: int, seed: int) -> None:
    portfolio = pd.read_csv(portfolio_path)
    with Path(market_path).open("r", encoding="utf-8") as handle:
        config = json.load(handle)

    market = simulate_market_paths(config, n_scenarios=scenarios, seed=seed)
    counterparties, cube = compute_exposure_paths(portfolio, market)

    profile_frames = []
    summary_rows = []
    for cp_index, counterparty in enumerate(counterparties):
        profile = exposure_profile(cube[:, :, cp_index], market.times)
        profile.insert(0, "counterparty", counterparty)
        profile_frames.append(profile)
        summary_rows.append({"counterparty": counterparty, **scalar_metrics(profile)})

    all_profiles = pd.concat(profile_frames, ignore_index=True)
    summary = pd.DataFrame(summary_rows).sort_values("epe", ascending=False)
    stress = stress_exposures(portfolio, market)
    write_reports(all_profiles, summary, stress, output_dir)

    print(f"Completed {scenarios:,} scenarios for {len(counterparties)} counterparties.")
    print(f"Reports written to: {Path(output_dir).resolve()}")
    print(summary.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate CCR exposure profiles and stress scenarios.")
    parser.add_argument("--portfolio", default="data/portfolio.csv")
    parser.add_argument("--market", default="data/market_inputs.json")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--scenarios", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run(args.portfolio, args.market, args.output_dir, args.scenarios, args.seed)


if __name__ == "__main__":
    main()
