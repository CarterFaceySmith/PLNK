import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import requests
import json
from datetime import datetime
import threading
from decimal import Decimal
import pandas as pd
import os

class PortfolioRebalancer:
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Rebalancer")
        self.root.geometry("1200x800")
        
        # Default portfolio data
        self.default_portfolio = {
            # ETFs (75%)
            'VOO': {'target': 25, 'units': 0, 'price': 0},
            'VOOG': {'target': 15, 'units': 0, 'price': 0},
            'VAS.AX': {'target': 15, 'units': 0, 'price': 0},
            'ITA': {'target': 10, 'units': 0, 'price': 0},
            'NLR': {'target': 5, 'units': 0, 'price': 0},
            'DTCR': {'target': 5, 'units': 0, 'price': 0},
            # Crypto (25%)
            'BTC': {'target': 15, 'units': 0, 'price': 0},
            'SOL': {'target': 10, 'units': 0, 'price': 0},
            # Special rows (not counted in allocation)
            'DEPOSIT': {'target': 0, 'units': 0, 'price': 1},
            'WITHDRAW': {'target': 0, 'units': 0, 'price': 1}
        }
        
        # Load saved data or use defaults
        self.portfolio = self.load_portfolio()
        
        self.create_gui()
        # Fetch prices automatically on startup
        self.root.after(1000, self.fetch_prices_threaded)
        
    def save_portfolio(self):
        """Save portfolio data to JSON file"""
        try:
            with open('portfolio_data.json', 'w') as f:
                json.dump(self.portfolio, f)
            self.status_label.config(text="Portfolio saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save portfolio: {e}")

    def load_portfolio(self):
        """Load portfolio data from JSON file"""
        try:
            if os.path.exists('portfolio_data.json'):
                with open('portfolio_data.json', 'r') as f:
                    data = json.load(f)
                # Ensure all expected keys exist
                for key in self.default_portfolio:
                    if key not in data:
                        data[key] = self.default_portfolio[key]
                return data
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to load portfolio: {e}\nUsing defaults.")
        return self.default_portfolio.copy()
        
    def create_gui(self):
        # Top frame for buttons and status
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # Buttons frame
        buttons_frame = ttk.Frame(top_frame)
        buttons_frame.pack(side=tk.LEFT)
        
        # Fetch prices button
        fetch_button = ttk.Button(
            buttons_frame, 
            text="Refresh Prices",
            command=self.fetch_prices_threaded
        )
        fetch_button.pack(side=tk.LEFT, padx=5)
        
        # Save button
        save_button = ttk.Button(
            buttons_frame,
            text="Save Portfolio",
            command=self.save_portfolio
        )
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(top_frame, text="")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            top_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(side=tk.LEFT, padx=5)
        
        # Create table
        columns = ('Asset', 'Units', 'Price', 'Value', 'Current %', 'Target %', 'To Trade')
        self.tree = ttk.Treeview(
            self.root,
            columns=columns,
            show='headings',
            padding="10"
        )
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        # Bind double-click event for editing
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Initial table population
        self.update_table()

    def on_double_click(self, event):
        """Handle double-click on table cell"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            # Allow editing of Units, Price, and Target % columns
            if column in ("#2", "#3", "#6"):  # Units, Price, Target %
                self.edit_cell(item, column)

    def edit_cell(self, item, column):
        """Create entry widget for editing cell"""
        x, y, w, h = self.tree.bbox(item, column)
        
        # Get current value and field type
        asset = self.tree.item(item)['values'][0]
        field_map = {
            "#2": ("units", "Units"),
            "#3": ("price", "Price"),
            "#6": ("target", "Target %")
        }
        
        field, field_name = field_map[column]
        current_value = self.portfolio[asset][field]
        
        # Create entry widget
        entry = ttk.Entry(self.tree, width=20)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def on_enter(event):
            try:
                new_value = float(entry.get())
                if field == "target" and asset != "DEPOSIT":
                    # Validate target percentage
                    total_target = sum(data['target'] for sym, data in self.portfolio.items() 
                                    if sym != asset and sym != "DEPOSIT") + new_value
                    if total_target != 100:
                        messagebox.showwarning(
                            "Warning", 
                            f"Total allocation would be {total_target}%. Should total 100%."
                        )
                self.portfolio[asset][field] = new_value
                self.update_table()
            except ValueError:
                messagebox.showerror("Error", f"Please enter a valid number for {field_name}")
            finally:
                entry.destroy()
        
        entry.bind('<Return>', on_enter)
        entry.bind('<FocusOut>', lambda e: entry.destroy())

    def fetch_prices_threaded(self):
        """Start price fetching in a separate thread"""
        self.progress.start()
        self.status_label.config(text="Fetching prices...")
        thread = threading.Thread(target=self.fetch_prices)
        thread.daemon = True
        thread.start()

    def fetch_individual_ticker(self, symbol):
        """Fetch price for a single ticker"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('regularMarketPrice')
            if price:
                self.portfolio[symbol]['price'] = price
            else:
                # Try to get price from history if info doesn't work
                history = ticker.history(period="1d")
                if not history.empty:
                    price = history['Close'].iloc[-1]
                    self.portfolio[symbol]['price'] = price
                else:
                    print(f"No price data available for {symbol}")
                    self.root.after(0, lambda s=symbol: self.status_label.config(
                        text=f"No price data for {s}"
                    ))
        except Exception as e:
            print(f"Error fetching individual ticker {symbol}: {e}")
            self.root.after(0, lambda s=symbol: self.status_label.config(
                text=f"Failed to fetch {s}"
            ))

    def fetch_prices(self):
        """Fetch prices from APIs"""
        try:
            # Fetch stock prices using yfinance
            stock_symbols = [symbol for symbol in self.portfolio.keys() 
                           if symbol not in ['BTC', 'SOL', 'DEPOSIT', 'WITHDRAW']]
            
            # Split symbols into groups based on exchange
            nasdaq_symbols = ['DTCR']  # NASDAQ symbols
            other_symbols = [s for s in stock_symbols if s not in nasdaq_symbols]
            
            # Download non-NASDAQ symbols in batch
            if other_symbols:
                try:
                    stock_data = yf.download(other_symbols, period="1d", group_by='ticker')
                    
                    for symbol in other_symbols:
                        try:
                            if len(other_symbols) == 1:
                                price = stock_data['Close'].iloc[-1]
                            else:
                                price = stock_data[symbol]['Close'].iloc[-1]
                            if pd.notna(price):
                                self.portfolio[symbol]['price'] = price
                            else:
                                self.fetch_individual_ticker(symbol)
                        except Exception as e:
                            print(f"Error in batch download for {symbol}: {e}")
                            self.fetch_individual_ticker(symbol)
                except Exception as e:
                    print(f"Batch download failed: {e}")
                    for symbol in other_symbols:
                        self.fetch_individual_ticker(symbol)
            
            # Handle NASDAQ symbols individually
            for symbol in nasdaq_symbols:
                self.fetch_individual_ticker(symbol)
            
            # Fetch crypto prices from CoinSpot
            try:
                coinspot_response = requests.get('https://www.coinspot.com.au/pubapi/v2/latest')
                if coinspot_response.status_code == 200:
                    crypto_data = coinspot_response.json()
                    self.portfolio['BTC']['price'] = float(crypto_data['prices']['btc']['last'])
                    self.portfolio['SOL']['price'] = float(crypto_data['prices']['sol']['last'])
            except Exception as e:
                print(f"Error fetching crypto prices: {e}")
                self.root.after(0, lambda: self.status_label.config(
                    text="Failed to fetch crypto prices"
                ))
            
            # Update UI in main thread
            self.root.after(0, self.update_table)
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.status_label.config(
                text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
            ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch prices: {e}"))
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.status_label.config(text="Error fetching prices"))

    def calculate_rebalancing(self):
        """Calculate rebalancing requirements"""
        # Calculate total portfolio value excluding deposit and withdraw
        total_value = sum(data['units'] * data['price'] 
                         for symbol, data in self.portfolio.items() 
                         if symbol not in ['DEPOSIT', 'WITHDRAW'])
        
        # Calculate net deposit/withdrawal
        deposit = self.portfolio['DEPOSIT']['units']
        withdrawal = self.portfolio['WITHDRAW']['units']
        net_change = deposit - withdrawal
        
        if net_change < 0 and abs(net_change) > total_value:
            messagebox.showerror("Error", "Withdrawal amount exceeds portfolio value!")
            self.portfolio['WITHDRAW']['units'] = total_value  # Cap withdrawal at total value
            net_change = -total_value
        
        total_with_changes = total_value + net_change
        
        results = []
        for symbol, data in self.portfolio.items():
            current_value = data['units'] * data['price']
            
            # Handle special rows differently
            if symbol in ['DEPOSIT', 'WITHDRAW']:
                current_percent = 0
                target_value = 0
                units_to_trade = 0
            else:
                current_percent = (current_value / total_value * 100) if total_value > 0 else 0
                target_value = total_with_changes * (data['target'] / 100)
                difference = target_value - current_value
                units_to_trade = difference / data['price'] if data['price'] else 0
            
            results.append({
                'symbol': symbol,
                'units': data['units'],
                'price': data['price'],
                'current_value': current_value,
                'current_percent': current_percent,
                'target_percent': data['target'],
                'units_to_trade': units_to_trade
            })
        
        return results

    def update_table(self):
        """Update the table with current portfolio data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate rebalancing
        rebalancing = self.calculate_rebalancing()
        
        # Update table
        for data in rebalancing:
            if data['symbol'] in ['DEPOSIT', 'WITHDRAW']:
                trade_text = '-'
            else:
                trade_text = (f"Buy {abs(data['units_to_trade']):.4f}" 
                            if data['units_to_trade'] > 0
                            else f"Sell {abs(data['units_to_trade']):.4f}")
            
            values = (
                data['symbol'],
                f"{data['units']:.4f}",
                f"${data['price']:.2f}",
                f"${data['current_value']:.2f}",
                f"{data['current_percent']:.1f}%",
                f"{data['target_percent']}%",
                trade_text
            )
            
            # Add row with appropriate tags for coloring
            tags = ()
            if data['units_to_trade'] > 0 and data['symbol'] not in ['DEPOSIT', 'WITHDRAW']:
                tags = ('buy',)
            elif data['units_to_trade'] < 0 and data['symbol'] not in ['DEPOSIT', 'WITHDRAW']:
                tags = ('sell',)
            elif data['symbol'] == 'WITHDRAW':
                tags = ('withdraw',)
            
            self.tree.insert('', tk.END, values=values, tags=tags)
        
        # Configure tag colors
        self.tree.tag_configure('buy', foreground='green')
        self.tree.tag_configure('sell', foreground='red')
        self.tree.tag_configure('withdraw', foreground='purple')

if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioRebalancer(root)
    root.mainloop()