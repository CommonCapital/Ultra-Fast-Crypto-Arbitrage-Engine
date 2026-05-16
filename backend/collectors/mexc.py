import asyncio
import json
import logging
import websockets
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def start_mexc_collector(redis_client, pairs):
    url = "wss://wbs.mexc.com/ws"

    while True:
        try:
            async with websockets.connect(url) as ws:
                logger.info(f"Connected to MEXC WS for {pairs}")
                
                symbols = [p.replace('/', '') for p in pairs]
                sub_msg = {
                    "method": "SUBSCRIPTION",
                    "params": [f"spot@public.bookTicker.v3.api@{s}" for s in symbols]
                }
                await ws.send(json.dumps(sub_msg))

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    
                    if 'c' in data and data['c'].startswith('spot@public.bookTicker'):
                        symbol = data['s']
                        tick = {
                            "ts": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
                            "exchange": "MEXC",
                            "pair": symbol,
                            "price": float(data['d'].get('a', 0)), # approximate last via ask
                            "volume": 0, # not in bookTicker
                            "bid": float(data['d'].get('b', 0)),
                            "ask": float(data['d'].get('a', 0))
                        }
                        redis_client.set(f"tick:MEXC:{symbol}", json.dumps(tick))
                        
        except Exception as e:
            logger.error(f"MEXC WS error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)
