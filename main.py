import matplotlib
# matplotlib.use('TkAgg')  # Commented out as requested
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import seaborn as sns
import logging.config
from config import BacktestConfig

def calculate_risk_metrics(returns):
    """Calculate advanced risk-adjusted performance metrics with proper error handling"""
    daily_rf = 0.02/252  # Assuming 2% risk-free rate
    
    try:
        total_return = (1 + returns).cumprod().iloc[-1] - 1
        
        # Handle annualization safely
        if len(returns) > 0:
            ann_factor = 252/len(returns)
            annual_return = (1 + total_return) ** ann_factor - 1
        else:
            annual_return = np.nan
        
        # Handle volatility and ratios safely
        volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else np.nan
        
        # Sharpe Ratio with error handling
        if volatility > 0 and not np.isnan(volatility):
            sharpe = ((returns.mean() - daily_rf) * np.sqrt(252)) / volatility
        else:
            sharpe = np.nan
        
        # Sortino Ratio with error handling
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252)
        if downside_std > 0 and not np.isnan(downside_std):
            sortino = ((returns.mean() - daily_rf) * np.sqrt(252)) / downside_std
        else:
            sortino = np.nan
        
        # Max Drawdown with error handling
        cum_returns = (1 + returns).cumprod()
        if len(cum_returns) > 0:
            rolling_max = cum_returns.cummax()
            drawdowns = cum_returns / rolling_max - 1
            max_drawdown = drawdowns.min()
        else:
            max_drawdown = np.nan
        
        # Calmar Ratio with error handling
        if max_drawdown < 0 and not np.isnan(max_drawdown):
            calmar = annual_return / abs(max_drawdown)
        else:
            calmar = np.nan
        
        # Win Rate with error handling
        if len(returns) > 0:
            win_rate = len(returns[returns > 0]) / len(returns)
        else:
            win_rate = np.nan
        
        metrics = {
            'Total Return': total_return,
            'Annual Return': annual_return,
            'Volatility': volatility,
            'Sharpe Ratio': sharpe,
            'Sortino Ratio': sortino,
            'Max Drawdown': max_drawdown,
            'Calmar Ratio': calmar,
            'Win Rate': win_rate
        }
        
        # Replace infinite values with nan
        metrics = {k: np.nan if np.isinf(v) else v 
                  for k, v in metrics.items()}
        
        return metrics
    
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return {
            'Total Return': np.nan,
            'Annual Return': np.nan,
            'Volatility': np.nan,
            'Sharpe Ratio': np.nan,
            'Sortino Ratio': np.nan,
            'Max Drawdown': np.nan,
            'Calmar Ratio': np.nan,
            'Win Rate': np.nan
        }

def calculate_composite_score(metrics):
    """Calculate composite score with error handling"""
    weights = {
        'Annual Return': 0.25,
        'Sharpe Ratio': 0.20,
        'Sortino Ratio': 0.15,
        'Max Drawdown': 0.15,
        'Win Rate': 0.15,
        'Volatility': 0.10
    }
    
    try:
        # Handle nan and inf values
        if any(np.isnan(metrics[k]) or np.isinf(metrics[k]) 
               for k in weights.keys()):
            return np.nan
        
        score = (
            metrics['Annual Return'] * weights['Annual Return'] * 100 +
            np.clip(metrics['Sharpe Ratio'], -10, 10) * weights['Sharpe Ratio'] * 20 +
            np.clip(metrics['Sortino Ratio'], -10, 10) * weights['Sortino Ratio'] * 20 +
            np.clip((1 + metrics['Max Drawdown']), 0, 1) * weights['Max Drawdown'] * 100 +
            metrics['Win Rate'] * weights['Win Rate'] * 100 +
            np.clip((1 - metrics['Volatility']), 0, 1) * weights['Volatility'] * 100
        )
        
        return np.clip(score, 0, 100)
    
    except Exception as e:
        print(f"Error calculating composite score: {e}")
        return np.nan

def calculate_risk_contribution(returns_data, weights):
    """Calculate risk contribution of each asset"""
    cov_matrix = returns_data.cov() * 252  # Annualized covariance
    portfolio_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
    
    # Calculate marginal risk contribution
    mrc = np.dot(cov_matrix, weights) / portfolio_vol
    
    # Calculate component risk contribution
    rc = np.multiply(weights, mrc)
    
    # Calculate percentage risk contribution
    prc = rc / portfolio_vol
    
    return pd.Series(prc, index=returns_data.columns)

