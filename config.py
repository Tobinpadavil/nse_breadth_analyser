"""
Configuration file for NSE F&O Breadth Analyzer
Updated with custom 208 stock universe
"""

from pathlib import Path

# ============================================
# PROJECT PATHS
# ============================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
REPORTS_DIR = DATA_DIR / "daily_reports"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================
# FILE PATHS
# ============================================

HISTORY_FILE = DATA_DIR / "breadth_history.json"
CSV_OUTPUT = OUTPUT_DIR / "breadth_report.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "summary.txt"
EXCEL_OUTPUT = OUTPUT_DIR / "breadth_analysis.xlsx"

# ============================================
# NSE F&O STOCK UNIVERSE (208 Stocks)
# ============================================

FNO_STOCKS = [
    "^INDIAVIX",
    "PGEL", "SIEMENS", "MCX", "PNBHOUSING", "JSWSTEEL",
    "NUVAMA", "VBL", "HUDCO", "PAYTM", "LTF",
    "SAIL", "SAMMAANCAP", "BPCL", "MANAPPURAM", "KALYANKJIL",
    "TATAPOWER", "RBLBANK", "DIXON", "CDSL", "GAIL",
    "HDFCLIFE", "UNOMINDA", "BAJAJFINSV", "360ONE", "TVSMOTOR",
    "SUZLON", "ABB", "BAJFINANCE", "GMRAIRPORT", "HINDPETRO",
    "BHEL", "IIFL", "JIOFIN", "INDIGO", "VEDL",
    "ANGELONE", "AMBER", "MFSL", "VOLTAS", "ADANIGREEN",
    "IGL", "CUMMINSIND", "JSWENERGY", "SHRIRAMFIN", "NMDC",
    "COFORGE", "ASHOKLEY", "DELHIVERY", "GRASIM", "GLENMARK",
    "IREDA", "TATATECH", "OBEROIRLTY", "UNITDSPR", "ADANIENSOL",
    "APLAPOLLO", "MAZDOCK", "JUBLFOOD", "TATASTEEL", "BOSCHLTD",
    "COALINDIA", "RELIANCE", "KPITTECH", "JINDALSTEL", "KFINTECH",
    "AXISBANK", "WIPRO", "SHREECEM", "TORNTPOWER", "INFY",
    "NBCC", "BDL", "HAL", "MARUTI", "BLUESTARCO",
    "UNIONBANK", "NATIONALUM", "HINDZINC", "KOTAKBANK", "LT",
    "CHOLAFIN", "IRCTC", "BSE", "AUROPHARMA", "SUNPHARMA",
    "PNB", "ICICIPRULI", "INDIANB", "TECHM", "ULTRACEMCO",
    "BHARATFORG", "DIVISLAB", "INOXWIND", "KEI", "ETERNAL",
    "ADANIPORTS", "SOLARINDS", "NCC", "UPL", "MOTHERSON",
    "HINDALCO", "HAVELLS", "LUPIN", "HFCL", "HDFCBANK",
    "LICHSGFIN", "TCS", "TATACHEM", "FORTIS", "PPLPHARMA",
    "POLYCAB", "CYIENT", "BIOCON", "RECLTD", "DLF",
    "ZYDUSLIFE", "TITAGARH", "INDUSINDBK", "IDFCFIRSTB", "BAJAJ-AUTO",
    "TATAELXSI", "ICICIBANK", "ALKEM", "ABCAPITAL", "CROMPTON",
    "BEL", "PIDILITIND", "MUTHOOTFIN", "POLICYBZR", "SONACOMS",
    "OFSS", "PHOENIXLTD", "IRFC", "TRENT", "BANKINDIA",
    "TITAN", "PETRONET", "IEX", "CIPLA", "NESTLEIND",
    "SUPREMEIND", "HCLTECH", "BANDHANBNK", "AUBANK", "YESBANK",
    "CAMS", "CANBK", "LTIM", "GODREJPROP", "DRREDDY",
    "ONGC", "LAURUSLABS", "EXIDEIND", "HEROMOTOCO", "IOC",
    "CGPOWER", "APOLLOHOSP", "GODREJCP", "COLPAL", "DMART",
    "AMBUJACEM", "MANKIND", "SYNGENE", "NTPC", "PRESTIGE",
    "NAUKRI", "CONCOR", "PERSISTENT", "INDHOTEL", "TATACONSUM",
    "OIL", "POWERGRID", "SRF", "ICICIGI", "DABUR",
    "SBICARD", "INDUSTOWER", "M&M", "HINDUNILVR", "HDFCAMC",
    "BANKBARODA", "MAXHEALTH", "MARICO", "ITC", "PAGEIND",
    "DALBHARAT", "KAYNES", "IDEA", "LODHA", "TORNTPHARM",
    "PFC", "NHPC", "BRITANNIA", "RVNL", "FEDERALBNK",
    "MPHASIS", "PATANJALI", "TIINDIA", "SBIN", "ASIANPAINT",
    "SBILIFE", "EICHERMOT", "PIIND", "LICI", "ASTRAL",
    "ADANIENT", "BHARTIARTL", "NYKAA"
]

