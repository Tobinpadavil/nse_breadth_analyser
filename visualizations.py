"""
Visualization helpers (requires matplotlib)
"""

import pandas as pd
import json
from pathlib import Path
from config import HISTORY_FILE

class BreadthVisualizer:
    """Create simple text-based visualizations"""
    
    @staticmethod
    def create_sparkline(values, width=50):
        """
        Create ASCII sparkline
        """
        if not values or len(values) < 2:
            return "N/A"
        
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        if range_val == 0:
            return "─" * width
        
        # Normalize to 0-7 range (8 vertical positions)
        ticks = "▁▂▃▄▅▆▇█"
        
        sparkline = ""
        for value in values:
            normalized = int(((value - min_val) / range_val) * 7)
            sparkline += ticks[normalized]
        
        return sparkline
    
    @staticmethod
    def create_horizontal_bar(value, max_value=100, width=30):
        """
        Create horizontal bar chart
        """
        if max_value == 0:
            return ""
        
        filled = int((value / max_value) * width)
        filled = max(0, min(filled, width))
        
        bar = "█" * filled + "░" * (width - filled)
        return f"{bar} {value:.1f}"
    
    @staticmethod
    def display_breadth_history(days=10):
        """
        Display breadth score history as sparkline
        """
        history_file = Path(HISTORY_FILE)
        
        if not history_file.exists():
            return "No history available"
        
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        if len(history) < 2:
            return "Insufficient history"
        
        recent = history[-days:]
        scores = [h['score'] for h in recent]
        dates = [h['date'] for h in recent]
        
        sparkline = BreadthVisualizer.create_sparkline(scores)
        
        return f"\n📈 {days}-Day Breadth Trend:\n   {dates[0]} {sparkline} {dates[-1]}\n   Score: {scores[0]:+.2f} → {scores[-1]:+.2f}"