def calculate_correlation_analysis(returns_data, benchmark_returns):
    """Calculate correlation analysis between assets and benchmarks"""
    # Handle empty benchmark returns
    if benchmark_returns.empty:
        return returns_data.corr(), {}
    
    # Combine asset and benchmark returns
    all_returns = pd.concat([returns_data, benchmark_returns], axis=1)
    
    # Calculate correlation matrix
    correlation_matrix = all_returns.corr()
    
    # Calculate rolling correlations with benchmarks (6-month window)
    rolling_correlations = {}
    window = 126  # ~6 months of trading days
    
    for benchmark in benchmark_returns.columns:
        rolling_corr = pd.DataFrame()
        for asset in returns_data.columns:
            rolling_corr[asset] = returns_data[asset].rolling(window).corr(benchmark_returns[benchmark])
        rolling_correlations[benchmark] = rolling_corr
    
    return correlation_matrix, rolling_correlations

def rebalance_portfolio(portfolio_weights, price_data, rebalance_period):
    """Simulate portfolio performance with periodic rebalancing"""
    try:
        # Initial portfolio setup
        portfolio_value = 1.0
        portfolio_values = pd.Series(index=price_data.index)
        
        # Initialize positions based on initial prices
        positions = {}
        for ticker, weight in portfolio_weights.items():
            if not np.isnan(price_data[ticker].iloc[0]):
                positions[ticker] = portfolio_value * weight / price_data[ticker].iloc[0]
        
        # Get rebalancing dates
        rebalance_dates = price_data.resample(rebalance_period).last().index
        last_rebalance_date = price_data.index[0]
        
        # Calculate daily values
        for date in price_data.index:
            current_value = 0
            for ticker, position in positions.items():
                if not np.isnan(price_data[ticker][date]):
                    current_value += position * price_data[ticker][date]
            
            portfolio_values[date] = current_value
            
            # Rebalance if needed
            if date in rebalance_dates and date > last_rebalance_date:
                for ticker, target_weight in portfolio_weights.items():
                    if not np.isnan(price_data[ticker][date]):
                        positions[ticker] = (current_value * target_weight / 
                                          price_data[ticker][date])
                last_rebalance_date = date
        
        return portfolio_values
        
    except Exception as e:
        print(f"Error in rebalancing calculation: {e}")
        return pd.Series(index=price_data.index)

def calculate_metrics(price_data, benchmark_data, portfolio_weights, 
                     asset_markets, asset_start_dates, use_mutual_dates=False):
    """Calculate metrics with improved error handling"""
    timeframe_type = "Mutual" if use_mutual_dates else "Maximum"
    print(f"\n{timeframe_type} Date Range Analysis")
    print("=" * 50)
    
    # Print asset information
    print("\nAsset Information:")
    for ticker in price_data.columns:
        asset_data = price_data[ticker].dropna()
        
        if len(asset_data) > 0:
            initial_price = asset_data.iloc[0]
            final_price = asset_data.iloc[-1]
            returns = (final_price/initial_price - 1)
            start_date = asset_data.index[0]
            duration = (asset_data.index[-1] - start_date).days / 365.25
            
            print(f"\n{ticker} ({asset_markets[ticker]}):")
            print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
            print(f"Data Duration: {duration:.1f} years")
            print(f"Initial Price: ${initial_price:.2f}")
            print(f"Final Price: ${final_price:.2f}")
            print(f"Total Return: {returns:.2%}")
            print(f"Annualized Return: {(((1 + returns) ** (1/duration)) - 1):.2%}")
    
    # Calculate returns with proper handling of missing values
    returns_data = price_data.pct_change(fill_method=None)
    returns_data = returns_data.replace([np.inf, -np.inf], np.nan)
    returns_data = returns_data.fillna(0)
    
    if not benchmark_data.empty:
        benchmark_returns = benchmark_data.pct_change(fill_method=None)
        benchmark_returns = benchmark_returns.replace([np.inf, -np.inf], np.nan)
        benchmark_returns = benchmark_returns.fillna(0)
    else:
        benchmark_returns = pd.DataFrame()
    
    # Recalculate rebalancing returns with fixed function
    rebalancing_metrics = {}
    period_names = {'ME': 'Monthly', 'QE': 'Quarterly', 'YE': 'Yearly'}
    
    for period, period_name in period_names.items():
        portfolio_values = rebalance_portfolio(portfolio_weights, price_data, period)
        portfolio_returns = portfolio_values.pct_change(fill_method=None)
        portfolio_returns = portfolio_returns.replace([np.inf, -np.inf], np.nan)
        portfolio_returns = portfolio_returns.fillna(0)
        
        metrics = calculate_risk_metrics(portfolio_returns)
        metrics['Strategy Score'] = calculate_composite_score(metrics)
        rebalancing_metrics[f'Portfolio ({period_name} Rebalancing)'] = metrics
    
    # Add benchmark metrics
    if not benchmark_returns.empty:
        for name, returns in benchmark_returns.items():
            metrics = calculate_risk_metrics(returns)
            metrics['Strategy Score'] = calculate_composite_score(metrics)
            rebalancing_metrics[f'Benchmark ({name})'] = metrics
    
    # Create metrics DataFrame
    metrics_df = pd.DataFrame(rebalancing_metrics).round(4)
    metrics_df = metrics_df.reindex()  # Ensure consistent order
    
    return {
        'metrics': metrics_df,
        'correlation': calculate_correlation_analysis(returns_data, benchmark_returns)[0],
        'risk_contribution': calculate_risk_contribution(returns_data, list(portfolio_weights.values())),
        'returns_data': returns_data,
        'start_dates': asset_start_dates
    }

