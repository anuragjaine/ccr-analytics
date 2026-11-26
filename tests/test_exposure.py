import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ccr_analytics.exposure import compute_exposure_paths, exposures_at_state, validate_portfolio
from ccr_analytics.market import simulate_market_paths

ROOT = Path(__file__).parents[1]
PORTFOLIO = pd.read_csv(ROOT / "data" / "portfolio.csv")
CONFIG = json.loads((ROOT / "data" / "market_inputs.json").read_text())


def test_exposure_cube_is_non_negative_and_correct_shape():
    market = simulate_market_paths(CONFIG, n_scenarios=40, seed=11)
    counterparties, cube = compute_exposure_paths(PORTFOLIO, market)
    assert len(counterparties) == PORTFOLIO["counterparty"].nunique()
    assert cube.shape == (40, len(market.times), len(counterparties))
    assert np.all(cube >= 0)


def test_netting_within_set_can_reduce_positive_exposure():
    portfolio = pd.DataFrame([
        ["A", "CP_X", "NET_1", "EQUITY_FORWARD", "SPX", 1.0, 90.0, 1.0, "BUY"],
        ["B", "CP_X", "NET_1", "EQUITY_FORWARD", "SPX", 1.0, 90.0, 1.0, "SELL"],
        ["C", "CP_X", "NET_2", "EQUITY_FORWARD", "SPX", 1.0, 110.0, 1.0, "SELL"],
    ], columns=PORTFOLIO.columns)
    factors = {"SPX": np.array([100.0]), "USD_RATE": np.array([0.0])}
    result = exposures_at_state(portfolio, factors, 0.0)
    # Net_1 has +10 and -10 (net zero); Net_2 is +10 because the short forward is in-the-money.
    assert result["CP_X"][0] == pytest.approx(10.0)


def test_duplicate_trade_id_fails():
    bad = pd.concat([PORTFOLIO, PORTFOLIO.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="unique"):
        validate_portfolio(bad)


def test_exposure_is_zero_after_all_trades_in_netting_set_mature():
    factors = {
        "SPX": np.array([100.0]),
        "USD_RATE": np.array([0.03]),
    }
    single_trade = PORTFOLIO.iloc[[3]].copy()
    result = exposures_at_state(single_trade, factors, time_years=1.0)
    assert result["CP_B"][0] == pytest.approx(0.0)
