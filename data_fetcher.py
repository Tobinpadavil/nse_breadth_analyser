"""
Data fetching module using Yahoo Finance
Handles special symbol formats and robust error handling
"""

import yfinance as yf
import pandas as pd
import time
from datetime import datetime
from config import FNO_STOCKS, Display

class DataFetcher:
    """Fetch market data for F&O stocks"""
    
    def __init__(self, stock_list=None):
        self.stock_list = stock_list if stock_list else FNO_STOCKS
        self.data = None
        self.failed_stocks = []
        
    def _convert_to_yahoo_format(self, symbol):
        """
        Convert NSE symbol to Yahoo Finance format
        Handles special cases and formats
        """
        # Special symbol mappings for Yahoo Finance
        special_formats = {
            "360ONE": "360ONE.NS",
            "M&M": "M&M.NS",
            "BAJAJ-AUTO": "BAJAJ-AUTO.NS",
            "M_M": "M&M.NS",  # Alternative format
            "^INDIAVIX": "^INDIAVIX",  # India VIX - no suffix
        }
        
        # Check if special format exists
        if symbol in special_formats:
            return special_formats[symbol]
        
        # Handle VIX and index symbols (start with ^)
        if symbol.startswith("^"):
            return symbol
        
        # Handle symbols that might have different Yahoo formats
        # Most NSE stocks use .NS suffix
        return f"{symbol}.NS"
    
    def fetch_quote(self, symbol):
        """
        Fetch quote for a single symbol
        Returns dict with price, change, volume data or None if failed
        """
        try:
            # Convert to Yahoo Finance format
            yahoo_symbol = self._convert_to_yahoo_format(symbol)
            
            # Create ticker object
            ticker = yf.Ticker(yahoo_symbol)
            
            # Get recent history (5 days to ensure we have data)
            hist = ticker.history(period="5d")
            
            # Check if we have sufficient data
            if hist.empty or len(hist) < 2:
                return None
            
            # Extract latest and previous close
            current_price = hist['Close'].iloc[-1]
            prev_close = hist['Close'].iloc[-2]
            current_volume = hist['Volume'].iloc[-1]
            
            # Calculate average volume from available data
            avg_volume = hist['Volume'].mean()
            
            # Validate data
            if pd.isna(current_price) or pd.isna(prev_close) or current_price <= 0 or prev_close <= 0:
                return None
            
            # Calculate percentage change
            pct_change = ((current_price - prev_close) / prev_close) * 100
            
            # Calculate volume ratio
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # Return data dictionary
            return {
                'symbol': symbol,  # Original NSE symbol
                'price': round(float(current_price), 2),
                'prev_close': round(float(prev_close), 2),
                'pct_change': round(float(pct_change), 2),
                'volume': int(current_volume) if not pd.isna(current_volume) else 0,
                'avg_volume': int(avg_volume) if not pd.isna(avg_volume) else 0,
                'volume_ratio': round(float(volume_ratio), 2)
            }
            
        except Exception as e:
            # Return None on any error
            return None
    
    def fetch_all(self, show_progress=True):
        """
        Fetch data for all stocks in the list
        Returns: (DataFrame, list of failed stocks)
        """
        results = []
        self.failed_stocks = []
        total = len(self.stock_list)
        
        if show_progress:
            print(f"\n⏳ Fetching data for {total} stocks...")
            print(f"⏱️  Estimated time: ~{total * 0.3 / 60:.1f} minutes")
            print(f"💡 Please be patient...\n")
        
        # Fetch data for each stock
        for i, symbol in enumerate(self.stock_list):
            quote = self.fetch_quote(symbol)
            
            if quote:
                results.append(quote)
            else:
                self.failed_stocks.append(symbol)
            
            # Progress update
            if show_progress and (i + 1) % Display.PROGRESS_UPDATE_FREQUENCY == 0:
                success_rate = len(results) / (i + 1) * 100
                print(f"   ✓ Progress: {i + 1}/{total} ({(i+1)/total*100:.0f}%) | "
                      f"Success: {success_rate:.0f}%")
            
            # Rate limiting to avoid overwhelming Yahoo Finance
            # 0.2 seconds = 5 requests per second (safe rate)
            time.sleep(0.2)
        
        # Convert results to DataFrame
        self.data = pd.DataFrame(results)
        
        # Print summary
        if show_progress:
            print(f"\n{'='*Display.CONSOLE_WIDTH}")
            print(f"✅ Data fetch complete!")
            print(f"   • Successfully fetched: {len(results)} stocks")
            if self.failed_stocks:
                print(f"   • Failed: {len(self.failed_stocks)} stocks")
                if len(self.failed_stocks) <= 10:
                    print(f"   • Failed stocks: {', '.join(self.failed_stocks)}")
                else:
                    print(f"   • First 10 failed: {', '.join(self.failed_stocks[:10])}...")
            print(f"{'='*Display.CONSOLE_WIDTH}\n")
        
        return self.data, self.failed_stocks
    
    def retry_failed_stocks(self, max_retries=2):
        """
        Retry fetching failed stocks
        Useful if some stocks failed due to temporary network issues
        """
        if not self.failed_stocks:
            print("✅ No failed stocks to retry")
            return self.data, []
        
        print(f"\n🔄 Retrying {len(self.failed_stocks)} failed stocks...")
        
        retry_results = []
        still_failed = []
        
        for attempt in range(max_retries):
            print(f"\n   Attempt {attempt + 1}/{max_retries}...")
            
            for symbol in self.failed_stocks:
                quote = self.fetch_quote(symbol)
                
                if quote:
                    retry_results.append(quote)
                    print(f"      ✅ {symbol} - Success!")
                else:
                    if attempt == max_retries - 1:  # Last attempt
                        still_failed.append(symbol)
                
                time.sleep(0.3)  # Slightly longer delay for retries
            
            # Update failed list for next attempt
            self.failed_stocks = [s for s in self.failed_stocks if s not in [r['symbol'] for r in retry_results]]
            
            if not self.failed_stocks:
                break
        
        # Append retry results to main data
        if retry_results:
            retry_df = pd.DataFrame(retry_results)
            self.data = pd.concat([self.data, retry_df], ignore_index=True)
        
        self.failed_stocks = still_failed
        
        print(f"\n   ✅ Recovered: {len(retry_results)} stocks")
        if still_failed:
            print(f"   ❌ Still failed: {len(still_failed)} stocks")
        
        return self.data, self.failed_stocks
    
    def get_dataframe(self):
        """Return the fetched data as DataFrame"""
        return self.data
    
    def get_failed_stocks(self):
        """Return list of stocks that failed to fetch"""
        return self.failed_stocks
    
    def export_failed_stocks(self, filename="failed_stocks.txt"):
        """Export failed stocks list to a text file"""
        if not self.failed_stocks:
            print("✅ No failed stocks to export")
            return
        
        with open(filename, 'w') as f:
            f.write("Failed to fetch data for the following stocks:\n")
            f.write("="*50 + "\n\n")
            for stock in self.failed_stocks:
                f.write(f"{stock}\n")
            f.write(f"\nTotal failed: {len(self.failed_stocks)}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"📁 Failed stocks list saved to: {filename}")
    
    def get_fetch_statistics(self):
        """Get statistics about the fetch operation"""
        total_attempted = len(self.stock_list)
        successful = len(self.data) if self.data is not None else 0
        failed = len(self.failed_stocks)
        success_rate = (successful / total_attempted * 100) if total_attempted > 0 else 0
        
        return {
            'total_attempted': total_attempted,
            'successful': successful,
            'failed': failed,
            'success_rate': round(success_rate, 1)
        }


# ============================================
# UTILITY FUNCTIONS
# ============================================

def test_single_stock(symbol):
    """
    Test fetching data for a single stock
    Useful for debugging symbol issues
    """
    print(f"\n🧪 Testing data fetch for: {symbol}")
    print("="*50)
    
    fetcher = DataFetcher(stock_list=[symbol])
    quote = fetcher.fetch_quote(symbol)
    
    if quote:
        print(f"\n✅ Success!")
        print(f"   Symbol: {quote['symbol']}")
        print(f"   Price: ₹{quote['price']}")
        print(f"   Change: {quote['pct_change']:+.2f}%")
        print(f"   Volume: {quote['volume']:,}")
        print(f"   Volume Ratio: {quote['volume_ratio']:.2f}x")
    else:
        print(f"\n❌ Failed to fetch data for {symbol}")
        print(f"\nPossible reasons:")
        print(f"   • Symbol not found on Yahoo Finance")
        print(f"   • Stock suspended or delisted")
        print(f"   • Insufficient trading history")
        print(f"   • Network/API issue")
    
    print("="*50)
    return quote


def test_multiple_stocks(symbols, show_details=True):
    """
    Test fetching data for multiple stocks
    """
    print(f"\n🧪 Testing data fetch for {len(symbols)} stocks...")
    print("="*50)
    
    fetcher = DataFetcher(stock_list=symbols)
    df, failed = fetcher.fetch_all(show_progress=False)
    
    if show_details and not df.empty:
        print("\n✅ Successfully fetched stocks:")
        for _, row in df.iterrows():
            print(f"   {row['symbol']:15s} | ₹{row['price']:8.2f} | {row['pct_change']:+6.2f}%")
    
    if failed:
        print(f"\n❌ Failed stocks ({len(failed)}):")
        for stock in failed:
            print(f"   • {stock}")
    
    stats = fetcher.get_fetch_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    print(f"   ({stats['successful']}/{stats['total_attempted']} stocks)")
    print("="*50)
    
    return df, failed


# ============================================
# MAIN TEST FUNCTION
# ============================================

def main():
    """Test the data fetcher"""
    print("="*80)
    print("🧪 DATA FETCHER TEST")
    print("="*80)
    
    # Test with first 10 stocks
    from config import FNO_STOCKS
    test_stocks = FNO_STOCKS[:10]
    
    print(f"\nTesting with {len(test_stocks)} sample stocks:")
    print(f"{', '.join(test_stocks)}")
    
    test_multiple_stocks(test_stocks, show_details=True)


if __name__ == "__main__":
    main()