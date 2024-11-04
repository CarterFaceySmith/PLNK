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

Using a venv:
```bash
python -m venv venv
source venv/bin/activate
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

## Sample Output

```
2024-11-04 13:14:14,465 [INFO] __main__: Starting dual timeframe portfolio backtest...
Downloading asset data...
Downloading VAS.AX...
Downloading ITA...
Downloading VOOG...
Downloading NLR...
Downloading DTCR...
Downloading VOO...
Downloading BTC-USD...
Downloading SOL-USD...

Data Quality Check:

VAS.AX:
  data_points: 3923
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

ITA:
  data_points: 3822
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

VOOG:
  data_points: 3486
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

NLR:
  data_points: 3822
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

DTCR:
  data_points: 987
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

VOO:
  data_points: 3486
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

BTC-USD:
  data_points: 2565
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

SOL-USD:
  data_points: 1156
  missing_values: 0
  zero_values: 0
  negative_values: 0
  has_sufficient_data: True

Downloading benchmark data...

=== Analysis using maximum date range for each asset ===

Maximum Date Range Analysis
==================================================

Asset Information:

VAS.AX (ASX):
Start Date: 2009-05-01
Data Duration: 15.5 years
Initial Price: $29.94
Final Price: $100.73
Total Return: 236.38%
Annualized Return: 8.14%

ITA (US):
Start Date: 2009-05-01
Data Duration: 15.5 years
Initial Price: $16.65
Final Price: $144.54
Total Return: 768.33%
Annualized Return: 14.96%

VOOG (US):
Start Date: 2010-09-09
Data Duration: 14.1 years
Initial Price: $42.47
Final Price: $345.50
Total Return: 713.49%
Annualized Return: 15.97%

NLR (US):
Start Date: 2009-05-01
Data Duration: 15.5 years
Initial Price: $37.87
Final Price: $90.09
Total Return: 137.90%
Annualized Return: 5.75%

DTCR (US):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $13.81
Final Price: $16.95
Total Return: 22.72%
Annualized Return: 5.24%

VOO (US):
Start Date: 2010-09-09
Data Duration: 14.1 years
Initial Price: $77.97
Final Price: $524.94
Total Return: 573.26%
Annualized Return: 14.43%

BTC-USD (Crypto):
Start Date: 2014-09-17
Data Duration: 10.1 years
Initial Price: $457.33
Final Price: $69482.47
Total Return: 15092.94%
Annualized Return: 64.24%

SOL-USD (Crypto):
Start Date: 2020-04-14
Data Duration: 4.6 years
Initial Price: $0.66
Final Price: $166.26
Total Return: 25017.97%
Annualized Return: 236.85%

=== Analysis using mutual date range across all assets ===

Mutual Date Range Analysis
==================================================

Asset Information:

VAS.AX (ASX):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $63.56
Final Price: $100.73
Total Return: 58.48%
Annualized Return: 12.17%

ITA (US):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $72.93
Final Price: $144.54
Total Return: 98.19%
Annualized Return: 18.61%

VOOG (US):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $198.97
Final Price: $345.50
Total Return: 73.65%
Annualized Return: 14.76%

NLR (US):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $40.91
Final Price: $90.09
Total Return: 120.21%
Annualized Return: 21.77%

DTCR (US):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $13.81
Final Price: $16.95
Total Return: 22.72%
Annualized Return: 5.24%

VOO (US):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $285.47
Final Price: $524.94
Total Return: 83.89%
Annualized Return: 16.41%

BTC-USD (Crypto):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $13437.88
Final Price: $69482.47
Total Return: 417.06%
Annualized Return: 50.67%

SOL-USD (Crypto):
Start Date: 2020-10-29
Data Duration: 4.0 years
Initial Price: $1.43
Final Price: $166.26
Total Return: 11535.38%
Annualized Return: 227.63%

=== Results for Max Range ===

Performance Comparison:
                Portfolio (Monthly Rebalancing)  Portfolio (Quarterly Rebalancing)  Portfolio (Yearly Rebalancing)  Benchmark (S&P500 (USD))  Benchmark (S&P500 (AUD))  Benchmark (World Index (AUD))
Total Return                              -1.00                              -1.00                           10.75                      5.73                      8.04                           1.79
Annual Return                             -0.85                              -0.40                            0.17                      0.14                      0.17                           0.08
Volatility                                 6.20                               6.16                            6.28                      0.17                      3.70                           0.11
Sharpe Ratio                               0.08                               0.09                            0.09                      0.05                      0.02                           0.03
Sortino Ratio                              0.20                               0.23                            0.26                      0.06                      0.17                           0.03
Max Drawdown                              -1.00                              -1.00                           -0.97                     -0.34                     -0.94                          -0.25
Calmar Ratio                              -0.85                              -0.40                            0.18                      0.42                      0.18                           0.30
Win Rate                                   0.54                               0.55                            0.56                      0.55                      0.53                           0.30
Strategy Score                             0.00                               0.00                           14.27                     30.38                     13.62                          26.91

Correlation Matrix:
                   VAS.AX  ITA  VOOG  NLR  DTCR  VOO  BTC-USD  SOL-USD  S&P500 (USD)  S&P500 (AUD)  World Index (AUD)
