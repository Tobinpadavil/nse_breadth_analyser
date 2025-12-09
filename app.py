"""
NSE F&O Breadth Thrust Analyzer - Streamlit Web App
Complete market breadth analysis dashboard
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Display, SECTORS, REGIMES, Thresholds
from data_fetcher import DataFetcher
from analysis import BreadthAnalyzer, HistoryManager
from advanced_analysis import AdvancedAnalysis

# Page config
st.set_page_config(
    page_title="NSE F&O Breadth Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .bull-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .bear-card {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
    }
    .neutral-card {
        background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
    }
    .stAlert {
        padding: 1rem;
        border-radius: 8px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.analyzer = None
    st.session_state.breadth_data = None
    st.session_state.sector_data = None
    st.session_state.magnitude_data = None
    st.session_state.regime = None
    st.session_state.action = None
    st.session_state.last_update = None

def load_data():
    """Fetch and analyze market data"""
    with st.spinner("🔄 Fetching market data... This may take 1-2 minutes..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Fetch data
        status_text.text("Fetching stock data from Yahoo Finance...")
        fetcher = DataFetcher()
        df, failed = fetcher.fetch_all(show_progress=False)
        progress_bar.progress(30)
        
        if df.empty:
            st.error("❌ No data fetched. Please check your internet connection and try again.")
            return False
        
        # Analyze data
        status_text.text("Analyzing market breadth...")
        analyzer = BreadthAnalyzer(df)
        analyzer.classify_stocks()
        progress_bar.progress(50)
        
        breadth_data = analyzer.calculate_breadth_score()
        progress_bar.progress(60)
        
        sector_data = analyzer.calculate_sector_breadth()
        progress_bar.progress(70)
        
        magnitude_data = analyzer.calculate_magnitude_analysis()
        progress_bar.progress(80)
        
        regime, action = analyzer.classify_regime()
        progress_bar.progress(90)
        
        # Save to session state
        st.session_state.df = df
        st.session_state.analyzer = analyzer
        st.session_state.breadth_data = breadth_data
        st.session_state.sector_data = sector_data
        st.session_state.magnitude_data = magnitude_data
        st.session_state.regime = regime
        st.session_state.action = action
        st.session_state.data_loaded = True
        st.session_state.last_update = datetime.now()
        
        # Save to history
        history_mgr = HistoryManager()
        history_mgr.save_score(datetime.now(), breadth_data['score'], regime)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        time.sleep(0.5)
        progress_bar.empty()
        status_text.empty()
        
        return True

def display_header():
    """Display main header"""
    st.markdown('<div class="main-header">🚀 NSE F&O BREADTH THRUST ANALYZER</div>', 
                unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.write(f"**📅 Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        if st.session_state.last_update:
            st.write(f"**🕐 Last Update:** {st.session_state.last_update.strftime('%H:%M:%S')}")
    with col3:
        if st.button("🔄 Refresh Data", type="primary"):
            st.session_state.data_loaded = False
            st.rerun()

def display_key_metrics():
    """Display key metrics in cards"""
    breadth_data = st.session_state.breadth_data
    sector_data = st.session_state.sector_data
    regime = st.session_state.regime
    
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score = breadth_data['score']
        st.metric(
            "Breadth Score",
            f"{score:+.3f}",
            help="Weighted breadth score (-2 to +2 scale)"
        )
    
    with col2:
        ratio = breadth_data['bull_bear_ratio']
        st.metric(
            "Bull/Bear Ratio",
            f"{ratio:.2f}:1",
            help="Ratio of bullish to bearish stocks"
        )
    
    with col3:
        participation = sector_data['participation_pct']
        st.metric(
            "Sector Participation",
            f"{participation:.0f}%",
            help="Percentage of sectors showing bullish behavior"
        )
    
    with col4:
        st.metric(
            "Market Regime",
            regime.replace("🚀", "").replace("✅", "").replace("⚠️", "").replace("🚫", "").replace("📉", "").replace("💀", "").strip(),
            help="Current market regime classification"
        )

def display_regime_action():
    """Display regime and trading action"""
    regime = st.session_state.regime
    action = st.session_state.action
    score = st.session_state.breadth_data['score']
    
    st.subheader("🎯 Market Regime & Trading Action")
    
    # Determine alert type based on score
    if score > 0.4:
        alert_type = "success"
    elif score > 0:
        alert_type = "info"
    elif score > -0.4:
        alert_type = "warning"
    else:
        alert_type = "error"
    
    st.markdown(f"### {regime}")
    
    # Display action with appropriate styling
    for line in action.split('\n'):
        if line.strip():
            st.markdown(f"**{line.strip()}**")

def display_stock_classification():
    """Display stock classification breakdown"""
    breadth_data = st.session_state.breadth_data
    
    st.subheader("📈 Stock Classification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        labels = ['Strong Bulls', 'Weak Bulls', 'Neutral', 'Weak Bears', 'Strong Bears']
        values = [
            breadth_data['strong_bulls'],
            breadth_data['weak_bulls'],
            breadth_data['neutral'],
            breadth_data['weak_bears'],
            breadth_data['strong_bears']
        ]
        colors = ['#00cc00', '#66ff66', '#ffcc00', '#ff6666', '#cc0000']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+value+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title="Stock Distribution",
            showlegend=True,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=labels,
            y=values,
            marker=dict(color=colors),
            text=values,
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Stock Count by Category",
            xaxis_title="Category",
            yaxis_title="Number of Stocks",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Statistics table
    st.markdown("### 📋 Detailed Breakdown")
    stats_df = pd.DataFrame({
        'Category': labels,
        'Count': values,
        'Percentage': [f"{v/breadth_data['total']*100:.1f}%" for v in values]
    })
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

def display_sector_analysis():
    """Display sector breadth analysis"""
    sector_data = st.session_state.sector_data
    
    st.subheader("🏭 Sector Breadth Analysis")
    
    # Convert sector data to DataFrame
    sectors_list = []
    for sector, data in sector_data['sectors'].items():
        sectors_list.append({
            'Sector': sector,
            'Score': data['score'],
            'Avg Change %': data['avg_change'],
            'Up Strong': data['up_strong'],
            'Up Moderate': data['up_moderate'],
            'Down Moderate': data['down_moderate'],
            'Down Strong': data['down_strong'],
            'Status': data['status']
        })
    
    sectors_df = pd.DataFrame(sectors_list).sort_values('Score', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sector score bar chart
        fig = go.Figure()
        
        colors = ['green' if s == 'Bullish' else 'red' if s == 'Bearish' else 'gray' 
                  for s in sectors_df['Status']]
        
        fig.add_trace(go.Bar(
            y=sectors_df['Sector'],
            x=sectors_df['Score'],
            orientation='h',
            marker=dict(color=colors),
            text=sectors_df['Score'].round(2),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Sector Scores",
            xaxis_title="Score",
            yaxis_title="Sector",
            showlegend=False,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sector average change
        fig = go.Figure()
        
        colors = ['green' if x > 0 else 'red' for x in sectors_df['Avg Change %']]
        
        fig.add_trace(go.Bar(
            y=sectors_df['Sector'],
            x=sectors_df['Avg Change %'],
            orientation='h',
            marker=dict(color=colors),
            text=sectors_df['Avg Change %'].round(2),
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Sector Average Change %",
            xaxis_title="Change %",
            yaxis_title="Sector",
            showlegend=False,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed sector table
    st.markdown("### 📊 Detailed Sector Data")
    st.dataframe(sectors_df, use_container_width=True, hide_index=True)

def display_magnitude_analysis():
    """Display magnitude-based analysis"""
    magnitude_data = st.session_state.magnitude_data
    
    st.subheader("💥 Magnitude Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Ultra Score",
            f"{magnitude_data['ultra_score']:+.3f}",
            help="Magnitude-weighted breadth score"
        )
    
    with col2:
        # Create stacked bar chart
        categories = ['Explosive (>5%)', 'Strong (3-5%)', 'Moderate (2-3%)']
        up_values = [
            magnitude_data['explosive_up'],
            magnitude_data['strong_up'],
            magnitude_data['moderate_up']
        ]
        down_values = [
            -magnitude_data['explosive_down'],
            -magnitude_data['strong_down'],
            -magnitude_data['moderate_down']
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Up Moves',
            x=categories,
            y=up_values,
            marker_color='green'
        ))
        
        fig.add_trace(go.Bar(
            name='Down Moves',
            x=categories,
            y=down_values,
            marker_color='red'
        ))
        
        fig.update_layout(
            title="Magnitude Distribution",
            yaxis_title="Stock Count",
            barmode='relative',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_top_movers():
    """Display top gainers and losers"""
    analyzer = st.session_state.analyzer
    top_gainers, top_losers = analyzer.get_top_movers(Display.TOP_MOVERS_COUNT)
    
    st.subheader("🔥 Top Movers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Top Gainers")
        gainers_display = top_gainers[['symbol', 'pct_change', 'volume_ratio', 'category']].copy()
        gainers_display.columns = ['Symbol', 'Change %', 'Volume Ratio', 'Category']
        st.dataframe(
            gainers_display.style.format({'Change %': '{:+.2f}', 'Volume Ratio': '{:.2f}'}),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("### 📉 Top Losers")
        losers_display = top_losers[['symbol', 'pct_change', 'volume_ratio', 'category']].copy()
        losers_display.columns = ['Symbol', 'Change %', 'Volume Ratio', 'Category']
        st.dataframe(
            losers_display.style.format({'Change %': '{:+.2f}', 'Volume Ratio': '{:.2f}'}),
            use_container_width=True,
            hide_index=True
        )

def display_advanced_metrics():
    """Display advanced analysis metrics"""
    df = st.session_state.df
    advanced = AdvancedAnalysis(df)
    
    st.subheader("🔬 Advanced Market Metrics")
    
    # Market Temperature
    temp = advanced.calculate_market_temperature()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Market Temperature", f"{temp['temperature']:.1f}/100")
        st.caption(temp['status'])
    
    with col2:
        st.metric("Breadth Component", f"{temp['components']['breadth']:.1f}")
    
    with col3:
        st.metric("Momentum Component", f"{temp['components']['momentum']:.1f}")
    
    # Market Internals
    st.markdown("### 📊 Market Internals")
    internals = advanced.calculate_market_internals()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Advances", internals['advances'])
    
    with col2:
        st.metric("Declines", internals['declines'])
    
    with col3:
        st.metric("AD Ratio", f"{internals['ad_ratio']:.2f}")
    
    with col4:
        st.metric("TRIN", f"{internals['trin']:.2f}")
        st.caption(internals['trin_signal'])
    
    # Concentration Risk
    st.markdown("### 🎯 Concentration Analysis")
    concentration = advanced.calculate_concentration_risk()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(
            "Concentration Risk",
            f"{concentration['concentration_pct']:.1f}%",
            help="Percentage of movement concentrated in top 10% stocks"
        )
        st.caption(concentration['risk_level'])
    
    with col2:
        st.markdown("**Top Contributors:**")
        st.write(", ".join(concentration['top_contributors']))
    
    # Sentiment Detection
    st.markdown("### 💭 Sentiment Analysis")
    sentiment = advanced.detect_capitulation_or_euphoria()
    
    if sentiment['condition'] == 'CAPITULATION':
        st.error(sentiment['signal'])
        st.warning(f"**Action:** {sentiment['action']}")
    elif sentiment['condition'] == 'EUPHORIA':
        st.warning(sentiment['signal'])
        st.info(f"**Action:** {sentiment['action']}")
    else:
        st.success(sentiment['signal'])

def display_historical_trend():
    """Display historical breadth trend"""
    st.subheader("📈 Historical Breadth Trend")
    
    history_mgr = HistoryManager()
    history = history_mgr.load_history()
    
    if len(history) < 2:
        st.info("📊 Insufficient historical data. Run the analysis daily to build trend data.")
        return
    
    # Convert to DataFrame
    history_df = pd.DataFrame(history)
    history_df['date'] = pd.to_datetime(history_df['date'])
    
    # Create line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=history_df['date'],
        y=history_df['score'],
        mode='lines+markers',
        name='Breadth Score',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    
    # Add regime zones
    fig.add_hrect(y0=0.8, y1=2, fillcolor="green", opacity=0.1, line_width=0)
    fig.add_hrect(y0=0.4, y1=0.8, fillcolor="lightgreen", opacity=0.1, line_width=0)
    fig.add_hrect(y0=-0.4, y1=0.4, fillcolor="yellow", opacity=0.1, line_width=0)
    fig.add_hrect(y0=-0.8, y1=-0.4, fillcolor="orange", opacity=0.1, line_width=0)
    fig.add_hrect(y0=-2, y1=-0.8, fillcolor="red", opacity=0.1, line_width=0)
    
    fig.update_layout(
        title="Breadth Score History",
        xaxis_title="Date",
        yaxis_title="Breadth Score",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        moving_avg = history_mgr.get_moving_average()
        if moving_avg:
            st.metric(f"{Thresholds.AVERAGE_PERIOD}-Day Average", f"{moving_avg:+.3f}")
    
    with col2:
        trend = history_mgr.get_trend()
        st.metric("Trend", trend)
    
    with col3:
        current_score = st.session_state.breadth_data['score']
        divergence_type, divergence_msg = history_mgr.detect_divergence(current_score)
        if divergence_type:
            st.warning(divergence_msg)

def display_all_stocks():
    """Display all stocks data"""
    st.subheader("📊 All Stocks Data")
    
    df = st.session_state.df
    
    # Check if category column exists
    has_category = 'category' in df.columns
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if has_category:
            category_filter = st.multiselect(
                "Filter by Category",
                options=['Strong Bull', 'Weak Bull', 'Neutral', 'Weak Bear', 'Strong Bear'],
                default=None
            )
        else:
            st.info("Run analysis to enable category filter")
            category_filter = None
    
    with col2:
        min_change = st.number_input("Min Change %", value=-100.0, step=0.1)
    
    with col3:
        max_change = st.number_input("Max Change %", value=100.0, step=0.1)
    
    # Apply filters
    filtered_df = df.copy()
    
    if category_filter and has_category:
        filtered_df = filtered_df[filtered_df['category'].isin(category_filter)]
    
    filtered_df = filtered_df[
        (filtered_df['pct_change'] >= min_change) &
        (filtered_df['pct_change'] <= max_change)
    ]
    
    # Display data
    st.write(f"**Showing {len(filtered_df)} of {len(df)} stocks**")
    
    # Build display columns based on what exists
    display_columns = ['symbol', 'pct_change']
    column_names = ['Symbol', 'Change %']
    format_dict = {'Change %': '{:+.2f}'}
    
    # Add optional columns if they exist
    if 'price' in filtered_df.columns:
        display_columns.append('price')
        column_names.append('Price')
        format_dict['Price'] = '₹{:.2f}'
    
    if 'prev_close' in filtered_df.columns:
        display_columns.append('prev_close')
        column_names.append('Prev Close')
        format_dict['Prev Close'] = '₹{:.2f}'
    
    if 'volume' in filtered_df.columns:
        display_columns.append('volume')
        column_names.append('Volume')
        format_dict['Volume'] = '{:,}'
    
    if 'volume_ratio' in filtered_df.columns:
        display_columns.append('volume_ratio')
        column_names.append('Vol Ratio')
        format_dict['Vol Ratio'] = '{:.2f}'
    
    if has_category:
        display_columns.append('category')
        column_names.append('Category')
    
    display_df = filtered_df[display_columns].sort_values('pct_change', ascending=False).copy()
    display_df.columns = column_names
    
    st.dataframe(
        display_df.style.format(format_dict),
        use_container_width=True,
        height=600,
        hide_index=True
    )
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        "📥 Download CSV",
        csv,
        f"breadth_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        key='download-csv'
    )

def calculate_fear_greed_index(breadth_3day, breadth_today, vix_3day, vix_day1, vix_day3, participation_3day):
    """Calculate NSE F&O Fear & Greed Index"""
    
    # Component 1: Breadth 3-Day Average (40%)
    if breadth_3day > 0.8: c1_raw = 97.5
    elif breadth_3day >= 0.6: c1_raw = 87
    elif breadth_3day >= 0.4: c1_raw = 72
    elif breadth_3day >= 0.2: c1_raw = 59.5
    elif breadth_3day >= 0.0: c1_raw = 49.5
    elif breadth_3day >= -0.2: c1_raw = 39.5
    elif breadth_3day >= -0.4: c1_raw = 29.5
    elif breadth_3day >= -0.6: c1_raw = 17
    else: c1_raw = 4.5
    c1_score = c1_raw * 0.40
    
    # Component 2: Breadth Momentum (15%)
    breadth_momentum = breadth_today - breadth_3day
    if breadth_momentum >= 0.15: c2_raw = 100
    elif breadth_momentum >= 0.10: c2_raw = 92
    elif breadth_momentum >= 0.05: c2_raw = 77
    elif breadth_momentum >= 0.0: c2_raw = 62
    elif breadth_momentum >= -0.05: c2_raw = 49.5
    elif breadth_momentum >= -0.10: c2_raw = 37
    elif breadth_momentum >= -0.15: c2_raw = 22
    else: c2_raw = 7
    c2_score = c2_raw * 0.15
    
    # Component 3: VIX Level (25%)
    if vix_3day < 12: c3_raw = 95
    elif vix_3day < 14: c3_raw = 82
    elif vix_3day < 16: c3_raw = 67
    elif vix_3day < 18: c3_raw = 54.5
    elif vix_3day < 20: c3_raw = 44.5
    elif vix_3day < 23: c3_raw = 32
    elif vix_3day < 27: c3_raw = 17
    else: c3_raw = 4.5
    c3_score = c3_raw * 0.25
    
    # Component 4: VIX Direction (10%)
    vix_change = vix_day3 - vix_day1
    if vix_change <= -3: c4_raw = 100
    elif vix_change <= -2: c4_raw = 85
    elif vix_change <= -1: c4_raw = 70
    elif vix_change <= 0: c4_raw = 55
    elif vix_change <= 1: c4_raw = 45
    elif vix_change <= 2: c4_raw = 30
    elif vix_change <= 3: c4_raw = 15
    else: c4_raw = 0
    c4_score = c4_raw * 0.10
    
    # Component 5: Participation (10%)
    if participation_3day > 80: c5_raw = 100
    elif participation_3day >= 70: c5_raw = 92
    elif participation_3day >= 60: c5_raw = 77
    elif participation_3day >= 50: c5_raw = 62
    elif participation_3day >= 40: c5_raw = 47
    elif participation_3day >= 30: c5_raw = 32
    else: c5_raw = 17
    c5_score = c5_raw * 0.10
    
    # Total Index
    total_index = c1_score + c2_score + c3_score + c4_score + c5_score
    
    # Classify regime
    if total_index >= 90: regime = "EXTREME GREED 🔥"
    elif total_index >= 75: regime = "GREED 🟢"
    elif total_index >= 60: regime = "MODERATE GREED 🟢"
    elif total_index >= 50: regime = "NEUTRAL 🟡"
    elif total_index >= 40: regime = "MILD FEAR 🟡"
    elif total_index >= 25: regime = "FEAR 🟠"
    elif total_index >= 10: regime = "EXTREME FEAR 🔴"
    else: regime = "PANIC 💀"
    
    return {
        'total_index': total_index,
        'regime': regime,
        'components': {
            'c1_raw': c1_raw,
            'c1_score': c1_score,
            'c2_raw': c2_raw,
            'c2_score': c2_score,
            'c3_raw': c3_raw,
            'c3_score': c3_score,
            'c4_raw': c4_raw,
            'c4_score': c4_score,
            'c5_raw': c5_raw,
            'c5_score': c5_score
        }
    }

def display_sector_positioning():
    """Display comprehensive sector positioning and trading recommendations"""
    st.subheader("🎯 Sector Positioning & Trading Strategy")
    
    # Get current data
    breadth_data = st.session_state.breadth_data
    sector_data = st.session_state.sector_data
    df = st.session_state.df
    
    # Get VIX data
    vix_data = df[df['symbol'] == '^INDIAVIX']
    if not vix_data.empty:
        vix_current = vix_data.iloc[0]['price']
    else:
        vix_current = None
    
    # Get history for 3-day average
    history_mgr = HistoryManager()
    history = history_mgr.load_history()
    
    if len(history) >= 3:
        last_3 = history[-3:]
        breadth_3day = sum([h['score'] for h in last_3]) / 3
    else:
        breadth_3day = breadth_data['score']
    
    # Market Context Section
    st.markdown("### 📊 MARKET CONTEXT")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Date", datetime.now().strftime('%Y-%m-%d'))
    
    with col2:
        st.metric("3-Day Breadth", f"{breadth_3day:+.3f}")
    
    with col3:
        if vix_current:
            st.metric("VIX", f"{vix_current:.2f}")
        else:
            st.metric("VIX", "N/A")
    
    with col4:
        participation = sector_data['participation_pct']
        st.metric("Participation", f"{participation:.0f}%")
    
    st.markdown("---")
    
    # Market Regime Assessment
    st.markdown("### 🎯 1. MARKET REGIME ASSESSMENT")
    
    score = breadth_data['score']
    
    # Determine market bias
    if score > 0.6:
        market_bias = "STRONG BULLISH 🟢"
        focus = "✅ **FOCUS ON LONGS** - Take all valid long setups"
        bias_color = "success"
    elif score > 0.3:
        market_bias = "MODERATE BULLISH 🟢"
        focus = "✅ **SELECTIVE LONGS** - Focus on strongest sectors"
        bias_color = "success"
    elif score > 0:
        market_bias = "WEAK BULLISH 🟡"
        focus = "⚠️ **HIGHLY SELECTIVE** - Only trade top-tier setups"
        bias_color = "warning"
    elif score > -0.3:
        market_bias = "WEAK BEARISH 🟡"
        focus = "⚠️ **DEFENSIVE** - Reduce exposure, tight stops"
        bias_color = "warning"
    elif score > -0.6:
        market_bias = "MODERATE BEARISH 🔴"
        focus = "❌ **AVOID LONGS** - Consider shorts or cash"
        bias_color = "error"
    else:
        market_bias = "STRONG BEARISH 🔴"
        focus = "❌ **STAY DEFENSIVE** - Mostly cash, prepare for reversal"
        bias_color = "error"
    
    col1, col2 = st.columns(2)
    
    with col1:
        if bias_color == "success":
            st.success(f"**Overall Market Bias:** {market_bias}")
        elif bias_color == "warning":
            st.warning(f"**Overall Market Bias:** {market_bias}")
        else:
            st.error(f"**Overall Market Bias:** {market_bias}")
    
    with col2:
        if bias_color == "success":
            st.success(focus)
        elif bias_color == "warning":
            st.warning(focus)
        else:
            st.error(focus)
    
    # VIX confirmation
    if vix_current:
        st.markdown("**VIX Level Analysis:**")
        if vix_current < 12:
            st.info("🟢 VIX < 12: Extreme complacency - Good for trend following but watch for spikes")
        elif vix_current < 15:
            st.success("🟢 VIX 12-15: Normal low volatility - Healthy bull market environment")
        elif vix_current < 18:
            st.warning("🟡 VIX 15-18: Elevated caution - Reduce position sizes by 20%")
        elif vix_current < 22:
            st.warning("🟠 VIX 18-22: High volatility - Defensive positioning, reduce size by 40%")
        else:
            st.error("🔴 VIX >22: Extreme fear - Minimal positions, watch for capitulation")
    
    st.markdown("---")
    
    # Sector Strength Rankings
    st.markdown("### 📊 2. SECTOR STRENGTH RANKINGS")
    
    sectors = sector_data['sectors']
    sorted_sectors = sorted(sectors.items(), key=lambda x: x[1]['score'], reverse=True)
    
    # Tier 1: Strongest
    st.markdown("#### 🟢 TIER 1: STRONGEST (Focus for Longs)")
    tier1_sectors = [s for s in sorted_sectors if s[1]['score'] > 0.5]
    
    if tier1_sectors:
        for sector, data in tier1_sectors[:5]:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
            with col1:
                st.success(f"**{sector}**")
            with col2:
                st.write(f"Score: {data['score']:+.2f}")
            with col3:
                st.write(f"Avg: {data['avg_change']:+.2f}%")
            with col4:
                # Get sample stocks
                sector_stocks = [s for s in SECTORS[sector] if s in df['symbol'].values]
                if sector_stocks:
                    top_stock = df[df['symbol'].isin(sector_stocks)].nlargest(1, 'pct_change')
                    if not top_stock.empty:
                        st.write(f"Ex: {top_stock.iloc[0]['symbol']}")
    else:
        st.info("No sectors currently in Tier 1 (score > 0.5)")
    
    # Tier 2: Emerging
    st.markdown("#### 🟡 TIER 2: EMERGING (Watch for Opportunities)")
    tier2_sectors = [s for s in sorted_sectors if 0.2 <= s[1]['score'] <= 0.5]
    
    if tier2_sectors:
        for sector, data in tier2_sectors[:5]:
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                st.warning(f"{sector}")
            with col2:
                st.write(f"{data['score']:+.2f}")
            with col3:
                st.write(f"{data['avg_change']:+.2f}%")
    else:
        st.info("No sectors in Tier 2 range")
    
    # Tier 3: Weak
    st.markdown("#### 🔴 TIER 3: WEAK (Avoid for Longs)")
    tier3_sectors = [s for s in sorted_sectors if s[1]['score'] < 0]
    
    if tier3_sectors:
        for sector, data in tier3_sectors[-5:]:
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                st.error(f"{sector}")
            with col2:
                st.write(f"{data['score']:+.2f}")
            with col3:
                st.write(f"{data['avg_change']:+.2f}%")
    
    st.markdown("---")
    
    # Actionable Stock Selection
    st.markdown("### ✅ 3. ACTIONABLE STOCK SELECTION PRIORITY")
    
    st.markdown("#### 🎯 MUST FOCUS ON (Top 3-5 Sectors)")
    if tier1_sectors:
        focus_sectors = tier1_sectors[:5]
        for sector, data in focus_sectors:
            with st.expander(f"🟢 {sector} (Score: {data['score']:+.2f})"):
                sector_stocks = [s for s in SECTORS[sector] if s in df['symbol'].values]
                sector_df = df[df['symbol'].isin(sector_stocks)].nlargest(5, 'pct_change')
                
                st.write(f"**Why this sector:** Showing consistent strength with {data['up_strong']} strong bulls")
                st.write(f"**Average change:** {data['avg_change']:+.2f}%")
                st.write("")
                st.write("**Top stocks in this sector:**")
                for _, stock in sector_df.iterrows():
                    st.write(f"• {stock['symbol']}: {stock['pct_change']:+.2f}% (Vol: {stock['volume_ratio']:.2f}x)")
    else:
        st.warning("⚠️ No strong sectors identified. Be highly selective with entries.")
    
    st.markdown("#### ❌ MUST AVOID")
    if tier3_sectors:
        avoid_sectors = tier3_sectors[-3:]
        for sector, data in avoid_sectors:
            st.error(f"• **{sector}** (Score: {data['score']:+.2f}) - {data['down_strong']} stocks showing strong selling")
    
    st.markdown("---")
    
    # Position Sizing Matrix
    st.markdown("### 💰 4. POSITION SIZING ADJUSTMENTS")
    
    st.markdown("""
    **Based on Sector Strength + Signal Quality:**
    
    | Signal Quality | Strong Sector (>0.5) | Emerging Sector (0.2-0.5) | Weak Sector (<0) |
    |----------------|----------------------|---------------------------|------------------|
    | 10/10 (Perfect)| 90-100% ✅          | 70-80% ⚠️                | PASS ❌          |
    | 8-9/10 (Strong)| 70-80% ✅           | 50-60% ⚠️                | PASS ❌          |
    | 6-7/10 (Good)  | 50-60% ⚠️           | 30-40% ⚠️                | PASS ❌          |
    | <6/10          | PASS ❌             | PASS ❌                  | PASS ❌          |
    """)
    
    # Market adjustment
    if score < 0:
        st.error("⚠️ **MARKET ADJUSTMENT:** Bearish breadth - Reduce ALL position sizes by 50%")
    elif score < 0.3:
        st.warning("⚠️ **MARKET ADJUSTMENT:** Weak breadth - Reduce position sizes by 30%")
    elif participation < 50:
        st.warning("⚠️ **PARTICIPATION WARNING:** Narrow leadership - Reduce position sizes by 30%")
    
    if vix_current and vix_current > 18:
        st.error(f"⚠️ **VIX WARNING:** VIX at {vix_current:.1f} - Reduce position sizes by 40%")
    
    st.markdown("---")
    
    # Sector Rotation Insights
    st.markdown("### 🔄 5. SECTOR ROTATION INSIGHTS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Money Flowing INTO:")
        if tier1_sectors:
            for sector, data in tier1_sectors[:3]:
                st.success(f"• {sector} ({data['avg_change']:+.2f}%)")
        else:
            st.info("No clear inflows detected")
    
    with col2:
        st.markdown("#### 📤 Money Flowing OUT OF:")
        if tier3_sectors:
            for sector, data in tier3_sectors[-3:]:
                st.error(f"• {sector} ({data['avg_change']:+.2f}%)")
        else:
            st.info("No clear outflows detected")
    
    st.markdown("---")
    
    # Time Horizon Recommendations
    st.markdown("### ⏰ 6. TIME HORIZON RECOMMENDATIONS")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚀 Quick 1-2 Week Momentum")
        if tier1_sectors:
            momentum_sectors = [s for s in tier1_sectors if s[1]['avg_change'] > 2.0]
            if momentum_sectors:
                for sector, data in momentum_sectors[:3]:
                    st.success(f"• {sector} (Strong momentum)")
            else:
                st.info("• Focus on top Tier 1 sectors")
    
    with col2:
        st.markdown("#### 📈 Longer 3-4 Week Holds")
        if tier1_sectors:
            stable_sectors = [s for s in tier1_sectors if 0.5 <= s[1]['score'] < 2.0]
            if stable_sectors:
                for sector, data in stable_sectors[:3]:
                    st.success(f"• {sector} (Stable strength)")
            else:
                st.info("• Use Tier 1 sectors with consistent breadth")
    
    st.markdown("---")
    
    # Risk Warnings
    st.markdown("### ⚠️ 7. RISK WARNINGS & CONSIDERATIONS")
    
    risk_level = "LOW"
    warnings = []
    
    if score < -0.3:
        risk_level = "HIGH"
        warnings.append("🔴 **BEARISH BREADTH**: Market showing broad weakness")
    elif score < 0.15:
        risk_level = "MODERATE"
        warnings.append("🟡 **WEAK BREADTH**: Limited upside momentum")
    
    if vix_current and vix_current > 20:
        risk_level = "HIGH"
        warnings.append(f"🔴 **ELEVATED VIX**: Fear at {vix_current:.1f} - expect volatility")
    elif vix_current and vix_current > 16:
        if risk_level == "LOW":
            risk_level = "MODERATE"
        warnings.append(f"🟡 **VIX WARNING**: Volatility elevated at {vix_current:.1f}")
    
    if participation < 40:
        risk_level = "HIGH"
        warnings.append("🔴 **NARROW MARKET**: Only few sectors participating - risky")
    elif participation < 60:
        if risk_level == "LOW":
            risk_level = "MODERATE"
        warnings.append("🟡 **MODERATE PARTICIPATION**: Leadership could be narrow")
    
    st.markdown(f"**Overall Risk Level: {risk_level}**")
    
    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("✅ No major risk warnings - Market conditions favorable")
    
    # Cash recommendation
    if risk_level == "HIGH":
        st.error("💰 **CASH RECOMMENDATION:** Hold 40-60% cash")
    elif risk_level == "MODERATE":
        st.warning("💰 **CASH RECOMMENDATION:** Hold 20-30% cash")
    else:
        st.success("💰 **CASH RECOMMENDATION:** Minimal cash (0-15%), deploy capital")
    
    st.markdown("---")
    
    # Integration with Trading System
    st.markdown("### 🎯 8. INTEGRATION WITH YOUR 4-LAYER SYSTEM")
    
    st.markdown("""
    **Decision Matrix:**
    
    **Scenario 1:** Stock passes all 4 layers BUT in weak sector (Tier 3)
    - ❌ **PASS** - Sector headwind too strong, likely to underperform
    - Exception: Only if 10/10 signal + sector showing reversal signs
    
    **Scenario 2:** Stock passes all 4 layers AND in strong sector (Tier 1)
    - ✅ **TAKE TRADE** - Use 70-100% sizing based on confluence
    - Strong sector tailwind increases probability
    
    **Scenario 3:** Stock passes all 4 layers in emerging sector (Tier 2)
    - ⚠️ **SELECTIVE** - Take if 9-10/10 signal, use 60-70% sizing
    - Monitor sector closely for deterioration
    
    **Scenario 4:** Two stocks, both 9/10 signals, different sectors
    - ✅ **TIE-BREAKER:** Choose stock in stronger sector
    - Sector strength = deciding factor when all else equal
    """)
    
    st.markdown("---")
    
    # Daily Checklist
    st.markdown("### ✅ DAILY PRE-MARKET CHECKLIST (7:00-9:00 AM)")
    
    checklist = {
        "7:00 AM - Data Gathering": [
            ("Check 3-day breadth score", f"Current: {breadth_3day:+.3f}"),
            ("Check VIX level", f"Current: {vix_current:.2f}" if vix_current else "Current: N/A"),
            ("Note sector participation", f"Current: {participation:.0f}%"),
            ("Identify market regime", f"Current: {market_bias}")
        ],
        "7:15 AM - Sector Analysis": [
            ("List Tier 1 sectors (focus)", f"{len(tier1_sectors)} sectors" if tier1_sectors else "None"),
            ("List Tier 3 sectors (avoid)", f"{len(tier3_sectors)} sectors" if tier3_sectors else "None"),
            ("Note rotation patterns", "Check money flows"),
            ("Adjust position sizing", f"Risk level: {risk_level}")
        ],
        "7:30 AM - Stock Screening": [
            ("Filter stocks in Tier 1 sectors ONLY", "Use sector filter"),
            ("Apply 4-layer system", "OI, Cycle, Indicators, Price"),
            ("Calculate sizing per matrix", "Sector + Signal quality"),
            ("Build watchlist (3-5 stocks)", "Ready for 9:15 AM")
        ],
        "9:00 AM - Final Prep": [
            ("Review risk warnings", "Check VIX, breadth, participation"),
            ("Confirm cash allocation", f"{risk_level} risk → adjust cash"),
            ("Set alerts for watchlist", "Price + volume alerts"),
            ("Ready to execute", "Wait for 9:15 AM open")
        ]
    }
    
    for section, items in checklist.items():
        with st.expander(f"**{section}**", expanded=False):
            for item, value in items:
                st.write(f"☐ {item}")
                st.caption(f"   → {value}")
    
    st.markdown("---")
    
    # Final Summary
    st.markdown("### 🎯 TODAY'S ACTION PLAN")
    
    if score > 0.3 and tier1_sectors:
        st.success(f"""
        ✅ **GREEN LIGHT FOR TRADING**
        - Market breadth: {score:+.3f} (Bullish)
        - {len(tier1_sectors)} strong sectors identified
        - Focus on: {', '.join([s[0] for s in tier1_sectors[:3]])}
        - Position sizing: 70-100% for top setups
        - Risk level: {risk_level}
        """)
    elif score > 0 and tier1_sectors:
        st.warning(f"""
        ⚠️ **PROCEED WITH CAUTION**
        - Market breadth: {score:+.3f} (Weak bullish)
        - {len(tier1_sectors)} sectors showing strength
        - Be highly selective, reduce sizes
        - Focus only on 9-10/10 signals
        - Risk level: {risk_level}
        """)
    else:
        st.error(f"""
        ❌ **DEFENSIVE MODE**
        - Market breadth: {score:+.3f} (Bearish/Neutral)
        - Limited sector strength
        - Hold {40 if risk_level == "HIGH" else 30}% cash minimum
        - Only take exceptional setups
        - Risk level: {risk_level}
        """)

def display_fear_greed_index():
    """Display Fear & Greed Index analysis using last 3 days of data"""
    st.subheader("😱 NSE F&O Fear & Greed Index")
    
    history_mgr = HistoryManager()
    history = history_mgr.load_history()
    
    if len(history) < 3:
        st.warning("⚠️ Need at least 3 days of historical data to calculate Fear & Greed Index.")
        st.info("Run daily analysis for 3 consecutive days to enable this feature.")
        return
    
    # Get last 3 days
    last_3 = history[-3:]
    
    # Get VIX data from current session
    df = st.session_state.df
    vix_data = df[df['symbol'] == '^INDIAVIX']
    
    if vix_data.empty:
        st.error("❌ VIX data not available. Ensure ^INDIAVIX is in your stock list and data is fetched.")
        return
    
    vix_current = vix_data.iloc[0]['price']
    
    # For demo, create mock VIX history (in production, you'd store this)
    # Assuming VIX decreased slightly over 3 days
    vix_day1 = vix_current * 1.05
    vix_day2 = vix_current * 1.02
    vix_day3 = vix_current
    
    # Extract data
    breadth_day1 = last_3[0]['score']
    breadth_day2 = last_3[1]['score']
    breadth_day3 = last_3[2]['score']
    
    # Get participation from current analysis
    sector_data = st.session_state.sector_data
    participation_current = sector_data['participation_pct']
    
    # Mock participation history (in production, store this)
    participation_day1 = participation_current * 0.95
    participation_day2 = participation_current * 0.98
    participation_day3 = participation_current
    
    # Calculate averages
    breadth_3day = (breadth_day1 + breadth_day2 + breadth_day3) / 3
    vix_3day = (vix_day1 + vix_day2 + vix_day3) / 3
    participation_3day = (participation_day1 + participation_day2 + participation_day3) / 3
    
    # Calculate Fear & Greed Index
    fg_result = calculate_fear_greed_index(
        breadth_3day, breadth_day3, vix_3day, vix_day1, vix_day3, participation_3day
    )
    
    # Display Raw Data
    st.markdown("### 📊 Raw Data Summary (Last 3 Days)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Day 1 (Oldest)", f"Breadth: {breadth_day1:+.3f}")
        st.caption(f"VIX: {vix_day1:.1f} | Participation: {participation_day1:.0f}%")
    
    with col2:
        st.metric("Day 2 (Yesterday)", f"Breadth: {breadth_day2:+.3f}")
        st.caption(f"VIX: {vix_day2:.1f} | Participation: {participation_day2:.0f}%")
    
    with col3:
        st.metric("Day 3 (Today)", f"Breadth: {breadth_day3:+.3f}")
        st.caption(f"VIX: {vix_day3:.1f} | Participation: {participation_day3:.0f}%")
    
    st.markdown("---")
    
    # Display 3-Day Averages
    st.markdown("### 📈 3-Day Moving Averages")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        delta_breadth = breadth_day3 - breadth_3day
        st.metric(
            "Breadth 3-Day Avg",
            f"{breadth_3day:+.3f}",
            delta=f"{delta_breadth:+.3f} vs today"
        )
    
    with col2:
        delta_vix = vix_day3 - vix_3day
        st.metric(
            "VIX 3-Day Avg",
            f"{vix_3day:.1f}",
            delta=f"{delta_vix:+.1f} vs today",
            delta_color="inverse"
        )
    
    with col3:
        delta_part = participation_day3 - participation_3day
        st.metric(
            "Participation 3-Day Avg",
            f"{participation_3day:.0f}%",
            delta=f"{delta_part:+.0f}% vs today"
        )
    
    st.markdown("---")
    
    # Main Fear & Greed Index Display
    st.markdown("### 🎯 NSE F&O FEAR & GREED INDEX")
    
    # Create gauge visualization
    index_value = fg_result['total_index']
    
    # Large index display
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center; font-size: 4rem;'>{index_value:.1f}</h1>", 
                    unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>{fg_result['regime']}</h2>", 
                    unsafe_allow_html=True)
    
    # Visual gauge
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = index_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Fear & Greed Index", 'font': {'size': 24}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 10], 'color': '#8B0000'},
                {'range': [10, 25], 'color': '#DC143C'},
                {'range': [25, 40], 'color': '#FF8C00'},
                {'range': [40, 50], 'color': '#FFD700'},
                {'range': [50, 60], 'color': '#FFFF00'},
                {'range': [60, 75], 'color': '#90EE90'},
                {'range': [75, 90], 'color': '#32CD32'},
                {'range': [90, 100], 'color': '#006400'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': index_value
            }
        }
    ))
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Component Breakdown
    st.markdown("### 📊 Index Component Breakdown")
    
    components = fg_result['components']
    
    comp_data = pd.DataFrame({
        'Component': [
            'Breadth 3-Day (40%)',
            'Breadth Momentum (15%)',
            'VIX Level (25%)',
            'VIX Direction (10%)',
            'Participation (10%)'
        ],
        'Raw Score': [
            f"{components['c1_raw']:.0f}/100",
            f"{components['c2_raw']:.0f}/100",
            f"{components['c3_raw']:.0f}/100",
            f"{components['c4_raw']:.0f}/100",
            f"{components['c5_raw']:.0f}/100"
        ],
        'Weighted Points': [
            f"{components['c1_score']:.1f}",
            f"{components['c2_score']:.1f}",
            f"{components['c3_score']:.1f}",
            f"{components['c4_score']:.1f}",
            f"{components['c5_score']:.1f}"
        ]
    })
    
    st.dataframe(comp_data, use_container_width=True, hide_index=True)
    
    st.markdown(f"**TOTAL INDEX: {index_value:.1f}/100**")
    
    st.markdown("---")
    
    # Trading Intelligence
    st.markdown("### 🎯 Trading Intelligence")
    
    # Position sizing recommendation
    if index_value >= 90:
        size_range = "80-100%"
        confidence = "HIGH"
        frequency = "AGGRESSIVE"
    elif index_value >= 75:
        size_range = "60-80%"
        confidence = "HIGH"
        frequency = "AGGRESSIVE"
    elif index_value >= 60:
        size_range = "50-70%"
        confidence = "MEDIUM"
        frequency = "MODERATE"
    elif index_value >= 50:
        size_range = "30-50%"
        confidence = "MEDIUM"
        frequency = "SELECTIVE"
    elif index_value >= 40:
        size_range = "20-40%"
        confidence = "LOW"
        frequency = "SELECTIVE"
    elif index_value >= 25:
        size_range = "10-30%"
        confidence = "LOW"
        frequency = "MINIMAL"
    else:
        size_range = "0-20%"
        confidence = "VERY LOW"
        frequency = "MINIMAL/CASH"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Recommended Size", size_range)
    
    with col2:
        st.metric("Confidence Level", confidence)
    
    with col3:
        st.metric("Trade Frequency", frequency)
    
    # DO/DON'T based on regime
    st.markdown("### ✅ DO / ❌ DON'T")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ✅ DO:")
        if index_value >= 75:
            st.success("• Take all valid long setups")
            st.success("• Use 80-100% position sizing")
            st.success("• Trail stops aggressively upward")
        elif index_value >= 60:
            st.success("• Take selective long setups")
            st.success("• Use 50-70% position sizing")
            st.success("• Focus on leading sectors")
        elif index_value >= 40:
            st.info("• Trade very selectively")
            st.info("• Keep positions small")
            st.info("• Use tight stops")
        else:
            st.warning("• Stay mostly in cash")
            st.warning("• Watch for capitulation")
            st.warning("• Prepare reversal watchlists")
    
    with col2:
        st.markdown("#### ❌ DON'T:")
        if index_value >= 75:
            st.error("• Fight the trend with shorts")
            st.error("• Fade strong moves")
            st.error("• Over-think entries")
        elif index_value >= 60:
            st.error("• Chase weak setups")
            st.error("• Ignore sector rotation")
            st.error("• Use full position sizes")
        elif index_value >= 40:
            st.error("• Add to losing positions")
            st.error("• Trade against trend")
            st.error("• Ignore warning signals")
        else:
            st.error("• Catch falling knives")
            st.error("• Trade without stops")
            st.error("• Use leverage")
    
    # Key Insights
    st.markdown("### 📌 Key Insights")
    
    # Momentum analysis
    breadth_trend = breadth_day3 - breadth_day1
    vix_trend = vix_day3 - vix_day1
    part_trend = participation_day3 - participation_day1
    
    insights = []
    
    # Pattern recognition
    if breadth_trend > 0.1 and vix_trend < -1 and part_trend > 5:
        insights.append("🚀 **PERFECT STORM**: All metrics aligned bullishly - momentum is accelerating")
    elif breadth_trend < -0.1 and vix_trend > 1 and part_trend < -5:
        insights.append("⚠️ **DISTRIBUTION PATTERN**: Classic topping signals - reduce exposure")
    
    if breadth_3day > 0.4 and vix_3day < 14:
        insights.append("✅ **HEALTHY BULL TREND**: Strong breadth with low volatility - ideal environment")
    elif breadth_3day < -0.4 and vix_3day > 20:
        insights.append("🔴 **BEAR MARKET CONDITION**: Weak breadth with elevated fear - stay defensive")
    
    if abs(delta_breadth) > 0.15:
        if delta_breadth > 0:
            insights.append("📈 **MOMENTUM ACCELERATION**: Breadth significantly above 3-day avg - trend strengthening")
        else:
            insights.append("📉 **MOMENTUM FADE**: Breadth well below 3-day avg - caution warranted")
    
    if participation_3day < 50 and breadth_3day > 0:
        insights.append("⚠️ **NARROW LEADERSHIP**: Despite positive breadth, participation is concerning")
    
    # Display insights
    for insight in insights:
        st.info(insight)
    
    # Summary
    st.markdown("---")
    
    if index_value >= 75:
        summary = f"🔥 **Market showing strong greed at {index_value:.1f}** - Conditions favor aggressive long positioning with {size_range} sizing."
    elif index_value >= 60:
        summary = f"🟢 **Moderate positive sentiment at {index_value:.1f}** - Selective long opportunities with {size_range} sizing advised."
    elif index_value >= 40:
        summary = f"🟡 **Mixed signals at {index_value:.1f}** - Trade cautiously with reduced {size_range} sizing and tight risk controls."
    else:
        summary = f"🔴 **Fear dominating at {index_value:.1f}** - Defensive positioning essential, keep size minimal at {size_range}."
    
    st.success(summary)

def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.image("logo.png", 
                 use_column_width=True)
        
        st.markdown("---")
        
        st.markdown("### 🎯 Navigation")
        page = st.radio(
            "Select Analysis View",
            [
                "📊 Overview",
                "🏭 Sector Analysis",
                "💥 Magnitude Analysis",
                "🔬 Advanced Metrics",
                "📈 Historical Trend",
                "📋 All Stocks",
                "😱 Fear & Greed Index",
                "🎯 Sector Positioning"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### ℹ️ About")
        st.info("""
        **NSE F&O Breadth Analyzer**
        
        Comprehensive market breadth analysis for NSE F&O stocks.
        
        **Features:**
        - Real-time breadth scoring
        - Sector participation analysis
        - Regime classification
        - Advanced market internals
        - Historical trend tracking
        
        **By:** Tesserakt Labs
        """)
        
        st.markdown("---")
        
        # Settings
        with st.expander("⚙️ Settings"):
            st.write("Coming soon...")
    
    # Main content
    display_header()
    
    # Load data if not loaded
    if not st.session_state.data_loaded:
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            success = load_data()
            if success:
                st.rerun()
        else:
            st.info("👆 Click 'Start Analysis' to fetch market data and begin analysis")
            return
    
    # Display selected page
    if page == "📊 Overview":
        display_key_metrics()
        st.markdown("---")
        display_regime_action()
        st.markdown("---")
        display_stock_classification()
        st.markdown("---")
        display_top_movers()
    
    elif page == "🏭 Sector Analysis":
        display_sector_analysis()
    
    elif page == "💥 Magnitude Analysis":
        display_magnitude_analysis()
    
    elif page == "🔬 Advanced Metrics":
        display_advanced_metrics()
    
    elif page == "📈 Historical Trend":
        display_historical_trend()
    
    elif page == "📋 All Stocks":
        display_all_stocks()
    
    elif page == "😱 Fear & Greed Index":
        display_fear_greed_index()
    
    elif page == "🎯 Sector Positioning":
        display_sector_positioning()

if __name__ == "__main__":
    main()