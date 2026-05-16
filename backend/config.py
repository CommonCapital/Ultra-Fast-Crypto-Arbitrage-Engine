import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys & URLs
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    CMC_API_KEY = os.getenv("CMC_API_KEY", "")
    NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL", "")
    
    # Engine Thresholds
    MIN_NET_SPREAD = 0.5 # 0.5% minimum profit AFTER all exchange fees are deducted
    REQUIRE_SHORT_DOMINANCE = True
    
    # Standard Taker Trading Fees per exchange (e.g. 0.001 = 0.1%)
    EXCHANGE_FEES = {
        "Binance": 0.001,
        "Bybit": 0.001,
        "MEXC": 0.001,    # often 0 for makers, but 0.1% for takers
        "BingX": 0.001,
        "Coinbase": 0.004 # Advanced trade standard taker fee
    }
    
    # Pairs to track
    PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

settings = Settings()
