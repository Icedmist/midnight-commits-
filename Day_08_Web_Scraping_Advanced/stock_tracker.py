"""
Stock Price Tracker
Track and analyze stock prices in real-time
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockTracker:
    """Track stock prices using free APIs"""

    def __init__(self, symbols: List[str] = None):
        """Initialize tracker with stock symbols"""
        self.symbols = symbols or []
        self.prices = {}
        self.history = {}

    def add_symbol(self, symbol: str) -> None:
        """Add stock symbol to track"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.history[symbol] = []
            logger.info(f"✅ Added {symbol}")

    def fetch_price(self, symbol: str) -> Optional[Dict]:
        """Fetch current price using Alpha Vantage or similar"""
        try:
            # Using yfinance as alternative (no API key needed)
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            
            if not data.empty:
                latest = data.iloc[-1]
                price_data = {
                    'symbol': symbol,
                    'price': latest['Close'],
                    'high': latest['High'],
                    'low': latest['Low'],
                    'volume': latest['Volume'],
                    'timestamp': datetime.now().isoformat()
                }
                self.prices[symbol] = price_data
                self.history[symbol].append(price_data)
                logger.info(f"✅ {symbol}: ${latest['Close']:.2f}")
                return price_data
        except Exception as e:
            logger.error(f"❌ Error fetching {symbol}: {e}")
        return None

    def get_price_change(self, symbol: str, period: str = "1d") -> Optional[Dict]:
        """Get price change over period"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if len(data) > 1:
                open_price = data.iloc[0]['Close']
                close_price = data.iloc[-1]['Close']
                change = close_price - open_price
                change_pct = (change / open_price) * 100
                
                return {
                    'symbol': symbol,
                    'period': period,
                    'open': open_price,
                    'close': close_price,
                    'change': change,
                    'change_pct': change_pct
                }
        except Exception as e:
            logger.error(f"❌ Error calculating change: {e}")
        return None

    def get_moving_average(self, symbol: str, period: int = 20) -> Optional[float]:
        """Calculate moving average"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{period+5}d")
            
            if len(data) >= period:
                ma = data['Close'].tail(period).mean()
                return ma
        except Exception as e:
            logger.error(f"❌ Error calculating MA: {e}")
        return None

    def get_volatility(self, symbol: str, period: int = 20) -> Optional[float]:
        """Calculate volatility"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{period+5}d")
            
            if len(data) >= period:
                returns = data['Close'].pct_change()
                volatility = returns.std() * 100
                return volatility
        except Exception as e:
            logger.error(f"❌ Error calculating volatility: {e}")
        return None

    def format_price(self, symbol: str) -> str:
        """Format price data for display"""
        if symbol not in self.prices:
            return f"{symbol}: No data"
        
        data = self.prices[symbol]
        price = data['price']
        high = data['high']
        low = data['low']
        
        return f"""
📈 {symbol}
💰 Price: ${price:.2f}
📊 High: ${high:.2f} | Low: ${low:.2f}
⏰ Updated: {data['timestamp']}
"""

    def watch_symbols(self, refresh_interval: int = 60) -> None:
        """Continuously watch symbols"""
        import time
        
        print(f"\n🔍 Watching {len(self.symbols)} symbols...\n")
        
        while True:
            for symbol in self.symbols:
                self.fetch_price(symbol)
                change = self.get_price_change(symbol, "1d")
                
                if change:
                    direction = "📈" if change['change_pct'] > 0 else "📉"
                    print(f"{direction} {symbol}: {change['change_pct']:+.2f}%")
            
            print(f"\n⏸️  Next update in {refresh_interval}s...\n")
            time.sleep(refresh_interval)

    def portfolio_summary(self) -> str:
        """Show portfolio summary"""
        if not self.prices:
            return "No stocks tracked"
        
        summary = "📊 Portfolio Summary\n"
        summary += "-" * 40 + "\n"
        
        for symbol, data in self.prices.items():
            summary += f"{symbol}: ${data['price']:.2f}\n"
        
        return summary


def demo_tracker():
    """Demo stock tracker"""
    tracker = StockTracker()
    
    # Add some popular stocks
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
    
    for symbol in symbols:
        tracker.add_symbol(symbol)
    
    # Fetch current prices
    print("\n💹 Fetching stock prices...\n")
    for symbol in symbols:
        tracker.fetch_price(symbol)
    
    # Show portfolio
    print(tracker.portfolio_summary())
    
    # Show analysis
    print("\n📊 Stock Analysis:")
    for symbol in symbols[:2]:
        change = tracker.get_price_change(symbol)
        if change:
            print(f"{symbol}: {change['change_pct']:+.2f}%")


if __name__ == "__main__":
    print("📈 Stock Price Tracker\n")
    
    print("Setup:")
    print("pip install yfinance requests")
    print("\nFeatures:")
    print("✓ Real-time stock prices")
    print("✓ Price change tracking")
    print("✓ Moving averages")
    print("✓ Volatility calculation")
    print("✓ Portfolio management")
