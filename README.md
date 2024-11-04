<h3 align="center">PLNK: Portfolio Backtest Analysis Tool</h3>
<br>
<p align="center"><i>A comprehensive portfolio analysis tool for multi-asset backtesting with flexible date ranges and risk metrics</i></p>

## About The Project

This portfolio backtest analysis tool provides in-depth performance and risk analysis for multi-asset portfolios. It features:

- Dual timeframe analysis (maximum available data and mutual date ranges)
- Comprehensive risk metrics (Sharpe, Sortino, Calmar ratios)
- Multiple rebalancing strategies (monthly, quarterly, yearly)
- Correlation and risk contribution analysis
- Benchmark comparisons
- Support for stocks, crypto, and international assets

## Getting Started

To get started with the portfolio backtest tool:

### Prerequisites

```bash
pip install -r requirements.txt
```

### Configuration

Create a `config.py` file with your portfolio settings:

```python
class BacktestConfig:
    # Portfolio weights
    PORTFOLIO = {
        'VAS.AX': 0.15,  # ASX ETF
        'ITA': 0.10,     # US Stock
        'VOOG': 0.15,    # US ETF
        'NLR': 0.05,     # US ETF
        'DTCR': 0.05,    # US Stock
        'VOO': 0.25,     # US ETF
        'BTC-USD': 0.15, # Crypto
        'SOL-USD': 0.10  # Crypto
    }
    
    # Display settings
    DISPLAY_OPTIONS = {
        'display.max_columns': None,
        'display.width': None,
        'display.precision': 2,
        'display.float_format': lambda x: f'{x:.2f}' if isinstance(x, float) else str(x)
    }
    
    # Logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            }
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
```

### Usage

Run the analysis:

```python
python main.py
```

The tool will output:
- Asset-specific performance metrics
- Portfolio rebalancing analysis
- Risk metrics and contributions
- Correlation analysis
- Benchmark comparisons

### Notes:

If you find any errors, issues or something of note for a different reason please feel free to either log an issue or [contact me](mailto:carterfs@proton.me).

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
