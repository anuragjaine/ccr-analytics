"""Deterministic market shocks applied to the simulated one-year market state."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .exposure import exposures_at_state
from .market import MarketPaths

DEFAULT_STRESSES = {
    "FX_EUR_UP_10": {"EURUSD_pct": 0.10},
    "EQUITY_DOWN_20": {"SPX_pct": -0.20},
    "RATES_UP": {"USD_RATE_bps": 100, "EUR_RATE_bps": 50, "USD_SWAP_5Y_bps": 150},
    "COMBINED_RISK_OFF": {
        "EURUSD_pct": -0.10, "SPX_pct": -0.20,
        "USD_RATE_bps": 100, "EUR_RATE_bps": 50, "USD_SWAP_5Y_bps": 150,
    },
}


def stress_exposures(
    portfolio: pd.DataFrame,
    market: MarketPaths,
    stresses: dict[str, dict[str, float]] | None = None,
    horizon_years: float = 1.0,
    pfe_quantile: float = 0.95,
) -> pd.DataFrame:
    """Revalue each Monte Carlo scenario after deterministic shocks at a selected horizon."""
    stresses = stresses or DEFAULT_STRESSES
    index = int(np.argmin(np.abs(market.times - horizon_years)))
    actual_time = float(market.times[index])
    base_state = {key: values[:, index].copy() for key, values in market.factors.items()}
    records: list[dict[str, float | str]] = []

    for stress_name, shocks in {"BASE": {}, **stresses}.items():
        shocked = {key: value.copy() for key, value in base_state.items()}
        for key, shock in shocks.items():
            if key.endswith("_pct"):
                factor = key[:-4]
                shocked[factor] *= (1.0 + float(shock))
            elif key.endswith("_bps"):
                factor = key[:-4]
                shocked[factor] += float(shock) / 10_000.0
            else:
                raise ValueError(f"unsupported stress field: {key}")
        by_cp = exposures_at_state(portfolio, shocked, actual_time)
        for counterparty, values in by_cp.items():
            records.append({
                "stress": stress_name,
                "counterparty": counterparty,
                "horizon_years": actual_time,
                "expected_exposure": float(np.mean(values)),
                "pfe": float(np.quantile(values, pfe_quantile)),
            })
    return pd.DataFrame.from_records(records)
