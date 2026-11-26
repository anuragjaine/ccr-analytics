import numpy as np
import pytest

from ccr_analytics.metrics import exposure_profile, scalar_metrics


def test_exposure_profile_and_epe():
    exposures = np.array([[0.0, 10.0, 20.0], [0.0, 20.0, 40.0], [0.0, 30.0, 60.0]])
    profile = exposure_profile(exposures, np.array([0.0, 1.0, 2.0]))
    assert profile.loc[1, "expected_exposure"] == pytest.approx(20.0)
    assert profile.loc[2, "pfe"] == pytest.approx(58.0)
    metrics = scalar_metrics(profile)
    assert metrics["epe"] == pytest.approx(20.0)
    assert metrics["pfe_1y"] == pytest.approx(29.0)


def test_bad_quantile_fails():
    with pytest.raises(ValueError):
        exposure_profile(np.ones((2, 2)), np.array([0.0, 1.0]), pfe_quantile=1.0)
