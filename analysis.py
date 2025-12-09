"""
Market breadth analysis module
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from pathlib import Path
from config import (
    SECTORS, Thresholds, REGIMES, 
    HISTORY_FILE, Display
)

class BreadthAnalyzer:
    """Analyze market breadth from stock data"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.breadth_data = {}
        self.sector_data = {}
        self.magnitude_data = {}
        self.regime = None
        self.action = None
        
    def classify_stocks(self):
        """Classify stocks into breadth categories"""
        df = self.df
        
        # Initialize category
        df['category'] = 'Neutral'
        
        # Strong Bulls: >2% with high volume
        strong_bull_mask = (
            (df['pct_change'] > Thresholds.STRONG_MOVE) & 
            (df['volume_ratio'] > Thresholds.VOLUME_MULTIPLIER)
        )
        df.loc[strong_bull_mask, 'category'] = 'Strong Bull'
        
        # Weak Bulls: >2% without volume
        weak_bull_mask = (
            (df['pct_change'] > Thresholds.STRONG_MOVE) & 
            (df['volume_ratio'] <= Thresholds.VOLUME_MULTIPLIER)
        )
        df.loc[weak_bull_mask, 'category'] = 'Weak Bull'
        
        # Strong Bears: <-2% with high volume
        strong_bear_mask = (
            (df['pct_change'] < -Thresholds.STRONG_MOVE) & 
            (df['volume_ratio'] > Thresholds.VOLUME_MULTIPLIER)
        )
        df.loc[strong_bear_mask, 'category'] = 'Strong Bear'
        
        # Weak Bears: <-2% without volume
        weak_bear_mask = (
            (df['pct_change'] < -Thresholds.STRONG_MOVE) & 
            (df['volume_ratio'] <= Thresholds.VOLUME_MULTIPLIER)
        )
        df.loc[weak_bear_mask, 'category'] = 'Weak Bear'
        
        self.df = df
        return df
    
    def calculate_breadth_score(self):
        """Calculate weighted breadth score"""
        counts = self.df['category'].value_counts()
        
        strong_bulls = int(counts.get('Strong Bull', 0))
        weak_bulls = int(counts.get('Weak Bull', 0))
        strong_bears = int(counts.get('Strong Bear', 0))
        weak_bears = int(counts.get('Weak Bear', 0))
        neutral = int(counts.get('Neutral', 0))
        
        # Weighted calculation
        numerator = (strong_bulls * 2) + (weak_bulls * 1) - (strong_bears * 2) - (weak_bears * 1)
        denominator = len(self.df)
        
        score = numerator / denominator if denominator > 0 else 0
        
        # Calculate additional metrics
        total_bulls = strong_bulls + weak_bulls
        total_bears = strong_bears + weak_bears
        bull_bear_ratio = total_bulls / total_bears if total_bears > 0 else float('inf')
        
        self.breadth_data = {
            'score': round(score, Display.SCORE_DECIMALS),
            'strong_bulls': strong_bulls,
            'weak_bulls': weak_bulls,
            'strong_bears': strong_bears,
            'weak_bears': weak_bears,
            'neutral': neutral,
            'total': denominator,
            'total_bulls': total_bulls,
            'total_bears': total_bears,
            'bull_bear_ratio': round(bull_bear_ratio, Display.RATIO_DECIMALS)
        }
        
        return self.breadth_data
    
    def calculate_sector_breadth(self):
        """Calculate breadth by sector"""
        sector_breadth = {}
        
        for sector, stocks in SECTORS.items():
            sector_df = self.df[self.df['symbol'].isin(stocks)]
            
            if len(sector_df) == 0:
                continue
            
            # Count stocks by movement
            up_strong = len(sector_df[sector_df['pct_change'] > Thresholds.STRONG_MOVE])
            up_moderate = len(sector_df[
                (sector_df['pct_change'] > Thresholds.MODERATE_MOVE) & 
                (sector_df['pct_change'] <= Thresholds.STRONG_MOVE)
            ])
            down_moderate = len(sector_df[
                (sector_df['pct_change'] < -Thresholds.MODERATE_MOVE) & 
                (sector_df['pct_change'] >= -Thresholds.STRONG_MOVE)
            ])
            down_strong = len(sector_df[sector_df['pct_change'] < -Thresholds.STRONG_MOVE])
            
            net_breadth = up_strong - down_strong
            
            # Calculate sector score
            sector_score = (up_strong * 2 + up_moderate * 1 - down_strong * 2 - down_moderate * 1) / len(sector_df)
            
            # Average % change in sector
            avg_change = sector_df['pct_change'].mean()
            
            sector_breadth[sector] = {
                'up_strong': up_strong,
                'up_moderate': up_moderate,
                'down_moderate': down_moderate,
                'down_strong': down_strong,
                'total': len(sector_df),
                'net': net_breadth,
                'score': round(sector_score, Display.SCORE_DECIMALS),
                'avg_change': round(avg_change, Display.PERCENT_DECIMALS),
                'status': 'Bullish' if net_breadth > 0 else 'Bearish' if net_breadth < 0 else 'Neutral'
            }
        
        # Calculate participation
        bullish_sectors = sum(1 for s in sector_breadth.values() if s['status'] == 'Bullish')
        total_sectors = len(sector_breadth)
        participation_pct = (bullish_sectors / total_sectors * 100) if total_sectors > 0 else 0
        
        self.sector_data = {
            'sectors': sector_breadth,
            'bullish_count': bullish_sectors,
            'total_count': total_sectors,
            'participation_pct': round(participation_pct, Display.PERCENT_DECIMALS)
        }
        
        return self.sector_data
    
    def calculate_magnitude_analysis(self):
        """Calculate magnitude-based analysis"""
        df = self.df
        
        # Categorize by magnitude
        explosive_up = len(df[df['pct_change'] > Thresholds.EXPLOSIVE_MOVE])
        strong_up = len(df[
            (df['pct_change'] >= Thresholds.STRONG_EXPLOSIVE) & 
            (df['pct_change'] <= Thresholds.EXPLOSIVE_MOVE)
        ])
        moderate_up = len(df[
            (df['pct_change'] >= Thresholds.STRONG_MOVE) & 
            (df['pct_change'] < Thresholds.STRONG_EXPLOSIVE)
        ])
        
        explosive_down = len(df[df['pct_change'] < -Thresholds.EXPLOSIVE_MOVE])
        strong_down = len(df[
            (df['pct_change'] <= -Thresholds.STRONG_EXPLOSIVE) & 
            (df['pct_change'] > -Thresholds.EXPLOSIVE_MOVE)
        ])
        moderate_down = len(df[
            (df['pct_change'] <= -Thresholds.STRONG_MOVE) & 
            (df['pct_change'] > -Thresholds.STRONG_EXPLOSIVE)
        ])
        
        # Ultra-weighted score
        numerator = (explosive_up * 3) + (strong_up * 2) + (moderate_up * 1) - \
                   (explosive_down * 3) - (strong_down * 2) - (moderate_down * 1)
        
        ultra_score = numerator / len(df) if len(df) > 0 else 0
        
        self.magnitude_data = {
            'ultra_score': round(ultra_score, Display.SCORE_DECIMALS),
            'explosive_up': explosive_up,
            'strong_up': strong_up,
            'moderate_up': moderate_up,
            'explosive_down': explosive_down,
            'strong_down': strong_down,
            'moderate_down': moderate_down
        }
        
        return self.magnitude_data
    
    def classify_regime(self):
        """Classify market regime based on breadth score"""
        score = self.breadth_data['score']
        participation = self.sector_data['participation_pct']
        
        # Determine regime
        if score > Thresholds.EXTREME_BULL:
            regime_key = "EXTREME_BULL"
        elif score >= Thresholds.STRONG_BULL:
            regime_key = "STRONG_BULL"
        elif score >= Thresholds.WEAK_BULL:
            regime_key = "WEAK_BULL"
        elif score >= Thresholds.NO_TRADE_LOW:
            regime_key = "NO_TRADE"
        elif score >= Thresholds.WEAK_BEAR:
            regime_key = "WEAK_BEAR"
        elif score >= Thresholds.STRONG_BEAR:
            regime_key = "STRONG_BEAR"
        else:
            regime_key = "EXTREME_BEAR"
        
        regime_info = REGIMES[regime_key]
        self.regime = regime_info['name']
        self.action = regime_info['action']
        
        # Adjust for narrow leadership
        if participation < Thresholds.WEAK_PARTICIPATION and score > 0:
            self.action += "\n   ⚠️ WARNING: Narrow leadership (low participation) - Reduce sizing by 30%"
        
        return self.regime, self.action
    
    def get_top_movers(self, n=10):
        """Get top gainers and losers"""
        top_gainers = self.df.nlargest(n, 'pct_change')[
            ['symbol', 'pct_change', 'volume_ratio', 'category']
        ]
        top_losers = self.df.nsmallest(n, 'pct_change')[
            ['symbol', 'pct_change', 'volume_ratio', 'category']
        ]
        
        return top_gainers, top_losers
    
    def get_sector_leaders_laggards(self):
        """Identify leading and lagging sectors"""
        sectors = self.sector_data['sectors']
        
        # Sort by score
        sorted_sectors = sorted(
            sectors.items(), 
            key=lambda x: x[1]['score'], 
            reverse=True
        )
        
        leaders = sorted_sectors[:3]  # Top 3
        laggards = sorted_sectors[-3:]  # Bottom 3
        
        return leaders, laggards

