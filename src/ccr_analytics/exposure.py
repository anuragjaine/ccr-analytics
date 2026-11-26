"""Trade valuation and netting-set exposure aggregation."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .market import MarketPaths

REQUIRED_COLUMNS = {
    "trade_id", "counterparty", "netting_set", "product_type", "underlying",
    "notional", "contract_rate", "maturity_years", "direction",
}


def validate_portfolio(portfolio: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS.difference(portfolio.columns)
    if missing:
        raise ValueError(f"portfolio is missing columns: {sorted(missing)}")
    if portfolio.empty:
        raise ValueError("portfolio must contain at least one trade")
    if portfolio["trade_id"].duplicated().any():
        raise ValueError("trade_id values must be unique")
    for col in ("notional", "contract_rate", "maturity_years"):
        values = pd.to_numeric(portfolio[col], errors="coerce")
        if values.isna().any() or not np.isfinite(values.to_numpy()).all():
            raise ValueError(f"{col} must contain finite numeric values")
    if (portfolio["notional"].astype(float) <= 0).any():
        raise ValueError("notional must be positive")
    if (portfolio["maturity_years"].astype(float) <= 0).any():
        raise ValueError("maturity_years must be positive")

    allowed = {
        "FX_FORWARD": {"RECEIVE_FOREIGN", "PAY_FOREIGN"},
        "EQUITY_FORWARD": {"BUY", "SELL"},
        "INTEREST_RATE_SWAP": {"RECEIVE_FIXED", "PAY_FIXED"},
    }
    for row in portfolio.itertuples(index=False):
        if row.product_type not in allowed:
            raise ValueError(f"unsupported product_type: {row.product_type}")
        if row.direction not in allowed[row.product_type]:
            raise ValueError(f"invalid direction {row.direction} for {row.product_type}")
        expected = {
            "FX_FORWARD": "EURUSD",
            "EQUITY_FORWARD": "SPX",
            "INTEREST_RATE_SWAP": "USD_SWAP_5Y",
        }[row.product_type]
        if row.underlying != expected:
            raise ValueError(f"{row.product_type} requires underlying {expected}")


def _trade_mtm(row: object, factors: dict[str, np.ndarray], time_years: float) -> np.ndarray:
    """Return scenario MTM in USD for one trade at one future date."""
    n_scenarios = len(next(iter(factors.values())))
    remaining = float(row.maturity_years) - time_years
    if remaining <= 0:
        return np.zeros(n_scenarios)

    if row.product_type == "FX_FORWARD":
        spot = factors["EURUSD"]
        usd_rate = factors["USD_RATE"]
        eur_rate = factors["EUR_RATE"]
        foreign_pv = float(row.notional) * spot * np.exp(-eur_rate * remaining)
        domestic_pv = float(row.notional) * float(row.contract_rate) * np.exp(-usd_rate * remaining)
        sign = 1.0 if row.direction == "RECEIVE_FOREIGN" else -1.0
        return sign * (foreign_pv - domestic_pv)

    if row.product_type == "EQUITY_FORWARD":
        spot = factors["SPX"]
        usd_rate = factors["USD_RATE"]
        dividend_yield = factors.get("SPX_DIVIDEND_YIELD", np.zeros_like(spot))
        sign = 1.0 if row.direction == "BUY" else -1.0
        forward_value = (
            spot * np.exp(-dividend_yield * remaining)
            - float(row.contract_rate) * np.exp(-usd_rate * remaining)
        )
        return sign * float(row.notional) * forward_value

    swap_rate = factors["USD_SWAP_5Y"]
    usd_rate = factors["USD_RATE"]
    payment_times = np.arange(0.5, remaining + 1e-9, 0.5)
    accruals = np.full(payment_times.size, 0.5, dtype=float)
    if payment_times.size == 0 or payment_times[-1] < remaining - 1e-9:
        payment_times = np.append(payment_times, remaining)
        accruals = np.append(accruals, remaining - (payment_times[-2] if payment_times.size > 1 else 0.0))
    annuity = np.sum(
        np.exp(-usd_rate[:, None] * payment_times[None, :]) * accruals[None, :], axis=1
    )
    sign = 1.0 if row.direction == "RECEIVE_FIXED" else -1.0
    return sign * float(row.notional) * (float(row.contract_rate) - swap_rate) * annuity


def exposures_at_state(
    portfolio: pd.DataFrame,
    factors: dict[str, np.ndarray],
    time_years: float,
) -> dict[str, np.ndarray]:
    """Aggregate positive exposure by counterparty after netting within netting sets."""
    validate_portfolio(portfolio)
    netting_values: dict[tuple[str, str], np.ndarray] = {}
    for row in portfolio.itertuples(index=False):
        key = (str(row.counterparty), str(row.netting_set))
        mtm = _trade_mtm(row, factors, time_years)
        netting_values[key] = netting_values.get(key, np.zeros_like(mtm)) + mtm

    result: dict[str, np.ndarray] = {}
    for (counterparty, _netting_set), net_value in netting_values.items():
        result[counterparty] = result.get(counterparty, np.zeros_like(net_value)) + np.maximum(net_value, 0.0)
    return result


def compute_exposure_paths(portfolio: pd.DataFrame, market: MarketPaths) -> tuple[list[str], np.ndarray]:
    """Return counterparty exposure cube with shape (scenarios, dates, counterparties)."""
    validate_portfolio(portfolio)
    counterparties = sorted(portfolio["counterparty"].astype(str).unique())
    n_scenarios = next(iter(market.factors.values())).shape[0]
    cube = np.zeros((n_scenarios, len(market.times), len(counterparties)))
    for date_index, time_years in enumerate(market.times):
        state = {name: values[:, date_index] for name, values in market.factors.items()}
        by_cp = exposures_at_state(portfolio, state, float(time_years))
        for cp_index, counterparty in enumerate(counterparties):
            cube[:, date_index, cp_index] = by_cp.get(counterparty, np.zeros(n_scenarios))
    return counterparties, cube
