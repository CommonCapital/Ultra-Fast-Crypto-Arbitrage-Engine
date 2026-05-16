# 📈 Ultra-Fast Crypto Arbitrage Engine

A high-performance, in-memory cryptocurrency arbitrage detection and alerting platform. 

Unlike traditional polling bots or heavy database-bound applications, this platform is optimized strictly for **velocity**. It opens persistent WebSocket connections to major exchanges, slurps live tick data and Order Book Level-2 depth directly into a Redis hot-cache, and evaluates cross-exchange spreads in sub-millisecond timeframes. 

When high-conviction opportunities are detected that pass strict fee-adjusted profitability thresholds, it dispatches human-readable alerts directly to your Terminal and a sleek React Dashboard.

---

## ✨ Core Features

* **RAM-Only Architecture**: Zero database overhead. Data is streamed via WebSockets directly into a local Redis cache for blazing-fast read/write cycles.
* **100% Real-Time Data**: Live feeds from Binance, Bybit, MEXC, BingX, Bitunix, and Coinbase.
* **Strict Mathematical Execution**:
  * **Compound Net Profit**: Calculates exact capital returns by deducting both the *Taker Buy Fee* and *Taker Sell Fee* specifically for the two exchanges involved in the spread. Guarantees a rigid minimum net profit (e.g., `0.5%`) after all slippage and commissions.
  * **Clear Growth Momentum**: Evaluates live Binance trade streams to ensure `Recent Buy Volume > Recent Sell Volume` before firing an alert.
  * **Real-Time L2 Liquidity Squeeze**: Evaluates the live Coinbase Level-2 order book dynamically, comparing the total dollar value of the Sell Liquidity pool against the Buy Liquidity pool to ensure upward price pressure.
* **Premium Dashboard**: A beautifully designed, glassmorphic React/Vite dashboard running on vanilla CSS to monitor the live Exchange Matrix and Terminal-style alert logs.

---

## 🛠 Technology Stack

| Layer | Technology |
|---|---|
| **Backend API & WebSockets** | Python 3.12, FastAPI, `websockets`, `asyncio` |
| **Hot Cache (sub-ms state)** | Redis (via local Homebrew/Docker) |
| **Frontend UI** | React (Vite), Vanilla CSS (Dark Mode/Glassmorphism) |

*(Note: PostgreSQL was intentionally removed to minimize latency and infrastructure costs.)*

---

## 🚀 Getting Started

### Prerequisites
* Python 3.11+
* Node.js 18+
* Redis (`brew install redis` or via Docker)

### 1. Installation & Setup

Clone the repository and install the backend dependencies:
```bash
git clone https://github.com/yourusername/crypto-arbitrage-platform.git
cd crypto-arbitrage-platform

# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Install Frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```env
# Optional API Keys for mocked integrations or specific exchanges
BITUNIX_API_KEY=your_bitunix_api_key_here
```
*(Binance, Bybit, MEXC, BingX, and Coinbase public websockets do not require API keys).*

### 3. Run the Platform

**Start Redis:**
```bash
redis-server --daemonize yes
# or if using docker: docker run -d -p 6379:6379 redis
```

**Start the Backend Engine:**
```bash
# From the root project directory
source .venv/bin/activate
uvicorn backend.main:app --reload
```

**Start the Frontend Dashboard:**
```bash
cd frontend
npm run dev
```
Navigate to `http://localhost:5173` to view the live exchange matrix!

---

## 🗺 Future Plans & Roadmap

This MVP is currently optimized as a high-speed alerting system for manual discretionary trading. The architecture is explicitly designed to scale into a fully automated, quantitative fund-grade system:

- [ ] **Automated Trade Execution**: Integrate the `ccxt` library and exchange API keys to automatically fire simultaneous `Market Buy` and `Market Sell` orders across exchanges the millisecond an alert triggers.
- [ ] **Machine Learning Re-Integration**: Re-introduce XGBoost and LightGBM models to predict false-breakout probabilities using historical order-book imbalance data.
- [ ] **Telegram & DeepSeek Integration**: Re-connect API hooks to broadcast alerts dynamically to private Telegram channels using LLM-generated market narratives.
- [ ] **Dynamic Fee API**: Transition from hardcoded exchange fee structures (`0.1%`) to dynamic API queries, accounting for VIP tiers and token-holding fee discounts (e.g., holding BNB on Binance).
- [ ] **DEX Expansion**: Expand websocket collectors to include on-chain decentralized exchanges (Uniswap, Raydium) to catch CEX/DEX arbitrage gaps.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.
# Ultra-Fast-Crypto-Arbitrage-Engine
