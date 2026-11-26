"""Correlated market-factor simulation for the educational CCR example."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class MarketPaths:
    """Simulated risk factors; each factor has shape (scenarios, time_steps)."""

    times: np.ndarray
    factors: dict[str, np.ndarray]


def simulate_market_paths(config: dict[str, Any], n_scenarios: int, seed: int = 42) -> MarketPaths:
    """Simulate FX/equity geometric Brownian motions and mean-reverting rates.

    FX is quoted as USD per EUR. Under the illustrative USD risk-neutral measure,
    its drift is r_USD - r_EUR. Equity drift is r_USD - dividend_yield.
    Three rate factors use Euler-discretised Ornstein-Uhlenbeck processes.
    """
    if n_scenarios < 1:
        raise ValueError("n_scenarios must be at least 1")

    horizon = float(config["horizon_years"])
    n_steps = int(config["steps"])
    if horizon <= 0 or n_steps < 1:
        raise ValueError("horizon_years and steps must be positive")

    factor_names = ["EURUSD", "SPX", "USD_RATE", "EUR_RATE", "USD_SWAP_5Y"]
    corr = np.asarray(config["correlation"], dtype=float)
    if corr.shape != (len(factor_names), len(factor_names)):
        raise ValueError("correlation must be a 5 x 5 matrix")
    if not np.allclose(corr, corr.T, atol=1e-10):
        raise ValueError("correlation matrix must be symmetric")
    if not np.allclose(np.diag(corr), 1.0, atol=1e-10):
        raise ValueError("correlation matrix must have ones on its diagonal")
    if np.linalg.eigvalsh(corr).min() < -1e-8:
        raise ValueError("correlation matrix must be positive semidefinite")

    rng = np.random.default_rng(seed)
    dt = horizon / n_steps
    times = np.linspace(0.0, horizon, n_steps + 1)
    z = rng.standard_normal((n_scenarios, n_steps, len(factor_names)))
    chol = np.linalg.cholesky(corr + np.eye(len(factor_names)) * 1e-12)
    z = z @ chol.T

    initial = config["initial"]
    vol = config["volatility"]
    rate_cfg = config["rates"]
    factors = {
        "EURUSD": np.empty((n_scenarios, n_steps + 1)),
        "SPX": np.empty((n_scenarios, n_steps + 1)),
        "USD_RATE": np.empty((n_scenarios, n_steps + 1)),
        "EUR_RATE": np.empty((n_scenarios, n_steps + 1)),
        "USD_SWAP_5Y": np.empty((n_scenarios, n_steps + 1)),
    }
    for name in factors:
        factors[name][:, 0] = float(initial[name])

    for step in range(n_steps):
        usd = factors["USD_RATE"][:, step]
        eur = factors["EUR_RATE"][:, step]
        fx = factors["EURUSD"][:, step]
        equity = factors["SPX"][:, step]

        factors["USD_RATE"][:, step + 1] = (
            usd + float(rate_cfg["USD_RATE"]["kappa"]) *
            (float(rate_cfg["USD_RATE"]["theta"]) - usd) * dt
            + float(vol["USD_RATE"]) * np.sqrt(dt) * z[:, step, 2]
        )
        factors["EUR_RATE"][:, step + 1] = (
            eur + float(rate_cfg["EUR_RATE"]["kappa"]) *
            (float(rate_cfg["EUR_RATE"]["theta"]) - eur) * dt
            + float(vol["EUR_RATE"]) * np.sqrt(dt) * z[:, step, 3]
        )
        swap = factors["USD_SWAP_5Y"][:, step]
        factors["USD_SWAP_5Y"][:, step + 1] = (
            swap + float(rate_cfg["USD_SWAP_5Y"]["kappa"]) *
            (float(rate_cfg["USD_SWAP_5Y"]["theta"]) - swap) * dt
            + float(vol["USD_SWAP_5Y"]) * np.sqrt(dt) * z[:, step, 4]
        )
        drift_fx = usd - eur
        factors["EURUSD"][:, step + 1] = fx * np.exp(
            (drift_fx - 0.5 * float(vol["EURUSD"]) ** 2) * dt
            + float(vol["EURUSD"]) * np.sqrt(dt) * z[:, step, 0]
        )
        dividend = float(config.get("equity_dividend_yield", 0.015))
        factors["SPX"][:, step + 1] = equity * np.exp(
            (usd - dividend - 0.5 * float(vol["SPX"]) ** 2) * dt
            + float(vol["SPX"]) * np.sqrt(dt) * z[:, step, 1]
        )

    dividend = float(config.get("equity_dividend_yield", 0.015))
    factors["SPX_DIVIDEND_YIELD"] = np.full((n_scenarios, n_steps + 1), dividend)
    return MarketPaths(times=times, factors=factors)
