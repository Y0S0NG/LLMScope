/**
 * Metrics chart component
 */
import React, { useEffect, useState } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';

interface Metrics {
  total_requests: number;
  total_tokens: number;
  total_cost: number;
  avg_latency_ms: number;
}

const MetricsChart: React.FC = () => {
  const { getMetrics } = useAnalytics();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await getMetrics();
        setMetrics(data);
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30s

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div>Loading metrics...</div>;
  }

  if (!metrics) {
    return <div>No metrics available</div>;
  }

  return (
    <div className="metrics-chart">
      <div className="metric-card">
        <h3>Total Requests</h3>
        <p className="metric-value">{metrics.total_requests.toLocaleString()}</p>
      </div>

      <div className="metric-card">
        <h3>Total Tokens</h3>
        <p className="metric-value">{metrics.total_tokens.toLocaleString()}</p>
      </div>

      <div className="metric-card">
        <h3>Total Cost</h3>
        <p className="metric-value">${metrics.total_cost.toFixed(2)}</p>
      </div>

      <div className="metric-card">
        <h3>Avg Latency</h3>
        <p className="metric-value">{metrics.avg_latency_ms.toFixed(0)}ms</p>
      </div>
    </div>
  );
};

export default MetricsChart;
