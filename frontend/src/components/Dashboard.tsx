/**
 * Main dashboard component
 */
import React from 'react';
import MetricsChart from './MetricsChart';
import LiveFeed from './LiveFeed';
import CostBreakdown from './CostBreakdown';
import AlertConfig from './AlertConfig';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <header>
        <h1>LLMScope Dashboard</h1>
      </header>

      <div className="dashboard-grid">
        <section className="metrics-section">
          <h2>Metrics Overview</h2>
          <MetricsChart />
        </section>

        <section className="live-feed-section">
          <h2>Live Feed</h2>
          <LiveFeed />
        </section>

        <section className="cost-section">
          <h2>Cost Breakdown</h2>
          <CostBreakdown />
        </section>

        <section className="alerts-section">
          <h2>Alert Configuration</h2>
          <AlertConfig />
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
