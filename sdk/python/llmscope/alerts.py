"""Alerts API module"""
from typing import List, Union
from .client import BaseClient
from .models import AlertRule


class AlertsClient(BaseClient):
    """Client for LLMScope Alerts API"""

    def list_rules(self) -> List[dict]:
        """
        List all alert rules

        Returns:
            List of alert rules

        Example:
            ```python
            rules = client.alerts.list_rules()
            for rule in rules:
                print(f"{rule['name']}: {rule['condition']} > {rule['threshold']}")
            ```
        """
        return self._get("/api/v1/alerts/rules")

    def create_rule(self, rule: Union[AlertRule, dict]) -> dict:
        """
        Create new alert rule

        Args:
            rule: Alert rule configuration as AlertRule object or dict

        Returns:
            Created alert rule

        Example:
            ```python
            from llmscope.models import AlertRule

            # Create alert for high latency
            rule = AlertRule(
                name="High Latency Alert",
                condition="avg_latency_ms",
                threshold=2000.0,
                enabled=True
            )

            created_rule = client.alerts.create_rule(rule)
            print(f"Created rule: {created_rule['id']}")
            ```

            ```python
            # Or use a dict
            rule = {
                "name": "High Cost Alert",
                "condition": "total_cost_usd",
                "threshold": 100.0,
                "enabled": True
            }

            created_rule = client.alerts.create_rule(rule)
            ```
        """
        if isinstance(rule, AlertRule):
            rule_data = rule.model_dump(exclude_none=True)
        else:
            rule_data = rule

        return self._post("/api/v1/alerts/rules", json=rule_data)