class HistoryManager:
    """Manage historical breadth data"""
    
    def __init__(self, filepath=HISTORY_FILE):
        self.filepath = Path(filepath)
        
    def load_history(self):
        """Load historical scores"""
        if self.filepath.exists():
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_score(self, date, score, regime):
        """Save today's score"""
        history = self.load_history()
        
        # Remove today if exists
        today_str = date.strftime('%Y-%m-%d')
        history = [h for h in history if h['date'] != today_str]
        
        # Add today
        history.append({
            'date': today_str,
            'score': float(score),
            'regime': regime
        })
        
        # Keep last N days
        history = history[-Thresholds.HISTORY_DAYS:]
        
        # Save
        with open(self.filepath, 'w') as f:
            json.dump(history, f, indent=2)
    
    def get_moving_average(self, period=Thresholds.AVERAGE_PERIOD):
        """Calculate moving average of breadth score"""
        history = self.load_history()
        
        if len(history) < 1:
            return None
        
        recent = history[-period:]
        scores = [h['score'] for h in recent]
        
        return round(sum(scores) / len(scores), Display.SCORE_DECIMALS)
    
    def get_trend(self, lookback=5):
        """Determine trend direction"""
        history = self.load_history()
        
        if len(history) < lookback:
            return "Insufficient data"
        
        recent = history[-lookback:]
        scores = [h['score'] for h in recent]
        
        # Simple trend
        if scores[-1] > scores[0]:
            return "Improving"
        elif scores[-1] < scores[0]:
            return "Deteriorating"
        else:
            return "Stable"
    
    def detect_divergence(self, current_score):
        """Detect if breadth is diverging from recent trend"""
        history = self.load_history()
        
        if len(history) < 3:
            return None, "Insufficient data"
        
        # Get last 3 scores
        recent = history[-3:]
        scores = [h['score'] for h in recent]
        
        # Check if deteriorating while still positive
        if current_score > 0 and all(scores[i] > scores[i+1] for i in range(len(scores)-1)):
            return "bearish", "⚠️ Breadth deteriorating - Distribution warning"
        
        # Check if improving while still negative
        if current_score < 0 and all(scores[i] < scores[i+1] for i in range(len(scores)-1)):
            return "bullish", "✨ Breadth improving - Accumulation signal"
        
        return None, "No divergence"