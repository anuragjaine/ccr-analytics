"""CSV and chart output helpers."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def write_reports(profile: pd.DataFrame, summary: pd.DataFrame, stress: pd.DataFrame, output_dir: str | Path) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    profile.to_csv(out / "exposure_profile.csv", index=False)
    summary.to_csv(out / "counterparty_summary.csv", index=False)
    stress.to_csv(out / "stress_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    for cp, group in profile.groupby("counterparty"):
        ax.plot(group["time_years"], group["pfe"], marker="o", linewidth=1.5, label=cp)
    ax.set(title="95th-percentile Potential Future Exposure", xlabel="Time (years)", ylabel="Exposure (USD)")
    ax.grid(True, alpha=0.3)
    ax.legend(title="Counterparty", ncol=2)
    fig.tight_layout()
    fig.savefig(out / "pfe_profile.png", dpi=160)
    plt.close(fig)

    one_year = stress[stress["stress"].isin(["BASE", "COMBINED_RISK_OFF"])].pivot(
        index="counterparty", columns="stress", values="pfe"
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    one_year.plot(kind="bar", ax=ax)
    ax.set(title="One-year PFE: base vs combined risk-off shock", xlabel="Counterparty", ylabel="PFE (USD)")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "stress_comparison.png", dpi=160)
    plt.close(fig)
