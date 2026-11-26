# Repository setup

This project is published at https://github.com/anuragjaine/ccr-analytics.

## Clone and run

```bash
git clone https://github.com/anuragjaine/ccr-analytics.git
cd ccr-analytics
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

pip install -e .[dev]
pytest
ccr-analytics --portfolio data/portfolio.csv --market data/market_inputs.json --output-dir outputs --scenarios 5000 --seed 42
```

The CI workflow runs the test suite on Python 3.10, 3.11 and 3.12.