VAS.AX               1.00 0.24  0.23 0.25  0.08 0.25     0.07     0.04          0.26          0.22               0.38
ITA                  0.24 1.00  0.68 0.61  0.19 0.76     0.13     0.09          0.79          0.04               0.10
VOOG                 0.23 0.68  1.00 0.57  0.41 0.96     0.19     0.17          0.94          0.03               0.08
NLR                  0.25 0.61  0.57 1.00  0.25 0.62     0.11     0.10          0.65          0.03               0.03
DTCR                 0.08 0.19  0.41 0.25  1.00 0.36     0.18     0.21          0.35          0.01               0.05
VOO                  0.25 0.76  0.96 0.62  0.36 1.00     0.17     0.15          0.98          0.04               0.09
BTC-USD              0.07 0.13  0.19 0.11  0.18 0.17     1.00     0.31          0.18          0.02               0.01
SOL-USD              0.04 0.09  0.17 0.10  0.21 0.15     0.31     1.00          0.15         -0.01              -0.02
S&P500 (USD)         0.26 0.79  0.94 0.65  0.35 0.98     0.18     0.15          1.00         -0.00               0.09
S&P500 (AUD)         0.22 0.04  0.03 0.03  0.01 0.04     0.02    -0.01         -0.00          1.00               0.03
World Index (AUD)    0.38 0.10  0.08 0.03  0.05 0.09     0.01    -0.02          0.09          0.03               1.00

Risk Contribution Analysis (% of portfolio risk):
        Risk Contribution
VAS.AX               4.0%
ITA                  6.6%
VOOG                10.0%
NLR                  2.8%
DTCR                 1.2%
VOO                 15.4%
BTC-USD             32.9%
SOL-USD             27.2%

=== Results for Mutual Range ===

Performance Comparison:
                Portfolio (Monthly Rebalancing)  Portfolio (Quarterly Rebalancing)  Portfolio (Yearly Rebalancing)  Benchmark (S&P500 (USD))  Benchmark (S&P500 (AUD))  Benchmark (World Index (AUD))
Total Return                               4.53                               7.30                           19.33                      0.84                      0.88                           0.88
Annual Return                              0.53                               0.69                            1.11                      0.16                      0.17                           0.17
Volatility                                 4.19                               3.90                            4.77                      0.16                      0.13                           0.13
Sharpe Ratio                               0.10                               0.09                            0.10                      0.06                      0.07                           0.07
Sortino Ratio                              0.19                               0.18                            0.22                      0.08                      0.10                           0.10
Max Drawdown                              -0.79                              -0.81                           -0.85                     -0.25                     -0.19                          -0.22
Calmar Ratio                               0.67                               0.86                            1.31                      0.67                      0.91                           0.78
Win Rate                                   0.54                               0.53                            0.54                      0.54                      0.51                           0.50
Strategy Score                            25.40                              29.07                           39.25                     32.39                     33.38                          32.79

Correlation Matrix:
                   VAS.AX  ITA  VOOG   NLR  DTCR  VOO  BTC-USD  SOL-USD  S&P500 (USD)  S&P500 (AUD)  World Index (AUD)
VAS.AX               1.00 0.13  0.16  0.12  0.18 0.18     0.10     0.10          0.18          0.53               0.57
ITA                  0.13 1.00  0.56  0.52  0.41 0.68     0.22     0.14          0.66          0.05               0.05
VOOG                 0.16 0.56  1.00  0.55  0.69 0.96     0.35     0.28          0.94          0.11               0.12
NLR                  0.12 0.52  0.55  1.00  0.49 0.61     0.24     0.20          0.59         -0.02              -0.03
DTCR                 0.18 0.41  0.69  0.49  1.00 0.71     0.30     0.25          0.68          0.05               0.08
VOO                  0.18 0.68  0.96  0.61  0.71 1.00     0.34     0.27          0.98          0.10               0.11
BTC-USD              0.10 0.22  0.35  0.24  0.30 0.34     1.00     0.55          0.33         -0.02              -0.02
SOL-USD              0.10 0.14  0.28  0.20  0.25 0.27     0.55     1.00          0.27         -0.01              -0.01
S&P500 (USD)         0.18 0.66  0.94  0.59  0.68 0.98     0.33     0.27          1.00          0.11               0.12
S&P500 (AUD)         0.53 0.05  0.11 -0.02  0.05 0.10    -0.02    -0.01          0.11          1.00               0.91
World Index (AUD)    0.57 0.05  0.12 -0.03  0.08 0.11    -0.02    -0.01          0.12          0.91               1.00

Risk Contribution Analysis (% of portfolio risk):
        Risk Contribution
VAS.AX               1.8%
ITA                  3.5%
VOOG                 8.0%
NLR                  1.9%
DTCR                 2.3%
VOO                 10.8%
BTC-USD             30.7%
SOL-USD             41.1%
2024-11-04 13:14:19,842 [INFO] __main__: Backtest completed successfully
```

### Notes:

If you find any errors, issues or something of note for a different reason please feel free to either log an issue or [contact me](mailto:carterfs@proton.me).

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.
