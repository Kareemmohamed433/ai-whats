import json
from datetime import datetime
from app.extensions import db

class AutomationRule(db.Model):
    __tablename__ = 'automation_rules'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    trigger_event = db.Column(db.String(50), nullable=False) # message_received, outside_hours, keyword_matched, human_requested
    conditions_json = db.Column(db.Text, nullable=True) # JSON criteria
    actions_json = db.Column(db.Text, nullable=False) # JSON actions: send_reply, pause_ai, assign_agent, add_tag
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        conds = {}
        acts = []
        if self.conditions_json:
            try:
                conds = json.loads(self.conditions_json)
            except Exception:
                conds = {}
        if self.actions_json:
            try:
                acts = json.loads(self.actions_json)
            except Exception:
                acts = []

        return {
            "id": self.id,
            "name": self.name,
            "trigger_event": self.trigger_event,
            "conditions": conds,
            "actions": acts,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
