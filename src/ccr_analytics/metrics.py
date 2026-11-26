"""Exposure profile and counterparty-level metric calculations."""
from __future__ import annotations

import numpy as np
import pandas as pd


def exposure_profile(exposures: np.ndarray, times: np.ndarray, pfe_quantile: float = 0.95) -> pd.DataFrame:
    """Compute EE and PFE for a (scenarios, dates) exposure matrix."""
    if exposures.ndim != 2:
        raise ValueError("exposures must be a two-dimensional scenarios x dates array")
    if exposures.shape[1] != len(times):
        raise ValueError("the number of exposure dates must match times")
    if not 0 < pfe_quantile < 1:
        raise ValueError("pfe_quantile must be between 0 and 1")
    if np.any(exposures < -1e-10):
        raise ValueError("positive exposure input cannot contain negative values")
    return pd.DataFrame({
        "time_years": times,
        "expected_exposure": exposures.mean(axis=0),
        "pfe": np.quantile(exposures, pfe_quantile, axis=0),
    })


def scalar_metrics(profile: pd.DataFrame) -> dict[str, float]:
    """Calculate time-averaged EPE and selected horizon PFE values."""
    times = profile["time_years"].to_numpy(dtype=float)
    ee = profile["expected_exposure"].to_numpy(dtype=float)
    pfe = profile["pfe"].to_numpy(dtype=float)
    horizon = float(times[-1])
    trapezoid_area = float(np.sum(0.5 * (ee[1:] + ee[:-1]) * np.diff(times)))
    epe = trapezoid_area / horizon if horizon > 0 else float(ee[0])
    one_year_idx = int(np.argmin(np.abs(times - 1.0)))
    three_year_idx = int(np.argmin(np.abs(times - 3.0)))
    return {
        "epe": epe,
        "pfe_1y": float(pfe[one_year_idx]),
        "pfe_3y": float(pfe[three_year_idx]),
        "max_pfe": float(np.max(pfe)),
    }
