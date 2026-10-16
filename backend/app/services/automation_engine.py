from app.models import AutomationRule, Conversation, Message, InternalNote
from app.services.ai_tools import escalate_to_human
from app.extensions import db
from datetime import datetime

class AutomationEngine:
    @classmethod
    def process_event(cls, trigger_event, conversation_id, message_data=None):
        """
        Process internal automation rules without n8n.
        Triggers:
        - message_received
        - outside_hours
        - human_requested
        """
        rules = AutomationRule.query.filter_by(trigger_event=trigger_event, is_active=True).all()
        if not rules:
            return

        conv = Conversation.query.get(conversation_id)
        if not conv:
            return

        for rule in rules:
            actions = rule.actions
            for act in actions:
                act_type = act.get("type")
                if act_type == "send_reply":
                    reply_content = act.get("content", "")
                    if reply_content:
                        from app.services.socket_service import SocketService
                        auto_msg = Message(
                            conversation_id=conversation_id,
                            sender_type='system',
                            content=reply_content,
                            message_type='text'
                        )
                        db.session.add(auto_msg)
                        db.session.commit()
                        SocketService.broadcast_new_message(auto_msg)

                elif act_type == "pause_ai":
                    conv.ai_enabled = False
                    db.session.commit()

                elif act_type == "assign_agent":
                    agent_id = act.get("agent_id")
                    if agent_id:
                        conv.assigned_agent_id = agent_id
                        db.session.commit()

                elif act_type == "add_tag":
                    tag_name = act.get("tag")
                    # add tag logic if needed
