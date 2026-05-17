import React, { useRef, useEffect } from 'react';

export function PriceMatrix({ prices }) {
  const prevPrices = useRef({});

  useEffect(() => {
    if (prices) {
      // Store current prices as previous for the next render
      Object.entries(prices).forEach(([exchange, data]) => {
        prevPrices.current[exchange] = data.price;
      });
    }
  }, [prices]);

  if (!prices || Object.keys(prices).length === 0) return <div className="text-muted">Waiting for data...</div>;

  // Calculate cheapest to buy (min ask) and most expensive to sell (max bid)
  let minAskExchange = null;
  let maxBidExchange = null;
  let minAsk = Infinity;
  let maxBid = -Infinity;

  Object.entries(prices).forEach(([exchange, data]) => {
    if (data.ask && data.ask > 0 && data.ask < minAsk) {
      minAsk = data.ask;
      minAskExchange = exchange;
    }
    if (data.bid && data.bid > 0 && data.bid > maxBid) {
      maxBid = data.bid;
      maxBidExchange = exchange;
    }
  });

  let spreadPct = 0;
  if (minAsk < Infinity && maxBid > -Infinity) {
    spreadPct = ((maxBid - minAsk) / minAsk) * 100;
  }

  return (
    <div className="price-matrix-container" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div className="price-matrix">
        <div className="price-row">
          {Object.entries(prices).map(([exchange, data]) => {
            const previousPrice = prevPrices.current[exchange];
            const currentPrice = data.price;
            
            let arrow = '';
            let color = 'inherit';
            
            if (previousPrice !== undefined && currentPrice !== undefined) {
              if (currentPrice > previousPrice) {
                arrow = ' ↑';
                color = 'var(--success)';
              } else if (currentPrice < previousPrice) {
                arrow = ' ↓';
                color = 'var(--danger)';
              }
            }

            const isCheapest = exchange === minAskExchange;
            const isExpensive = exchange === maxBidExchange;
            
            let cardStyle = { position: 'relative' };
            if (isCheapest) {
              cardStyle.border = '1px solid var(--success)';
              cardStyle.boxShadow = '0 0 10px rgba(0, 255, 136, 0.2)';
            } else if (isExpensive) {
              cardStyle.border = '1px solid #ff00ea'; // magenta/pink for expensive
              cardStyle.boxShadow = '0 0 10px rgba(255, 0, 234, 0.2)';
            }

            return (
              <div key={exchange} className="exchange-card" style={cardStyle}>
                {isCheapest && <div style={{ position: 'absolute', top: -10, left: 10, background: 'var(--success)', color: '#000', fontSize: '0.6rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold' }}>CHEAPEST (BUY)</div>}
                {isExpensive && <div style={{ position: 'absolute', top: -10, left: 10, background: '#ff00ea', color: '#fff', fontSize: '0.6rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 'bold' }}>MOST EXPENSIVE (SELL)</div>}
                
                <div className="exchange-name">{exchange}</div>
                <div className="exchange-price" style={{ color: color, transition: 'color 0.3s' }}>
                  ${currentPrice?.toFixed(4) || '---'} {arrow}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  B: {data.bid?.toFixed(4)} | A: {data.ask?.toFixed(4)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {spreadPct !== 0 && (
        <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Potential Gross Spread: </span>
          <span style={{ 
            fontSize: '1.2rem', 
            fontWeight: 'bold', 
            color: spreadPct > 0 ? 'var(--success)' : 'var(--danger)' 
          }}>
            {spreadPct > 0 ? '+' : ''}{spreadPct.toFixed(4)}%
          </span>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            (Buy on {minAskExchange} → Sell on {maxBidExchange})
          </div>
        </div>
      )}
    </div>
  );
}