# ============================================
# SECTOR CLASSIFICATION
# ============================================

SECTORS = {
    "Bank": [
        "AXISBANK", "KOTAKBANK", "HDFCBANK", "ICICIBANK", "SBIN",
        "INDUSINDBK", "IDFCFIRSTB", "BANDHANBNK", "AUBANK", "YESBANK",
        "PNB", "CANBK", "UNIONBANK", "BANKINDIA", "BANKBARODA",
        "INDIANB", "FEDERALBNK", "RBLBANK"
    ],
    
    "IT & Software": [
        "TCS", "INFY", "WIPRO", "HCLTECH", "TECHM",
        "LTIM", "COFORGE", "PERSISTENT", "MPHASIS", "KPITTECH",
        "TATAELXSI", "CYIENT", "OFSS"
    ],
    
    "Auto & Auto Components": [
        "MARUTI", "TVSMOTOR", "BAJAJ-AUTO", "ASHOKLEY", "EICHERMOT",
        "M&M", "HEROMOTOCO", "EXIDEIND", "MOTHERSON", "BHARATFORG",
        "SONACOMS", "UNOMINDA"
    ],
    
    "Metal & Mining": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "JINDALSTEL",
        "SAIL", "COALINDIA", "NMDC", "NATIONALUM", "HINDZINC"
    ],
    
    "Pharma & Healthcare": [
        "SUNPHARMA", "CIPLA", "DRREDDY", "DIVISLAB", "LUPIN",
        "BIOCON", "ALKEM", "AUROPHARMA", "TORNTPHARM", "GLENMARK",
        "ZYDUSLIFE", "LAURUSLABS", "MANKIND", "SYNGENE", "PPLPHARMA",
        "APOLLOHOSP", "MAXHEALTH", "FORTIS"
    ],
    
    "Energy & Power": [
        "RELIANCE", "ONGC", "BPCL", "IOC", "HINDPETRO",
        "OIL", "GAIL", "IGL", "PETRONET", "NTPC",
        "POWERGRID", "TATAPOWER", "TORNTPOWER", "JSWENERGY", "ADANIGREEN",
        "ADANIENSOL", "SUZLON", "IREDA", "NHPC"
    ],
    
    "FMCG & Consumer": [
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR",
        "MARICO", "GODREJCP", "COLPAL", "TATACONSUM", "JUBLFOOD",
        "VBL", "PATANJALI"
    ],
    
    "Infrastructure & Construction": [
        "LT", "NCC", "NBCC", "RVNL", "IRFC",
        "TITAGARH", "MAZDOCK", "ADANIPORTS", "CONCOR", "GMRAIRPORT"
    ],
    
    "Real Estate": [
        "DLF", "GODREJPROP", "OBEROIRLTY", "PRESTIGE", "LODHA",
        "PHOENIXLTD"
    ],
    
    "Financial Services": [
        "BAJFINANCE", "BAJAJFINSV", "SHRIRAMFIN", "CHOLAFIN", "MFSL",
        "LICHSGFIN", "MUTHOOTFIN", "MANAPPURAM", "ABCAPITAL", "IIFL",
        "PNBHOUSING", "HUDCO", "RECLTD", "PFC", "NUVAMA",
        "360ONE", "SAMMAANCAP", "ANGELONE"
    ],
    
    "Insurance": [
        "SBILIFE", "HDFCLIFE", "ICICIPRULI", "ICICIGI", "LICI",
        "POLICYBZR"
    ],
    
    "Capital Goods & Defense": [
        "SIEMENS", "ABB", "BHEL", "HAL", "BEL",
        "BDL", "CUMMINSIND", "BOSCHLTD", "VOLTAS", "BLUESTARCO",
        "CROMPTON", "HAVELLS", "POLYCAB", "KEI", "PGEL"
    ],
    
    "Telecom": [
        "BHARTIARTL", "IDEA", "INDUSTOWER", "HFCL"
    ],
    
    "Cement": [
        "ULTRACEMCO", "SHREECEM", "AMBUJACEM", "DALBHARAT"
    ],
    
    "Chemicals": [
        "UPL", "SRF", "PIDILITIND", "TATACHEM", "AARTI",
        "DEEPAKNTR", "GNFC", "CHAMBAL", "COROMANDEL"
    ],
    
    "Retail & E-commerce": [
        "DMART", "TRENT", "NYKAA", "TITAN", "KALYANKJIL"
    ],
    
    "Technology & Platforms": [
        "PAYTM", "NAUKRI", "JIOFIN", "INDIGO", "IRCTC",
        "DELHIVERY", "CDSL", "BSE", "MCX", "IEX",
        "KFINTECH", "CAMS"
    ],
    
    "Industrials & Materials": [
        "GRASIM", "SUPREMEIND", "ASTRAL", "APLAPOLLO", "DIXON",
        "AMBER", "CGPOWER", "SOLARINDS", "INOXWIND", "ETERNAL",
        "KAYNES", "TATATECH", "UNITDSPR", "TIINDIA"
    ],
    
    "Hospitality & Leisure": [
        "INDHOTEL"
    ],
    
    "Asset Management": [
        "HDFCAMC"
    ],
    
    "Diversified": [
        "LTF", "ADANIENT", "PIIND", "PAGEIND"
    ]
}

