import asyncio
import json
import logging
import websockets
from datetime import datetime, timezone
from ..config import settings

logger = logging.getLogger(__name__)

async def start_bitunix_collector(redis_client, pairs):
    if not settings.BITUNIX_API_KEY:
        logger.warning("BITUNIX_API_KEY not set. Skipping Bitunix live collector.")
        return

    url = "wss://ws.bitunix.com/ws"

    while True:
        try:
            async with websockets.connect(url) as ws:
                logger.info(f"Connected to Bitunix WS for {pairs}")
                
                # Standard Bitunix WS authentication
                auth_msg = {
                    "event": "login",
                    "params": {
                        "apikey": settings.BITUNIX_API_KEY
                    }
                }
                await ws.send(json.dumps(auth_msg))
                
                # Subscribe to tickers
                for p in pairs:
                    symbol = p.replace('/', '')
                    sub_msg = {
                        "event": "subscribe",
                        "params": {
                            "channel": f"ticker_{symbol}"
                        }
                    }
                    await ws.send(json.dumps(sub_msg))

                while True:
                    msg = await ws.recv()
                    try:
                        data = json.loads(msg)
                        
                        if data.get("ping"):
                            await ws.send(json.dumps({"pong": data["ping"]}))
                            continue
                            
                        # Parse Bitunix ticker payload
                        if "data" in data and "ticker" in str(data.get("channel", "")):
                            tick_data = data["data"]
                            channel = data.get("channel", "")
                            symbol = channel.split("_")[-1]
                            
                            tick = {
                                "ts": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
                                "exchange": "Bitunix",
                                "pair": symbol,
                                "price": float(tick_data.get('last', 0)),
                                "volume": float(tick_data.get('vol', 0)),
                                "bid": float(tick_data.get('buy', 0)),
                                "ask": float(tick_data.get('sell', 0))
                            }
                            redis_client.set(f"tick:Bitunix:{symbol}", json.dumps(tick))
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            logger.error(f"Bitunix WS error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)
