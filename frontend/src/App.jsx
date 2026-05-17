import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { PriceMatrix } from './components/PriceMatrix';
import { ArbAlert } from './components/ArbAlert';
import { AlertLog } from './components/AlertLog';

function App() {
  const { data, status } = useWebSocket('ws://localhost:8000/ws');
  const [alerts, setAlerts] = useState([]);
  const [activePair, setActivePair] = useState('BTC/USDT');
  
  // Find the selected pair data
  const primaryPairData = data.find(p => p.pair === activePair) || (data.length > 0 ? data[0] : null);

  // Listen for new alerts in all data streams
  useEffect(() => {
    if (data && data.length > 0) {
      data.forEach(pairData => {
        if (pairData?.opportunity?.alert_message) {
          setAlerts(prev => {
            const newAlert = {
              time: new Date().toLocaleTimeString(),
              pair: pairData.pair,
              message: pairData.opportunity.alert_message
            };
            // Avoid duplicates if same message
            if (prev.length > 0 && prev[0].message === newAlert.message) return prev;
            return [newAlert, ...prev].slice(0, 50); // keep last 50
          });
        }
      });
    }
  }, [data]);

  // Unique list of pairs
  const availablePairs = data.map(p => p.pair);

  return (
    <div className="dashboard-container">
      <header>
        <h1>CRYPTO ARBITRAGE PLATFORM</h1>
        <div className="status-bar">
          <div className="pulse" style={{ backgroundColor: status === 'Connected' ? 'var(--success)' : 'var(--danger)' }}></div>
          Status: {status}
        </div>
      </header>

      <main className="main-content">
        <section className="panel">
          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', borderBottom: '1px solid #333', paddingBottom: '1rem' }}>
            {availablePairs.map(pair => (
              <button 
                key={pair}
                onClick={() => setActivePair(pair)}
                style={{
                  background: activePair === pair ? 'var(--primary)' : 'transparent',
                  color: 'white',
                  border: '1px solid var(--primary)',
                  padding: '0.5rem 1rem',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                {pair}
              </button>
            ))}
          </div>
          <h2>Live Exchange Matrix — {primaryPairData?.pair || 'Loading...'}</h2>
          <PriceMatrix prices={primaryPairData?.prices || {}} />
        </section>

        {primaryPairData?.opportunity && (
          <section className="panel" style={{ padding: 0, background: 'transparent', border: 'none', boxShadow: 'none' }}>
            <ArbAlert opportunity={primaryPairData.opportunity} />
          </section>
        )}
      </main>

      <aside>
        <div className="panel" style={{ height: '100%' }}>
          <h2>Alert History</h2>
          <AlertLog alerts={alerts} />
        </div>
      </aside>
    </div>
  );
}

export default App;

