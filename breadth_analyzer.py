"""
NSE F&O Breadth Thrust Analyzer - Main Script
Complete market breadth analysis system
"""

import sys
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime
from config import Display
from data_fetcher import DataFetcher
from analysis import BreadthAnalyzer, HistoryManager
from reporting import ReportGenerator

def check_dependencies():
    """Check if all required libraries are installed"""
    missing = []
    
    try:
        import yfinance
    except ImportError:
        missing.append('yfinance')
    
    try:
        import pandas
    except ImportError:
        missing.append('pandas')
    
    try:
        import numpy
    except ImportError:
        missing.append('numpy')
    
    try:
        import tabulate
    except ImportError:
        missing.append('tabulate')
    
    if missing:
        print("\n❌ Missing required libraries!")
        print(f"\nPlease install: {', '.join(missing)}")
        print("\nRun this command:")
        print(f"   pip install {' '.join(missing)}")
        sys.exit(1)

def main():
    """Main execution function"""
    
    print("="*Display.CONSOLE_WIDTH)
    print("🚀 NSE F&O BREADTH THRUST ANALYZER")
    print("="*Display.CONSOLE_WIDTH)
    
    # Check dependencies
    check_dependencies()
    print("✅ All dependencies found")
    
    try:
        # ============================================
        # STEP 1: DATA COLLECTION
        # ============================================
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("📊 STEP 1: FETCHING MARKET DATA")
        print("="*Display.CONSOLE_WIDTH)
        
        fetcher = DataFetcher()
        df, failed = fetcher.fetch_all(show_progress=True)
        
        if df.empty:
            print("\n❌ No data fetched. Possible reasons:")
            print("   • No internet connection")
            print("   • Market is closed")
            print("   • Yahoo Finance API issue")
            print("\nPlease check and try again.")
            return
        
        # ============================================
        # STEP 2: BREADTH ANALYSIS
        # ============================================
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("🔍 STEP 2: ANALYZING MARKET BREADTH")
        print("="*Display.CONSOLE_WIDTH)
        
        analyzer = BreadthAnalyzer(df)
        
        # Classify stocks
        print("\n   • Classifying stocks...")
        analyzer.classify_stocks()
        
        # Calculate breadth score
        print("   • Calculating breadth score...")
        breadth_data = analyzer.calculate_breadth_score()
        
        # Sector analysis
        print("   • Analyzing sector breadth...")
        sector_data = analyzer.calculate_sector_breadth()
        
        # Magnitude analysis
        print("   • Performing magnitude analysis...")
        magnitude_data = analyzer.calculate_magnitude_analysis()
        
        # Classify regime
        print("   • Classifying market regime...")
        regime, action = analyzer.classify_regime()
        
        # Get top movers
        print("   • Identifying top movers...")
        top_gainers, top_losers = analyzer.get_top_movers(Display.TOP_MOVERS_COUNT)
        
        # Get sector leaders/laggards
        print("   • Finding sector leaders/laggards...")
        leaders, laggards = analyzer.get_sector_leaders_laggards()
        
        print("\n✅ Analysis complete!")
        
        # ============================================
        # STEP 3: HISTORICAL ANALYSIS
        # ============================================
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("📈 STEP 3: HISTORICAL TREND ANALYSIS")
        print("="*Display.CONSOLE_WIDTH)
        
        history_mgr = HistoryManager()
        
        # Get moving average
        moving_avg = history_mgr.get_moving_average()
        if moving_avg:
            print(f"   • 3-day moving average: {moving_avg:+.3f}")
        else:
            print("   • Insufficient historical data (need 3 days)")
        
        # Get trend
        trend = history_mgr.get_trend()
        print(f"   • 5-day trend: {trend}")
        
        # Check divergence
        divergence_type, divergence_msg = history_mgr.detect_divergence(breadth_data['score'])
        if divergence_type:
            print(f"   • {divergence_msg}")
        else:
            print(f"   • No divergence detected")
        
        # Save today's score
        history_mgr.save_score(datetime.now(), breadth_data['score'], regime)
        print("   • Today's score saved to history")
        
        # ============================================
        # STEP 4: GENERATE REPORTS
        # ============================================
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("📄 STEP 4: GENERATING REPORTS")
        print("="*Display.CONSOLE_WIDTH)
        
        # Console report
        ReportGenerator.print_header()
        ReportGenerator.print_breadth_summary(breadth_data, regime, action, moving_avg, trend)
        
        if divergence_type:
            print(f"\n⚠️  DIVERGENCE ALERT:")
            print(f"   {divergence_msg}")
        
        ReportGenerator.print_sector_analysis(sector_data)
        ReportGenerator.print_magnitude_analysis(magnitude_data)
        ReportGenerator.print_top_movers(top_gainers, top_losers)
        ReportGenerator.print_sector_focus(leaders, laggards)
        
        # Save files
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("💾 SAVING REPORTS")
        print("="*Display.CONSOLE_WIDTH + "\n")
        
        ReportGenerator.save_csv_report(analyzer.df)
        ReportGenerator.save_excel_report(analyzer.df, breadth_data, sector_data)
        ReportGenerator.save_summary_text(breadth_data, regime, action, sector_data)
        
        ReportGenerator.print_footer()
        
        # ============================================
        # TRADING CHECKLIST
        # ============================================
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("📋 DAILY TRADING CHECKLIST")
        print("="*Display.CONSOLE_WIDTH)
        
        print(f"\n1. ✅ Market Regime: {regime}")
        print(f"2. ✅ Breadth Score: {breadth_data['score']:+.3f}")
        print(f"3. ✅ Bull/Bear Ratio: {breadth_data['bull_bear_ratio']:.2f}:1")
        print(f"4. ✅ Sector Participation: {sector_data['participation_pct']:.0f}%")
        print(f"5. ✅ Trend: {trend}")
        
        print(f"\n💡 FOCUS SECTORS:")
        for sector, data in leaders:
            print(f"   ✅ {sector} (Score: {data['score']:+.2f})")
        
        print(f"\n⚠️  AVOID SECTORS:")
        for sector, data in laggards:
            print(f"   ❌ {sector} (Score: {data['score']:+.2f})")
        
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("🎯 READY TO TRADE!")
        print("="*Display.CONSOLE_WIDTH + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()