def calculate_rebalancing_metrics(price_data, portfolio_weights, benchmark_returns):
    """Calculate metrics for different rebalancing periods"""
    all_metrics = {}
    period_names = {'ME': 'Monthly', 'QE': 'Quarterly', 'YE': 'Yearly'}
    
    for period, period_name in period_names.items():
        try:
            portfolio_values = rebalance_portfolio(portfolio_weights, price_data, period)
            returns = portfolio_values.pct_change(fill_method=None)
            returns.fillna(0, inplace=True)
            
            metrics = calculate_risk_metrics(returns)
            metrics['Strategy Score'] = calculate_composite_score(metrics)
            all_metrics[f'Portfolio ({period_name} Rebalancing)'] = metrics
            
        except Exception as e:
            print(f"Error calculating {period_name} rebalancing: {e}")
    
    # Add benchmark metrics if available
    if not benchmark_returns.empty:
        for name, returns in benchmark_returns.items():
            metrics = calculate_risk_metrics(returns)
            metrics['Strategy Score'] = calculate_composite_score(metrics)
            all_metrics[f'Benchmark ({name})'] = metrics
    
    # Create formatted DataFrame
    metrics_df = pd.DataFrame(all_metrics).round(4)
    
    # Order metrics
    display_order = [
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
    metrics_df = metrics_df.reindex(display_order)
    
    # Format display
    display_df = pd.DataFrame(index=metrics_df.index)
    for col in metrics_df.columns:
        formatted_col = []
        for idx in metrics_df.index:
            value = metrics_df.loc[idx, col]
            if idx == 'Strategy Score':
                formatted_col.append(f"{value:.1f}")
            elif idx in ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio']:
                formatted_col.append(f"{value:.2f}")
            else:
                formatted_col.append(f"{value:.2%}")
        display_df[col] = formatted_col
    
    return display_df

def validate_price_data(price_data, min_days=20):
    """Validate price data quality"""
    validation_results = {}
    
    for ticker in price_data.columns:
        data = price_data[ticker].dropna()
        validation_results[ticker] = {
            'data_points': len(data),
            'missing_values': data.isnull().sum(),
            'zero_values': (data == 0).sum(),
            'negative_values': (data < 0).sum(),
            'has_sufficient_data': len(data) >= min_days
        }
    
    return validation_results

def backtest_portfolio(portfolio_weights, use_mutual_dates=False):
    """Backtest portfolio with maximum and mutual date ranges"""
    benchmarks = {
        'VOO': 'S&P500 (USD)',
        'IVV.AX': 'S&P500 (AUD)',
        'IWLD.AX': 'World Index (AUD)'
    }
    
    end_date = pd.to_datetime(datetime.now().strftime('%Y-%m-%d')).tz_localize(None)
    
    # Download and process data
    price_data = pd.DataFrame()
    asset_start_dates = {}
    asset_markets = {}
    
    print("Downloading asset data...")
    for ticker in portfolio_weights.keys():
        try:
            print(f"Downloading {ticker}...")
            asset = yf.download(ticker, start=None, end=end_date, progress=False)
            
            if len(asset) < 20:
                print(f"Warning: Insufficient data for {ticker}")
                continue
                
            valid_data = asset['Adj Close'].dropna()
            if len(valid_data) > 0:
                valid_data.index = valid_data.index.tz_localize(None)
                first_valid_date = valid_data.index[0]
                asset_start_dates[ticker] = first_valid_date
                price_data[ticker] = valid_data
                asset_markets[ticker] = ('ASX' if ticker.endswith('.AX') else
                                      'Crypto' if ticker.endswith('-USD') else 'US')
                    
        except Exception as e:
            print(f"Error downloading {ticker}: {e}")
    
    validation_results = validate_price_data(price_data)
    print("\nData Quality Check:")
    for ticker, results in validation_results.items():
        print(f"\n{ticker}:")
        for metric, value in results.items():
            print(f"  {metric}: {value}")
        
        if not results['has_sufficient_data']:
            print(f"  WARNING: Insufficient data for {ticker}")
    
    # Download benchmark data
    print("\nDownloading benchmark data...")
    benchmark_data = pd.DataFrame()
    for ticker, name in benchmarks.items():
        try:
            benchmark = yf.download(ticker, start=None, end=end_date, progress=False)
            if len(benchmark) > 0:
                benchmark.index = benchmark.index.tz_localize(None)
                benchmark_data[name] = benchmark['Adj Close']
        except Exception as e:
            print(f"Error downloading benchmark {name}: {e}")
    
    if len(price_data.columns) == 0:
        print("No valid data downloaded for any assets.")
        return None
    
    # Calculate metrics for both timeframes
    results = {}
    
    # Maximum date range analysis
    print("\n=== Analysis using maximum date range for each asset ===")
    results['max_range'] = calculate_metrics(
        price_data.copy(),
        benchmark_data.copy(),
        portfolio_weights,
        asset_markets,
        asset_start_dates,
        use_mutual_dates=False
    )
    
    # Mutual date range analysis
    if use_mutual_dates:
        print("\n=== Analysis using mutual date range across all assets ===")
        mutual_start_date = max(asset_start_dates.values())
        mutual_price_data = price_data[mutual_start_date:]
        mutual_benchmark_data = benchmark_data[mutual_start_date:]
        
        results['mutual_range'] = calculate_metrics(
            mutual_price_data,
            mutual_benchmark_data,
            portfolio_weights,
            asset_markets,
            asset_start_dates,
            use_mutual_dates=True
        )
    
    return results

def setup_environment():
    """Setup the environment with configuration settings"""
    # Configure logging
    logging.config.dictConfig(BacktestConfig.LOGGING)
    
    # Configure pandas display settings
    for option, value in BacktestConfig.DISPLAY_OPTIONS.items():
        pd.set_option(option, value)

def main():
    """Main execution function"""
    setup_environment()
    logger = logging.getLogger(__name__)
    
    try:
        BacktestConfig.validate_portfolio()
        
        logger.info("Starting dual timeframe portfolio backtest...")
        results = backtest_portfolio(
            portfolio_weights=BacktestConfig.PORTFOLIO,
            use_mutual_dates=True
        )
        
        if results:
            for timeframe, result in results.items():
                print(f"\n=== Results for {timeframe.replace('_', ' ').title()} ===")
                print("\nPerformance Comparison:")
                print(result['metrics'])
                
                print("\nCorrelation Matrix:")
                print(result['correlation'].round(3))
                
                print("\nRisk Contribution Analysis (% of portfolio risk):")
                print(result['risk_contribution'].round(4).mul(100)
                      .apply(lambda x: f"{x:.1f}%")
                      .to_frame('Risk Contribution'))
        
        logger.info("Backtest completed successfully")
            
    except Exception as e:
        logger.error(f"An error occurred during backtest: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()