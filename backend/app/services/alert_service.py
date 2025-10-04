"""Alert service"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from ..db.models import AlertRule


class AlertService:
    """Service for alert management"""

    @staticmethod
    async def create_rule(db: Session, rule_data: Dict[str, Any]) -> AlertRule:
        """Create alert rule"""
        rule = AlertRule(**rule_data)
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    async def get_rules(db: Session) -> List[AlertRule]:
        """Get all alert rules"""
        return db.query(AlertRule).filter(AlertRule.enabled == True).all()

    @staticmethod
    async def check_condition(
        rule: AlertRule,
        current_value: float
    ) -> bool:
        """Check if alert condition is met"""
        # TODO: Implement condition evaluation
        return current_value > rule.threshold
