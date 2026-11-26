# Methodology notes

## 1. Risk-factor simulation

The model simulates five correlated factors on an evenly spaced time grid: EURUSD (USD per EUR), SPX, USD short rate, EUR short rate and a USD five-year swap-rate proxy. FX and equity levels follow lognormal diffusion steps. The three rate factors follow Euler-discretised mean-reverting Ornstein-Uhlenbeck steps. Correlated standard normal shocks are generated from the configured correlation matrix.

For the illustrative risk-neutral drift, EURUSD uses `r_USD - r_EUR`; SPX uses `r_USD - dividend_yield`. The configured mean-reversion and volatility inputs are illustrative assumptions, not calibrated market parameters.

## 2. Trade valuation

All amounts are expressed as USD-equivalent values for this sample.

### FX forward

For a trade receiving `N` EUR and paying `N K` USD, with spot quoted as USD per EUR:

\[V_t = N S_t e^{-r_{EUR,t}\\tau} - NK e^{-r_{USD,t}\\tau}.\]

A `PAY_FOREIGN` trade reverses the sign. This is a simplified flat-rate discounting treatment.

### Equity forward

For a long forward on `q` units with continuous dividend yield `d` and delivery price `K`:

\[V_t = q(S_t e^{-d\\tau}-K e^{-r_{USD,t}\\tau}).\]

A short forward reverses the sign. Dividend yield is represented continuously; discrete dividends and equity-index financing / basis effects are not modelled.

### Interest-rate swap proxy

The swap is valued using a simplified par-rate proxy:

\[V_t = sN(K-c_t)A_t, \\qquad A_t=\\sum_i \\Delta_i e^{-r_{USD,t}u_i},\]

where `s=+1` for receive-fixed and `s=-1` for pay-fixed. `c_t` is the simulated USD five-year swap-rate proxy. Payment intervals are approximated as half-yearly. This is deliberately not a full multi-curve swap pricer.

## 3. Netting and exposure

Trade MTMs are summed within each `(counterparty, netting_set)` pair. Positive exposure is then calculated as the positive part of that netting-set value. Positive exposures across different netting sets are added; no cross-netting across separate netting sets is assumed.

\[E_{c,s}(t)=\\max(\\sum_{j\\in(c,s)}V_j(t),0),\\qquad E_c(t)=\\sum_s E_{c,s}(t).\]

## 4. Exposure metrics

For simulated counterparty exposure `E_c(t)`:

- **Expected Exposure (EE):** scenario average at each date.
- **PFE 95:** 95th percentile of scenario exposure at each date.
- **Expected Positive Exposure (EPE):** time-average of EE over the configured horizon, calculated with trapezoidal integration.

The selected one-year PFE is taken at the grid point nearest one year; with the included configuration, one year is an exact grid point.

## 5. Stress testing

Deterministic percentage shocks are applied to FX/equity factors and basis-point shocks to rates at the one-year simulated state. The portfolio is revalued for each Monte Carlo scenario after the shock. The output compares the scenario mean and 95th percentile before and after each shock. A stress name describes the shock assumptions, not a forecast or a calibrated historical event.
