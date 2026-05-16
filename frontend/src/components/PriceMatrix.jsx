import React from 'react';

export function PriceMatrix({ prices }) {
  if (!prices || Object.keys(prices).length === 0) return <div className="text-muted">Waiting for data...</div>;

  return (
    <div className="price-matrix">
      <div className="price-row">
        {Object.entries(prices).map(([exchange, data]) => (
          <div key={exchange} className="exchange-card">
            <div className="exchange-name">{exchange}</div>
            <div className="exchange-price">${data.price?.toFixed(4) || '---'}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              B: {data.bid?.toFixed(4)} | A: {data.ask?.toFixed(4)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
