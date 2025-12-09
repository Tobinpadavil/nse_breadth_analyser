"""
Quick launcher script with menu options
"""

import sys
from breadth_analyzer import main as run_full_analysis
from advanced_analysis import AdvancedAnalysis
from visualizations import BreadthVisualizer
from data_fetcher import DataFetcher
from analysis import BreadthAnalyzer

def show_menu():
    """Display analysis menu"""
    print("\n" + "="*80)
    print("📊 NSE F&O BREADTH ANALYZER - MENU")
    print("="*80)
    print("\n1. 🚀 Full Analysis (Complete report with all features)")
    print("2. ⚡ Quick Analysis (Basic breadth only)")
    print("3. 📈 Advanced Metrics (Market internals, concentration, etc.)")
    print("4. 📊 Historical Trend (View breadth history)")
    print("5. 🎯 Trading Signals (Get specific trading recommendations)")
    print("6. ❌ Exit")
    print("\n" + "="*80)

def quick_analysis():
    """Quick breadth check"""
    print("\n⚡ Running quick analysis...\n")
    
    fetcher = DataFetcher()
    df, _ = fetcher.fetch_all(show_progress=False)
    
    if df.empty:
        print("❌ No data available")
        return
    
    analyzer = BreadthAnalyzer(df)
    analyzer.classify_stocks()
    breadth_data = analyzer.calculate_breadth_score()
    regime, _ = analyzer.classify_regime()
    
    print(f"✅ Quick Results:")
    print(f"   Breadth Score: {breadth_data['score']:+.3f}")
    print(f"   Regime: {regime}")
    print(f"   Bulls: {breadth_data['total_bulls']} | Bears: {breadth_data['total_bears']}")

def advanced_metrics():
    """Show advanced metrics"""
    print("\n📈 Calculating advanced metrics...\n")
    
    fetcher = DataFetcher()
    df, _ = fetcher.fetch_all(show_progress=False)
    
    if df.empty:
        print("❌ No data available")
        return
    
    advanced = AdvancedAnalysis(df)
    
    # Market temperature
    temp = advanced.calculate_market_temperature()
    print(f"🌡️ Market Temperature: {temp['temperature']:.1f}/100 - {temp['status']}")
    
    # Market internals
    internals = advanced.calculate_market_internals()
    print(f"\n📊 Market Internals:")
    print(f"   AD Ratio: {internals['ad_ratio']:.2f} ({internals['advances']}↑ / {internals['declines']}↓)")
    print(f"   Volume Ratio: {internals['volume_ratio']:.2f} (Up/Down)")
    print(f"   TRIN: {internals['trin']:.2f} ({internals['trin_signal']})")
    
    # Concentration risk
    concentration = advanced.calculate_concentration_risk()
    print(f"\n🎯 Concentration Analysis:")
    print(f"   {concentration['risk_level']}")
    print(f"   Top contributors: {', '.join(concentration['top_contributors'])}")
    
    # Sentiment
    sentiment = advanced.detect_capitulation_or_euphoria()
    print(f"\n💭 Sentiment:")
    print(f"   {sentiment['signal']}")

def show_history():
    """Show historical trend"""
    print("\n📈 Breadth History:\n")
    trend = BreadthVisualizer.display_breadth_history(days=10)
    print(trend)

def trading_signals():
    """Generate trading signals"""
    print("\n🎯 Generating trading signals...\n")
    
    fetcher = DataFetcher()
    df, _ = fetcher.fetch_all(show_progress=False)
    
    if df.empty:
        print("❌ No data available")
        return
    
    analyzer = BreadthAnalyzer(df)
    analyzer.classify_stocks()
    breadth_data = analyzer.calculate_breadth_score()
    sector_data = analyzer.calculate_sector_breadth()
    
    advanced = AdvancedAnalysis(df)
    signals = advanced.generate_trading_signals(
        breadth_data['score'],
        sector_data['participation_pct']
    )
    
    print("📡 Trading Signals:")
    for signal in signals:
        print(f"\n   {signal['message']}")
        print(f"   Type: {signal['type']} | Strength: {signal['strength']}")

def main():
    """Main menu loop"""
    while True:
        show_menu()
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            run_full_analysis()
            input("\nPress Enter to continue...")
        elif choice == '2':
            quick_analysis()
            input("\nPress Enter to continue...")
        elif choice == '3':
            advanced_metrics()
            input("\nPress Enter to continue...")
        elif choice == '4':
            show_history()
            input("\nPress Enter to continue...")
        elif choice == '5':
            trading_signals()
            input("\nPress Enter to continue...")
        elif choice == '6':
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("\n❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()