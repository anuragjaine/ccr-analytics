import json
from pathlib import Path

import numpy as np

from ccr_analytics.market import simulate_market_paths

CONFIG = json.loads((Path(__file__).parents[1] / "data" / "market_inputs.json").read_text())


def test_simulation_is_reproducible_and_has_expected_shape():
    first = simulate_market_paths(CONFIG, n_scenarios=50, seed=7)
    second = simulate_market_paths(CONFIG, n_scenarios=50, seed=7)
    assert first.times.shape == (CONFIG["steps"] + 1,)
    assert first.factors["SPX"].shape == (50, CONFIG["steps"] + 1)
    np.testing.assert_allclose(first.factors["EURUSD"], second.factors["EURUSD"])


def test_invalid_scenario_count_fails():
    import pytest
    with pytest.raises(ValueError, match="at least 1"):
        simulate_market_paths(CONFIG, n_scenarios=0)
