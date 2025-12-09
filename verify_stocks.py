"""
Verify stock list and test data fetching
"""

from config import FNO_STOCKS, SECTORS
from data_fetcher import DataFetcher

def verify_configuration():
    """Verify stock list configuration"""
    
    print("="*80)
    print("🔍 STOCK LIST VERIFICATION")
    print("="*80)
    
    # Basic counts
    print(f"\n📊 Stock Statistics:")
    print(f"   Total stocks configured: {len(FNO_STOCKS)}")
    print(f"   Total sectors: {len(SECTORS)}")
    
    # Sector breakdown
    print(f"\n🏭 Sector Breakdown:")
    for sector, stocks in sorted(SECTORS.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {sector:30s}: {len(stocks):3d} stocks")
    
    # Find unassigned stocks
    all_sector_stocks = set()
    for stocks in SECTORS.values():
        all_sector_stocks.update(stocks)
    
    unassigned = set(FNO_STOCKS) - all_sector_stocks
    if unassigned:
        print(f"\n⚠️  Unassigned Stocks ({len(unassigned)}):")
        for stock in sorted(unassigned):
            print(f"      • {stock}")
    else:
        print(f"\n✅ All stocks properly assigned to sectors")
    
    # Check for duplicates
    duplicates = [stock for stock in FNO_STOCKS if FNO_STOCKS.count(stock) > 1]
    if duplicates:
        print(f"\n⚠️  Duplicate stocks found: {set(duplicates)}")
    else:
        print(f"✅ No duplicate stocks")

def test_data_fetching(sample_size=10):
    """Test fetching data for sample stocks"""
    
    print("\n" + "="*80)
    print("🧪 DATA FETCH TEST")
    print("="*80)
    
    print(f"\n⏳ Testing data fetch for {sample_size} sample stocks...\n")
    
    # Test with first N stocks
    test_stocks = FNO_STOCKS[:sample_size]
    
    fetcher = DataFetcher(stock_list=test_stocks)
    
    success = 0
    failed = []
    
    for stock in test_stocks:
        quote = fetcher.fetch_quote(stock)
        if quote:
            print(f"   ✅ {stock:15s} | Price: ₹{quote['price']:8.2f} | "
                  f"Change: {quote['pct_change']:+6.2f}%")
            success += 1
        else:
            print(f"   ❌ {stock:15s} | Failed to fetch")
            failed.append(stock)
    
    print(f"\n{'='*80}")
    print(f"📊 Test Results:")
    print(f"   Success: {success}/{sample_size} ({success/sample_size*100:.0f}%)")
    if failed:
        print(f"   Failed: {', '.join(failed)}")
    print(f"{'='*80}\n")

def main():
    """Main verification function"""
    verify_configuration()
    
    # Ask if user wants to test data fetching
    response = input("\n🧪 Test data fetching for 10 sample stocks? (y/n): ").strip().lower()
    if response == 'y':
        test_data_fetching(sample_size=10)
    
    print("\n✅ Verification complete!\n")

if __name__ == "__main__":
    main()