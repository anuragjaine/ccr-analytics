# Counterparty Credit Risk (CCR) Analytics & Stress Testing

A Python portfolio project that demonstrates a practical workflow for **counterparty credit risk exposure analytics** across FX forwards, equity forwards and interest-rate swaps.

> **Scope and data notice**  
> This is an independent educational project built from synthetic portfolio data. It is not affiliated with, endorsed by, or based on proprietary systems, data, or models of Barclays or any other bank. The calculations are simplified illustrations, not regulatory IMM, SA-CCR, CVA, Economic Capital or RWA calculations and must not be used for trading, limit setting, regulatory reporting or risk decisions.

## What the project does

- Generates correlated Monte Carlo paths for FX, equity and interest-rate market factors.
- Revalues a mixed-asset-class portfolio at future dates.
- Nets trades **within each netting set** and floors each netting-set value at zero before aggregating positive exposure by counterparty.
- Calculates Expected Exposure (EE), 95th-percentile Potential Future Exposure (PFE) and time-averaged Expected Positive Exposure (EPE).
- Applies deterministic FX, equity and rates shocks to the one-year simulated market state and compares stressed exposure with the unstressed state.
- Produces CSV outputs and charts for review.
- Includes unit tests and a GitHub Actions workflow.

**Explicitly out of scope:** Stressed Expected Loss (SEL), Economic Capital (EC), Risk-Weighted Assets (RWA), regulatory IMM / SA-CCR, collateral modelling and CVA. These require additional credit, collateral, regulatory and validation methodologies that this educational simulation does not implement.

## Mapping to the role profile

| Role-profile theme | Project component |
|---|---|
| CCR exposure analysis across asset classes | FX forward, equity forward and interest-rate swap valuation in `exposure.py` |
| PFE and exposure metric generation / monitoring | EE, PFE and EPE in `metrics.py` |
| Quantitative market / portfolio analysis and stress testing | Correlated market simulation and deterministic shocks in `market.py` and `stress.py` |
| Model development, testing and discussion of results | Modular valuation functions, tests, reproducible random seed and generated reports |
| Controls, documentation and model governance | Input validation, assumptions, limitations, tests and CI workflow |
| Python / Excel / VBA automation skills | Python package and repeatable command-line workflow; CSV outputs are Excel-friendly |

## Quick start

Python 3.10 or later is recommended.

```bash
git clone https://github.com/anuragjaine/ccr-analytics.git
cd ccr-analytics
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

pip install -e .[dev]
pytest
ccr-analytics --portfolio data/portfolio.csv --market data/market_inputs.json --output-dir outputs --scenarios 5000 --seed 42
```

You can also run without installing the console script:

```bash
PYTHONPATH=src python -m ccr_analytics.cli --portfolio data/portfolio.csv --market data/market_inputs.json --output-dir outputs --scenarios 5000 --seed 42
```

## Outputs

The command creates:

- `outputs/counterparty_summary.csv` — counterparty-level EPE and selected PFE measures.
- `outputs/exposure_profile.csv` — EE and PFE by counterparty and future date.
- `outputs/stress_summary.csv` — stressed and unstressed one-year EE / PFE comparisons.
- `outputs/pfe_profile.png` — 95th-percentile exposure profile by counterparty.
- `outputs/stress_comparison.png` — one-year PFE before and after stress.

A small set of example reports generated from 1,000 scenarios is included in `sample_outputs/`. All sample data are synthetic. Results will be reproducible for the same configuration, scenario count and seed.

## Portfolio input format

`data/portfolio.csv` contains one row per trade:

| Column | Meaning |
|---|---|
| `trade_id` | Unique trade identifier |
| `counterparty` | Counterparty identifier |
| `netting_set` | Legal / operational netting-set identifier; netting is only performed within this key |
| `product_type` | `FX_FORWARD`, `EQUITY_FORWARD` or `INTEREST_RATE_SWAP` |
| `underlying` | `EURUSD`, `SPX` or `USD_SWAP_5Y` |
| `notional` | Foreign-currency amount, equity units or swap notional, depending on product |
| `contract_rate` | FX delivery rate, equity delivery price or fixed swap rate |
| `maturity_years` | Remaining maturity at the valuation date, in years |
| `direction` | `RECEIVE_FOREIGN` / `PAY_FOREIGN`, `BUY` / `SELL`, or `RECEIVE_FIXED` / `PAY_FIXED` |

The sample portfolio has intentionally small, readable values. Replace it with appropriately anonymised and authorised data before using the framework for any other purpose.

## Method overview

1. Simulate correlated risk-factor paths on an evenly spaced time grid.
2. Revalue each live trade at every future date using the market state at that date.
3. Sum trade values inside each counterparty/netting-set pair.
4. Calculate positive exposure at netting-set level and aggregate across netting sets for each counterparty.
5. Take the scenario mean for EE, the requested percentile for PFE and the trapezoidal time average of EE for EPE.
6. Apply deterministic shocks to the one-year simulated market state and revalue the portfolio.

See [`docs/methodology.md`](docs/methodology.md) for formulas and [`docs/limitations.md`](docs/limitations.md) for important simplifications.

## Suggested extensions

- Add collateral balances, thresholds, minimum transfer amounts and margin period of risk.
- Replace simplified swap valuation with a curve-based discounted cash-flow engine.
- Add more currencies, commodities, options and credit products.
- Add backtesting / benchmarking, sensitivity analysis and model monitoring thresholds.
- Add CVA only after specifying counterparty PD term structures, recovery assumptions, discounting and wrong-way risk treatment.
- Add an independently reviewed SA-CCR or IMM implementation only with the required regulatory methodology and controls.

## Project structure

```text
ccr-analytics/
├── data/                 # Synthetic portfolio and market assumptions
├── docs/                 # Methodology and limitations
├── src/ccr_analytics/    # Reusable Python package
├── tests/                # Unit tests
└── .github/workflows/    # CI test workflow
```

## License

MIT. See [`LICENSE`](LICENSE).
