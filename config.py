from datetime import datetime

class BacktestConfig:
    # Portfolio Settings
    PORTFOLIO = {
        'VAS.AX': 0.15,
        'ITA': 0.10,
        'VOOG': 0.15,
        'NLR': 0.05,
        'DTCR': 0.05,
        'VOO': 0.25,
        'BTC-USD': 0.15,
        'SOL-USD': 0.10
    }
    
    # Backtest Parameters
    START_DATE = '2017-11-09'
    END_DATE = datetime.now().strftime('%Y-%m-%d')
    BENCHMARK_START_DATE = '2017-01-01'
    
    # Display Settings (corrected)
    DISPLAY_OPTIONS = {
        'display.max_columns': None,
        'display.width': None,
        'display.precision': 2,
        'display.float_format': lambda x: f'{x:.2f}' if isinstance(x, float) else str(x)
    }
    
    # Rebalancing Settings
    REBALANCING_PERIODS = {
        'ME': 'Monthly',
        'QE': 'Quarterly', 
        'YE': 'Yearly'
    }

    DISPLAY_ORDER = [
        'Strategy Score',
        'Total Return',
        'Annual Return',
        'Volatility',
        'Sharpe Ratio',
        'Sortino Ratio',
        'Max Drawdown',
        'Calmar Ratio',
        'Win Rate'
    ]
    
    # Risk-Free Rate Settings
    RISK_FREE_RATE = 0.02  # 2% annual risk-free rate
    
    # Benchmark Definitions
    BENCHMARK_PORTFOLIOS = {
        '60/40 Portfolio': {'SPY': 0.6, 'AGG': 0.4},
        'All Weather': {'SPY': 0.3, 'TLT': 0.4, 'GLD': 0.15, 'DBC': 0.075, 'VNQ': 0.075},
        'Global Market': {'VT': 1.0}
    }
    
    # Risk Analysis Settings
    RISK_SETTINGS = {
        'VAR_CONFIDENCE': 0.95,
        'ROLLING_WINDOW': 126,  # ~6 months of trading days
        'MIN_TRADING_DAYS': 20,
        'ANNUALIZATION_FACTOR': 252
    }
    
    # Scoring Weights
    SCORING_WEIGHTS = {
        'Annual Return': 0.25,
        'Sharpe Ratio': 0.20,
        'Sortino Ratio': 0.15,
        'Max Drawdown': 0.15,
        'Win Rate': 0.15,
        'Volatility': 0.10
    }
    
    # Market Condition Definitions
    MARKET_CONDITIONS = {
        'Bull Market': lambda returns: returns > returns.mean(),
        'Bear Market': lambda returns: returns < returns.mean(),
        'High Vol': lambda returns: returns.rolling(21).std() > returns.std(),
        'Low Vol': lambda returns: returns.rolling(21).std() <= returns.std()
    }
    
    # Asset Classifications
    ASSET_CLASSIFICATIONS = {
        'ASX': lambda ticker: ticker.endswith('.AX'),
        'Crypto': lambda ticker: ticker.endswith('-USD'),
        'US': lambda ticker: not (ticker.endswith('.AX') or ticker.endswith('-USD'))
    }
    
    # Logging Configuration
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
            },
            'file': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'logs/backtest.log',
                'mode': 'a',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    
    @classmethod
    def validate_portfolio(cls):
        """Validate portfolio weights sum to 1"""
        total_weight = sum(cls.PORTFOLIO.values())
        if not abs(total_weight - 1.0) < 1e-6:
            raise ValueError(f"Portfolio weights sum to {total_weight}, not 1.0")
        return True
    
    @classmethod
    def get_market_type(cls, ticker):
        """Get market type for a given ticker"""
        for market, condition in cls.ASSET_CLASSIFICATIONS.items():
            if condition(ticker):
                return market
        return 'Other'