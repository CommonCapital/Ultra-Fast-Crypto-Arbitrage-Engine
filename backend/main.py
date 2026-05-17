import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import redis

# Internal modules
from .collectors.binance import start_binance_collector
from .collectors.bybit import start_bybit_collector
from .collectors.mexc import start_mexc_collector
from .collectors.bingx import start_bingx_collector
from .collectors.coinbase import start_coinbase_collector
from .collectors.global_metrics import start_global_metrics_collector
from .engine.arbitrage import ArbitrageDetector
from .integrations.deepseek import generate_narrative
from .integrations.telegram import send_telegram_alert
from .config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared state
active_connections = []
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
arb_detector = ArbitrageDetector()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def broadcast_loop():
    """Background task to broadcast state to WS clients and detect arbitrage."""
    while True:
        try:
            if active_connections:
                # Fetch latest prices for pairs from Redis
                dashboard_data = []
                for pair in settings.PAIRS:
                    symbol = pair.replace('/', '')
                    prices = {}
                    for ex in ['Binance', 'Bybit', 'MEXC', 'BingX', 'Coinbase']:
                        raw_tick = redis_client.get(f"tick:{ex}:{symbol}")
                        if raw_tick:
                            prices[ex] = json.loads(raw_tick)
                    
                    if prices:
                        dashboard_data.append({
                            "pair": pair,
                            "prices": prices
                        })
                        
                        # Arbitrage check
                        opp = arb_detector.check_opportunity(pair, prices)
                        if opp:
                            # Cooldown check logic (Redis-based)
                            cooldown_key = f"cooldown:{pair}"
                            if not redis_client.get(cooldown_key):
                                logger.info(f"Arbitrage detected: {opp}")
                                
                                # Local MVP Alert Narrative (No DeepSeek/Telegram)
                                short_liq = opp.get('cb_short_liq', 0)
                                long_liq = opp.get('cb_long_liq', 0)
                                liq_diff = short_liq - long_liq
                                
                                # Pull Global Metrics
                                fng_data_str = redis_client.get("global:fng")
                                fng_str = "N/A"
                                if fng_data_str:
                                    fng = json.loads(fng_data_str)
                                    fng_str = f"{fng.get('value')} ({fng.get('class')})"
                                    
                                base_sym = symbol.replace('USDT', '')
                                cmc_vol_str = redis_client.get(f"global:cmc_vol:{base_sym}")
                                cmc_vol = "N/A"
                                if cmc_vol_str:
                                    cmc_data = json.loads(cmc_vol_str)
                                    cmc_vol = f"${cmc_data.get('volume_24h', 0):,.0f}"
                                
                                narrative = (
                                    f"🚨 LOCAL ALERT: {pair}\n"
                                    f"📈 Net Spread (Post-Fees): {opp['spread_pct']}%\n"
                                    f"🛒 Buy on {opp['buy_exchange']} at ${opp['buy_price']}\n"
                                    f"💰 Sell on {opp['sell_exchange']} at ${opp['sell_price']}\n"
                                    f"📊 Momentum: Buy Vol {round(opp.get('buy_vol', 0), 2)} | Sell Vol {round(opp.get('sell_vol', 0), 2)}\n"
                                    f"💧 Coinbase Liq Pool: Sell {round(short_liq, 2)} - Buy {round(long_liq, 2)} (Diff: +{round(liq_diff, 2)})\n"
                                    f"🌍 Global Metrics: F&G {fng_str} | CMC 24h Vol: {cmc_vol}"
                                )
                                print("\n" + "="*40)
                                print(narrative)
                                print("="*40 + "\n")
                                
                                redis_client.setex(cooldown_key, 300, "1") # 5 min cooldown
                                opp["alert_message"] = narrative
                                dashboard_data[-1]["opportunity"] = opp
                
                # Broadcast
                fng_data_str = redis_client.get("global:fng")
                fng = json.loads(fng_data_str) if fng_data_str else None
                
                for conn in active_connections:
                    await conn.send_json({
                        "type": "update", 
                        "data": dashboard_data,
                        "global": {"fng": fng}
                    })
                    
        except Exception as e:
            logger.error(f"Broadcast loop error: {e}")
            
        await asyncio.sleep(0.5) # 500ms cycle

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Crypto Arbitrage Platform MVP...")
    
    # Start background tasks
    asyncio.create_task(broadcast_loop())
    
    # Start collectors
    asyncio.create_task(start_binance_collector(redis_client, settings.PAIRS))
    asyncio.create_task(start_bybit_collector(redis_client, settings.PAIRS))
    asyncio.create_task(start_mexc_collector(redis_client, settings.PAIRS))
    asyncio.create_task(start_bingx_collector(redis_client, settings.PAIRS))
    asyncio.create_task(start_coinbase_collector(redis_client, settings.PAIRS))
    asyncio.create_task(start_global_metrics_collector(redis_client, settings.PAIRS))

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    redis_client.close()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

@app.get("/health")
def health_check():
    return {"status": "ok"}
