/**
 * Alert configuration component
 */
import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

interface AlertRule {
  id?: string;
  name: string;
  condition: string;
  threshold: number;
  enabled: boolean;
}

const AlertConfig: React.FC = () => {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [newRule, setNewRule] = useState<AlertRule>({
    name: '',
    condition: 'cost_per_hour',
    threshold: 0,
    enabled: true,
  });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      const data = await apiClient.get('/alerts/rules');
      setRules(data.rules);
    } catch (error) {
      console.error('Failed to fetch alert rules:', error);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/alerts/rules', newRule);
      setNewRule({ name: '', condition: 'cost_per_hour', threshold: 0, enabled: true });
      fetchRules();
    } catch (error) {
      console.error('Failed to create alert rule:', error);
    }
  };

  return (
    <div className="alert-config">
      <form onSubmit={handleCreateRule} className="new-alert-form">
        <input
          type="text"
          placeholder="Alert name"
          value={newRule.name}
          onChange={(e) => setNewRule({ ...newRule, name: e.target.value })}
          required
        />
        <select
          value={newRule.condition}
          onChange={(e) => setNewRule({ ...newRule, condition: e.target.value })}
        >
          <option value="cost_per_hour">Cost per hour</option>
          <option value="requests_per_minute">Requests per minute</option>
          <option value="avg_latency">Average latency</option>
        </select>
        <input
          type="number"
          placeholder="Threshold"
          value={newRule.threshold}
          onChange={(e) => setNewRule({ ...newRule, threshold: Number(e.target.value) })}
          required
        />
        <button type="submit">Create Alert</button>
      </form>

      <div className="rules-list">
        {rules.map((rule) => (
          <div key={rule.id} className="rule-item">
            <span className="rule-name">{rule.name}</span>
            <span className="rule-condition">{rule.condition}</span>
            <span className="rule-threshold">{rule.threshold}</span>
            <span className={`rule-status ${rule.enabled ? 'enabled' : 'disabled'}`}>
              {rule.enabled ? 'Enabled' : 'Disabled'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AlertConfig;
