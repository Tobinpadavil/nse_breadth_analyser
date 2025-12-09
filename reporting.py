"""
Report generation module
"""

import pandas as pd
from datetime import datetime
from config import Display, CSV_OUTPUT, SUMMARY_OUTPUT, EXCEL_OUTPUT, Thresholds

class ReportGenerator:
    """Generate analysis reports"""
    
    @staticmethod
    def print_header():
        """Print report header"""
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print(f"📊 NSE F&O BREADTH THRUST ANALYZER - COMPREHENSIVE ANALYSIS")
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*Display.CONSOLE_WIDTH)
    
    @staticmethod
    def print_breadth_summary(breadth_data, regime, action, moving_avg=None, trend=None):
        """Print breadth summary"""
        score = breadth_data['score']
        
        print(f"\n{'='*60}")
        print(f"  BREADTH SCORE: {score:+.3f}")
        if moving_avg:
            print(f"  {Thresholds.AVERAGE_PERIOD}-DAY AVERAGE: {moving_avg:+.3f}")
        if trend:
            print(f"  TREND: {trend}")
        print(f"{'='*60}")
        
        print(f"\n📈 STOCK CLASSIFICATION:")
        print(f"   Strong Bulls (>2%, Vol+): {breadth_data['strong_bulls']:3d}")
        print(f"   Weak Bulls (>2%, Vol-):   {breadth_data['weak_bulls']:3d}")
        print(f"   Neutral (-2% to +2%):     {breadth_data['neutral']:3d}")
        print(f"   Weak Bears (<-2%, Vol-):  {breadth_data['weak_bears']:3d}")
        print(f"   Strong Bears (<-2%, Vol+): {breadth_data['strong_bears']:3d}")
        print(f"   {'─'*56}")
        print(f"   Total Stocks:              {breadth_data['total']:3d}")
        print(f"   Bull/Bear Ratio:           {breadth_data['bull_bear_ratio']:.2f}:1")
        
        print(f"\n🎯 MARKET REGIME: {regime}")
        
        print(f"\n💡 TRADING ACTION:")
        for line in action.split('\n'):
            print(f"   {line}")
    
    @staticmethod
    def print_sector_analysis(sector_data):
        """Print sector analysis"""
        participation = sector_data['participation_pct']
        sectors = sector_data['sectors']
        
        print(f"\n🏭 SECTOR BREADTH (Participation: {participation:.0f}%):")
        
        # Sort by score
        sorted_sectors = sorted(
            sectors.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        for sector, data in sorted_sectors:
            icon = "✅" if data['status'] == "Bullish" else "❌" if data['status'] == "Bearish" else "➖"
            print(f"   {icon} {sector:25s}: {data['up_strong']:2d}↑↑ {data['up_moderate']:2d}↑ "
                  f"{data['down_moderate']:2d}↓ {data['down_strong']:2d}↓↓ | "
                  f"Score: {data['score']:+.2f} | Avg: {data['avg_change']:+.2f}%")
    
    @staticmethod
    def print_magnitude_analysis(magnitude_data):
        """Print magnitude analysis"""
        print(f"\n📊 MAGNITUDE ANALYSIS (Ultra Score: {magnitude_data['ultra_score']:+.3f}):")
        print(f"   Explosive Up (>5%):    {magnitude_data['explosive_up']:3d}")
        print(f"   Strong Up (3-5%):      {magnitude_data['strong_up']:3d}")
        print(f"   Moderate Up (2-3%):    {magnitude_data['moderate_up']:3d}")
        print(f"   {'─'*50}")
        print(f"   Moderate Down (2-3%):  {magnitude_data['moderate_down']:3d}")
        print(f"   Strong Down (3-5%):    {magnitude_data['strong_down']:3d}")
        print(f"   Explosive Down (>5%):  {magnitude_data['explosive_down']:3d}")
    
    @staticmethod
    def print_top_movers(top_gainers, top_losers):
        """Print top movers"""
        print(f"\n🔥 TOP {Display.TOP_MOVERS_COUNT} GAINERS:")
        for idx, row in top_gainers.iterrows():
            print(f"   {row['symbol']:15s} {row['pct_change']:+6.2f}%  "
                  f"Vol: {row['volume_ratio']:.2f}x  [{row['category']}]")
        
        print(f"\n❄️  TOP {Display.TOP_MOVERS_COUNT} LOSERS:")
        for idx, row in top_losers.iterrows():
            print(f"   {row['symbol']:15s} {row['pct_change']:+6.2f}%  "
                  f"Vol: {row['volume_ratio']:.2f}x  [{row['category']}]")
    
    @staticmethod
    def print_sector_focus(leaders, laggards):
        """Print sector focus recommendations"""
        print(f"\n🎯 SECTOR FOCUS:")
        
        print(f"\n   ✅ LEADING SECTORS (Focus here):")
        for sector, data in leaders:
            print(f"      • {sector}: Score {data['score']:+.2f}, Avg Change {data['avg_change']:+.2f}%")
        
        print(f"\n   ❌ LAGGING SECTORS (Avoid):")
        for sector, data in laggards:
            print(f"      • {sector}: Score {data['score']:+.2f}, Avg Change {data['avg_change']:+.2f}%")
    
    @staticmethod
    def save_csv_report(df, filename=CSV_OUTPUT):
        """Save detailed CSV report"""
        df_export = df[[
            'symbol', 'price', 'prev_close', 'pct_change', 
            'volume', 'volume_ratio', 'category'
        ]].sort_values('pct_change', ascending=False)
        
        df_export.to_csv(filename, index=False)
        print(f"\n📁 Detailed CSV saved: {filename}")
    
    @staticmethod
    def save_excel_report(df, breadth_data, sector_data, filename=EXCEL_OUTPUT):
        """Save comprehensive Excel report"""
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Sheet 1: All stocks
                df_export = df[[
                    'symbol', 'price', 'prev_close', 'pct_change', 
                    'volume', 'volume_ratio', 'category'
                ]].sort_values('pct_change', ascending=False)
                df_export.to_excel(writer, sheet_name='All Stocks', index=False)
                
                # Sheet 2: Summary
                summary_data = {
                    'Metric': [
                        'Breadth Score',
                        'Strong Bulls',
                        'Weak Bulls',
                        'Neutral',
                        'Weak Bears',
                        'Strong Bears',
                        'Bull/Bear Ratio',
                        'Sector Participation %'
                    ],
                    'Value': [
                        breadth_data['score'],
                        breadth_data['strong_bulls'],
                        breadth_data['weak_bulls'],
                        breadth_data['neutral'],
                        breadth_data['weak_bears'],
                        breadth_data['strong_bears'],
                        breadth_data['bull_bear_ratio'],
                        sector_data['participation_pct']
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                # Sheet 3: Sector Analysis
                sector_df = pd.DataFrame([
                    {
                        'Sector': sector,
                        'Up Strong': data['up_strong'],
                        'Up Moderate': data['up_moderate'],
                        'Down Moderate': data['down_moderate'],
                        'Down Strong': data['down_strong'],
                        'Score': data['score'],
                        'Avg Change %': data['avg_change'],
                        'Status': data['status']
                    }
                    for sector, data in sector_data['sectors'].items()
                ]).sort_values('Score', ascending=False)
                sector_df.to_excel(writer, sheet_name='Sectors', index=False)
            
            print(f"📊 Excel report saved: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save Excel report: {e}")
            print(f"   (This is optional, CSV report was saved successfully)")
    
    @staticmethod
    def save_summary_text(breadth_data, regime, action, sector_data, filename=SUMMARY_OUTPUT):
        """Save text summary"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("NSE F&O BREADTH ANALYSIS SUMMARY\n")
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"BREADTH SCORE: {breadth_data['score']:+.3f}\n")
                f.write(f"MARKET REGIME: {regime}\n\n")
                
                f.write(f"TRADING ACTION:\n{action}\n\n")
                
                f.write("STOCK COUNTS:\n")
                f.write(f"  Strong Bulls: {breadth_data['strong_bulls']}\n")
                f.write(f"  Weak Bulls: {breadth_data['weak_bulls']}\n")
                f.write(f"  Neutral: {breadth_data['neutral']}\n")
                f.write(f"  Weak Bears: {breadth_data['weak_bears']}\n")
                f.write(f"  Strong Bears: {breadth_data['strong_bears']}\n\n")
                
                f.write(f"SECTOR PARTICIPATION: {sector_data['participation_pct']:.0f}%\n")
            
            print(f"📝 Summary text saved: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save text summary: {e}")
    
    @staticmethod
    def print_footer():
        """Print report footer"""
        print("\n" + "="*Display.CONSOLE_WIDTH)
        print("✅ Analysis complete!")
        print("="*Display.CONSOLE_WIDTH + "\n")


class QuickReport:
    """Generate quick summary reports"""
    
    @staticmethod
    def print_quick_summary(breadth_data, regime, sector_participation):
        """Print quick one-screen summary"""
        print("\n" + "="*60)
        print("⚡ QUICK BREADTH SUMMARY")
        print("="*60)
        
        score = breadth_data['score']
        bulls = breadth_data['total_bulls']
        bears = breadth_data['total_bears']
        ratio = breadth_data['bull_bear_ratio']
        
        print(f"\n🎯 REGIME: {regime}")
        print(f"📊 SCORE: {score:+.3f}")
        print(f"📈 BULLS: {bulls} | BEARS: {bears} | RATIO: {ratio:.2f}:1")
        print(f"🏭 SECTOR PARTICIPATION: {sector_participation:.0f}%")
        print("\n" + "="*60 + "\n")
    
    @staticmethod
    def print_trading_decision(regime, action):
        """Print concise trading decision"""
        print("💡 TRADING DECISION:")
        print("-"*60)
        print(f"{regime}")
        print(f"\n{action}")
        print("-"*60 + "\n")