/**
 * Cost breakdown component
 */
import React, { useEffect, useState } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';

interface CostItem {
  model: string;
  provider: string;
  requests: number;
  total_cost: number;
}

const CostBreakdown: React.FC = () => {
  const { getCostBreakdown } = useAnalytics();
  const [breakdown, setBreakdown] = useState<CostItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBreakdown = async () => {
      try {
        const data = await getCostBreakdown();
        setBreakdown(data);
      } catch (error) {
        console.error('Failed to fetch cost breakdown:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBreakdown();
    const interval = setInterval(fetchBreakdown, 60000); // Refresh every 60s

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div>Loading cost breakdown...</div>;
  }

  const totalCost = breakdown.reduce((sum, item) => sum + item.total_cost, 0);

  return (
    <div className="cost-breakdown">
      <div className="total-cost">
        <h3>Total: ${totalCost.toFixed(2)}</h3>
      </div>

      <table className="breakdown-table">
        <thead>
          <tr>
            <th>Model</th>
            <th>Provider</th>
            <th>Requests</th>
            <th>Cost</th>
            <th>%</th>
          </tr>
        </thead>
        <tbody>
          {breakdown.map((item, index) => (
            <tr key={index}>
              <td>{item.model}</td>
              <td>{item.provider}</td>
              <td>{item.requests.toLocaleString()}</td>
              <td>${item.total_cost.toFixed(2)}</td>
              <td>{((item.total_cost / totalCost) * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CostBreakdown;
