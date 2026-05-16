import React, { useState, useEffect } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { PriceMatrix } from './components/PriceMatrix';
import { ArbAlert } from './components/ArbAlert';
import { AlertLog } from './components/AlertLog';

function App() {
  const { data, status } = useWebSocket('ws://localhost:8000/ws');
  const [alerts, setAlerts] = useState([]);
  
  // Extract the first pair for the primary view (e.g., BTC/USDT)
  const primaryPairData = data.length > 0 ? data[0] : null;

  // Listen for new alerts in the data stream
  useEffect(() => {
    if (primaryPairData?.opportunity?.alert_message) {
      setAlerts(prev => {
        const newAlert = {
          time: new Date().toLocaleTimeString(),
          pair: primaryPairData.pair,
          message: primaryPairData.opportunity.alert_message
        };
        // Avoid duplicates if same message
        if (prev.length > 0 && prev[0].message === newAlert.message) return prev;
        return [newAlert, ...prev].slice(0, 50); // keep last 50
      });
    }
  }, [primaryPairData]);

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