# ============================================
# ANALYSIS PARAMETERS
# ============================================

class Thresholds:
    """Analysis thresholds and parameters"""
    
    # Breadth classification thresholds
    STRONG_MOVE = 2.0           # % change for strong move
    MODERATE_MOVE = 1.0         # % change for moderate move
    EXPLOSIVE_MOVE = 5.0        # % change for explosive move
    STRONG_EXPLOSIVE = 3.0      # % change between moderate and explosive
    
    # Volume thresholds
    VOLUME_MULTIPLIER = 1.0     # Volume ratio vs 20-day average
    HIGH_VOLUME = 1.5           # High volume threshold
    
    # Regime classification scores
    EXTREME_BULL = 0.8
    STRONG_BULL = 0.4
    WEAK_BULL = 0.15
    NO_TRADE_HIGH = 0.15
    NO_TRADE_LOW = -0.15
    WEAK_BEAR = -0.4
    STRONG_BEAR = -0.8
    
    # Sector participation thresholds
    HEALTHY_PARTICIPATION = 60  # % of sectors bullish
    WEAK_PARTICIPATION = 40     # % of sectors bullish
    
    # Historical analysis
    HISTORY_DAYS = 30           # Days to keep in history
    AVERAGE_PERIOD = 3          # Days for moving average

# ============================================
# REGIME DEFINITIONS
# ============================================

REGIMES = {
    "EXTREME_BULL": {
        "name": "EXTREME BULL 🚀",
        "action": "🔥 MAXIMUM AGGRESSION - Take all long setups, full sizing (100%)",
        "color": "\033[92m",  # Bright green
    },
    "STRONG_BULL": {
        "name": "STRONG BULL ✅",
        "action": "✅ Take all valid long setups, 80-100% sizing",
        "color": "\033[92m",  # Green
    },
    "WEAK_BULL": {
        "name": "WEAK BULL ⚠️",
        "action": "⚠️ Selective longs only (high RS stocks), 50% sizing",
        "color": "\033[93m",  # Yellow
    },
    "NO_TRADE": {
        "name": "NO TRADE ZONE 🚫",
        "action": "🚫 NO NEW ENTRIES - Trail winners, cut losers, cash mode",
        "color": "\033[95m",  # Orange
    },
    "WEAK_BEAR": {
        "name": "WEAK BEAR ⚠️",
        "action": "⚠️ Selective shorts only, 50% sizing, no longs",
        "color": "\033[93m",  # Yellow
    },
    "STRONG_BEAR": {
        "name": "STRONG BEAR 📉",
        "action": "📉 Take all short setups, 80-100% sizing, no longs",
        "color": "\033[91m",  # Red
    },
    "EXTREME_BEAR": {
        "name": "EXTREME BEAR 💀",
        "action": "💀 MAXIMUM SHORT AGGRESSION - Full sizing, no longs",
        "color": "\033[91m",  # Bright red
    },
}

# Reset color
RESET_COLOR = "\033[0m"

# ============================================
# DISPLAY SETTINGS
# ============================================

class Display:
    """Display and formatting settings"""
    
    # Console width
    CONSOLE_WIDTH = 80
    
    # Number of top movers to display
    TOP_MOVERS_COUNT = 10
    
    # Decimal places for display
    SCORE_DECIMALS = 3
    PERCENT_DECIMALS = 2
    RATIO_DECIMALS = 2
    
    # Progress update frequency
    PROGRESS_UPDATE_FREQUENCY = 10  # Update every N stocks

# ============================================
# STOCK COUNT VALIDATION
# ============================================

print(f"✅ Configuration loaded: {len(FNO_STOCKS)} stocks configured")
print(f"✅ Sectors defined: {len(SECTORS)} sectors")

# Verify total stocks in sectors
total_in_sectors = sum(len(stocks) for stocks in SECTORS.values())
print(f"✅ Total stocks assigned to sectors: {total_in_sectors}")

# Find stocks not assigned to any sector
all_sector_stocks = set()
for stocks in SECTORS.values():
    all_sector_stocks.update(stocks)

unassigned = set(FNO_STOCKS) - all_sector_stocks
if unassigned:
    print(f"⚠️  {len(unassigned)} stocks not assigned to sectors: {list(unassigned)[:10]}...")
else:
    print(f"✅ All stocks assigned to sectors")