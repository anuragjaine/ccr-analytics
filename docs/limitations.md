# Assumptions, controls and limitations

This project is designed to demonstrate quantitative coding and a transparent exposure-analysis workflow. It is not a production counterparty credit risk engine.

## Important limitations

1. **Synthetic inputs:** all trades and market assumptions are invented for demonstration. They are not actual client, bank or market data.
2. **Simplified market dynamics:** lognormal FX/equity paths and one-factor mean-reverting rate proxies do not capture the full dynamics, smiles, basis, jumps or tail dependence of real markets.
3. **Simplified valuation:** swap valuation uses a single par-rate proxy and flat discounting; no bootstrapped discount / forward curves, schedule conventions, resets, day-count rules or optionality are modelled.
4. **No collateral:** thresholds, independent amounts, margin calls, minimum transfer amounts, collateral haircuts, disputes and margin period of risk are omitted.
5. **No credit-side modelling:** default probabilities, recovery, credit migration, wrong-way risk, CVA, DVA, FVA and funding costs are omitted.
6. **No regulatory methodology:** the outputs are not SA-CCR exposure at default, IMM exposure, regulatory capital, RWA or Economic Capital. Do not use them for regulatory or business decisions.
7. **No model calibration or validation claim:** the tests cover software behaviour and selected arithmetic properties, not empirical model performance or regulatory validation.
8. **Netting assumptions:** netting is only within the supplied netting-set identifiers. Legal enforceability is assumed, not assessed.

## Basic controls included

- Required-column, numeric-range, supported-product and trade-ID uniqueness checks.
- Correlation-matrix dimension, symmetry, diagonal and positive-semidefinite checks.
- Deterministic random seed for reproducibility.
- Separate modules for simulation, valuation, metrics, stress tests and reporting.
- Unit tests and continuous integration.

## Before extending the model

Document intended use, ownership, data lineage, calibration, independent validation, limitations, change controls, monitoring thresholds, model performance and approval requirements. Obtain expert review before implementing any regulatory or production use case.
