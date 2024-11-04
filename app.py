from flask import Flask, render_template
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from main import backtest_portfolio, BacktestConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def create_performance_chart(results):
    """Create main performance chart with benchmarks"""
    returns_data = results['returns_data']
    cum_returns = (1 + returns_data).cumprod()
    
    fig = go.Figure()
    
    # Portfolio strategies first
    strategy_cols = [col for col in cum_returns.columns if 'Portfolio' in col]
    benchmark_cols = [col for col in cum_returns.columns if 'Benchmark' in col]
    
    # Add strategy lines
    for col in strategy_cols:
        fig.add_trace(
            go.Scatter(x=cum_returns.index, 
                      y=cum_returns[col], 
                      name=col,
                      line=dict(width=2))
        )
    
    # Add benchmark lines
    for col in benchmark_cols:
        fig.add_trace(
            go.Scatter(x=cum_returns.index, 
                      y=cum_returns[col], 
                      name=col,
                      line=dict(dash='dash'))
        )
    
    fig.update_layout(
        title='Portfolio Performance vs Benchmarks',
        xaxis_title='Date',
        yaxis_title='Growth of $1',
        height=600
    )
    
    return fig.to_json()

def create_drawdown_chart(results):
    """Create drawdown comparison chart"""
    returns_data = results['returns_data']
    cum_returns = (1 + returns_data).cumprod()
    drawdowns = cum_returns / cum_returns.cummax() - 1
    
    fig = go.Figure()
    
    for col in drawdowns.columns:
        fig.add_trace(
            go.Scatter(x=drawdowns.index,
                      y=drawdowns[col],
                      name=col,
                      fill='tonexty' if 'Portfolio' in col else None)
        )
    
    fig.update_layout(
        title='Drawdown Analysis',
        xaxis_title='Date',
        yaxis_title='Drawdown',
        height=400
    )
    
    return fig.to_json()

def create_risk_metrics_chart(results):
    """Create risk metrics visualization"""
    metrics_df = results['metrics']
    
    # Create subplots for different risk metrics
    fig = make_subplots(rows=2, cols=2,
                       subplot_titles=('Volatility', 'Sharpe Ratio', 
                                     'Max Drawdown', 'Win Rate'))
    
    strategies = metrics_df.columns
    
    # Volatility
    fig.add_trace(
        go.Bar(x=strategies, y=metrics_df.loc['Volatility'],
               name='Volatility'),
        row=1, col=1
    )
    
    # Sharpe Ratio
    fig.add_trace(
        go.Bar(x=strategies, y=metrics_df.loc['Sharpe Ratio'],
               name='Sharpe Ratio'),
        row=1, col=2
    )
    
    # Max Drawdown
    fig.add_trace(
        go.Bar(x=strategies, y=metrics_df.loc['Max Drawdown'],
               name='Max Drawdown'),
        row=2, col=1
    )
    
    # Win Rate
    fig.add_trace(
        go.Bar(x=strategies, y=metrics_df.loc['Win Rate'],
               name='Win Rate'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    
    return fig.to_json()

def create_correlation_heatmap(results):
    """Create correlation heatmap"""
    corr_matrix = results['correlation']
    
    fig = px.imshow(
        corr_matrix,
        labels=dict(x="Asset", y="Asset", color="Correlation"),
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        color_continuous_scale='RdBu'
    )
    
    fig.update_layout(
        title='Asset Correlation Heatmap',
        height=600
    )
    
    return fig.to_json()

@app.route('/')
def index():
    """Main dashboard route"""
    try:
        logger.info("Starting backtest...")
        results = backtest_portfolio(BacktestConfig.PORTFOLIO, use_mutual_dates=True)
        logger.info("Backtest completed")
        
        if 'mutual_range' in results:
            charts = {
                'performance': create_performance_chart(results['mutual_range']),
                'drawdown': create_drawdown_chart(results['mutual_range']),
                'risk_metrics': create_risk_metrics_chart(results['mutual_range']),
                'correlation': create_correlation_heatmap(results['mutual_range'])
            }
            
            metrics = results['mutual_range']['metrics']
            
            logger.info("Rendering template...")
            return render_template('dashboard.html', 
                                charts=charts,
                                metrics=metrics.to_dict())
        else:
            return "Error: No results data available"
            
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)