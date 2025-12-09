"""
Advanced breadth analysis features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from config import Thresholds, SECTORS

class AdvancedAnalysis:
    """Advanced breadth analysis methods"""
    
    def __init__(self, df):
        self.df = df
    
    def calculate_market_temperature(self):
        """
        Calculate market temperature (0-100 scale)
        Combines breadth, momentum, and volume
        """
        df = self.df
        
        # Breadth component (0-40 points)
        up_pct = len(df[df['pct_change'] > 0]) / len(df) * 40
        
        # Momentum component (0-30 points)
        avg_change = df['pct_change'].mean()
        momentum_score = min(max((avg_change + 2) / 4 * 30, 0), 30)
        
        # Volume component (0-30 points)
        avg_vol_ratio = df['volume_ratio'].mean()
        volume_score = min(max((avg_vol_ratio - 0.5) / 1.5 * 30, 0), 30)
        
        temperature = up_pct + momentum_score + volume_score
        
        if temperature > 80:
            status = "🔥 OVERHEATED (Potential reversal)"
        elif temperature > 60:
            status = "🌡️ HOT (Strong bullish)"
        elif temperature > 40:
            status = "☀️ WARM (Moderate bullish)"
        elif temperature > 30:
            status = "🌤️ NEUTRAL"
        elif temperature > 20:
            status = "⛅ COOL (Moderate bearish)"
        else:
            status = "❄️ COLD (Strong bearish)"
        
        return {
            'temperature': round(temperature, 1),
            'status': status,
            'components': {
                'breadth': round(up_pct, 1),
                'momentum': round(momentum_score, 1),
                'volume': round(volume_score, 1)
            }
        }
    
    def calculate_market_internals(self):
        """
        Calculate key market internals
        Similar to NYSE internals (TICK, TRIN, etc.)
        """
        df = self.df
        
        # Advance/Decline numbers
        advances = len(df[df['pct_change'] > 0])
        declines = len(df[df['pct_change'] < 0])
        unchanged = len(df[df['pct_change'] == 0])
        
        # AD Ratio
        ad_ratio = advances / declines if declines > 0 else float('inf')
        
        # Volume-weighted internals
        up_volume = df[df['pct_change'] > 0]['volume'].sum()
        down_volume = df[df['pct_change'] < 0]['volume'].sum()
        volume_ratio = up_volume / down_volume if down_volume > 0 else float('inf')
        
        # TRIN equivalent (Arms Index)
        # TRIN = (Declines/Advances) / (Down Volume/Up Volume)
        if advances > 0 and up_volume > 0:
            trin = (declines / advances) / (down_volume / up_volume)
        else:
            trin = 0
        
        # Interpret TRIN
        if trin < 0.5:
            trin_signal = "Extremely Bullish"
        elif trin < 0.8:
            trin_signal = "Bullish"
        elif trin < 1.2:
            trin_signal = "Neutral"
        elif trin < 2.0:
            trin_signal = "Bearish"
        else:
            trin_signal = "Extremely Bearish"
        
        return {
            'advances': advances,
            'declines': declines,
            'unchanged': unchanged,
            'ad_ratio': round(ad_ratio, 2),
            'up_volume': up_volume,
            'down_volume': down_volume,
            'volume_ratio': round(volume_ratio, 2),
            'trin': round(trin, 2),
            'trin_signal': trin_signal
        }
    
    def calculate_concentration_risk(self):
        """
        Measure if gains/losses are concentrated in few stocks
        High concentration = risky/narrow market
        """
        df = self.df
        
        # Sort by absolute % change
        df_sorted = df.sort_values('pct_change', key=abs, ascending=False)
        
        # Top 10% of stocks
        top_10_pct = int(len(df) * 0.1)
        top_stocks = df_sorted.head(top_10_pct)
        
        # Calculate contribution
        total_abs_change = df['pct_change'].abs().sum()
        top_abs_change = top_stocks['pct_change'].abs().sum()
        
        concentration = (top_abs_change / total_abs_change) * 100
        
        if concentration > 50:
            risk_level = "🔴 HIGH RISK - Very narrow market"
        elif concentration > 35:
            risk_level = "🟡 MODERATE RISK - Somewhat narrow"
        else:
            risk_level = "🟢 LOW RISK - Broad participation"
        
        return {
            'concentration_pct': round(concentration, 1),
            'risk_level': risk_level,
            'top_contributors': list(top_stocks['symbol'].head(5))
        }
    
    def calculate_sector_rotation_strength(self):
        """
        Measure strength of sector rotation
        Strong rotation = healthy market
        """
        df = self.df
        
        sector_performances = {}
        for sector, stocks in SECTORS.items():
            sector_df = df[df['symbol'].isin(stocks)]
            if len(sector_df) > 0:
                avg_change = sector_df['pct_change'].mean()
                sector_performances[sector] = avg_change
        
        # Calculate standard deviation of sector performances
        performances = list(sector_performances.values())
        if len(performances) > 1:
            rotation_strength = np.std(performances)
            
            if rotation_strength > 2.0:
                rotation_status = "🔄 STRONG ROTATION - Divergent sector moves"
            elif rotation_strength > 1.0:
                rotation_status = "↔️ MODERATE ROTATION - Some divergence"
            else:
                rotation_status = "➡️ WEAK ROTATION - Sectors moving together"
        else:
            rotation_strength = 0
            rotation_status = "N/A"
        
        # Leading and lagging sectors
        sorted_sectors = sorted(sector_performances.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'rotation_strength': round(rotation_strength, 2),
            'status': rotation_status,
            'leading_sector': sorted_sectors[0] if sorted_sectors else None,
            'lagging_sector': sorted_sectors[-1] if sorted_sectors else None
        }
    
    def detect_capitulation_or_euphoria(self):
        """
        Detect extreme sentiment conditions
        """
        df = self.df
        magnitude_data = self.calculate_magnitude_stats()
        
        # Capitulation signals
        explosive_down_pct = magnitude_data['explosive_down'] / len(df) * 100
        if explosive_down_pct > 15:
            return {
                'condition': 'CAPITULATION',
                'signal': '💀 CAPITULATION DETECTED - Potential bottom near',
                'explosive_moves_pct': round(explosive_down_pct, 1),
                'action': 'Watch for reversal, prepare long entries'
            }
        
        # Euphoria signals
        explosive_up_pct = magnitude_data['explosive_up'] / len(df) * 100
        if explosive_up_pct > 15:
            return {
                'condition': 'EUPHORIA',
                'signal': '🚀 EUPHORIA DETECTED - Potential top near',
                'explosive_moves_pct': round(explosive_up_pct, 1),
                'action': 'Book profits, tighten stops'
            }
        
        return {
            'condition': 'NORMAL',
            'signal': 'No extreme sentiment detected',
            'explosive_moves_pct': 0,
            'action': 'Continue normal trading'
        }
    
    def calculate_magnitude_stats(self):
        """Helper method for magnitude statistics"""
        df = self.df
        
        return {
            'explosive_up': len(df[df['pct_change'] > 5]),
            'explosive_down': len(df[df['pct_change'] < -5])
        }
    
    def generate_trading_signals(self, breadth_score, sector_participation):
        """
        Generate specific trading signals based on analysis
        """
        signals = []
        
        # Signal 1: Strong breadth + high participation
        if breadth_score > 0.5 and sector_participation > 70:
            signals.append({
                'type': 'BUY',
                'strength': 'STRONG',
                'message': '✅ Strong buy signal - Broad-based rally with high participation'
            })
        
        # Signal 2: Weak breadth with high participation warning
        elif breadth_score > 0 and sector_participation < 40:
            signals.append({
                'type': 'WARNING',
                'strength': 'MODERATE',
                'message': '⚠️ Narrow leadership warning - Reduce exposure'
            })
        
        # Signal 3: Strong bearish breadth
        elif breadth_score < -0.5:
            signals.append({
                'type': 'SELL',
                'strength': 'STRONG',
                'message': '❌ Strong sell signal - Broad-based decline'
            })
        
        # Signal 4: Neutral/choppy
        elif -0.2 < breadth_score < 0.2:
            signals.append({
                'type': 'NEUTRAL',
                'strength': 'WEAK',
                'message': '🚫 No clear signal - Stay in cash or tight ranges'
            })
        
        return signals