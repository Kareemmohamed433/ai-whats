from datetime import datetime
from app.extensions import db

class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(20), default='#10B981')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color
        }

class ConversationTag(db.Model):
    __tablename__ = 'conversation_tags'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)

class Conversation(db.Model):
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    platform = db.Column(db.String(30), nullable=False) # whatsapp, instagram, tiktok, telegram
    platform_conversation_id = db.Column(db.String(100), nullable=False, index=True)
    assigned_agent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # State Architecture
    conversation_status = db.Column(db.String(20), default='open', nullable=False) # open, closed
    ai_status = db.Column(db.String(20), default='active', nullable=False) # active, human_handled, disabled
    requires_human = db.Column(db.Boolean, default=False)
    welcome_sent = db.Column(db.Boolean, default=False)
    order_draft_json = db.Column(db.Text, nullable=True) # JSON transient order draft
    
    priority = db.Column(db.String(20), default='medium') # low, medium, high, urgent
    unread_count = db.Column(db.Integer, default=0)
    last_message_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)
    human_handoff_at = db.Column(db.DateTime, nullable=True)
    ai_enabled_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('Message', backref='conversation', cascade='all, delete-orphan', lazy='dynamic', order_by='Message.created_at.asc()')
    internal_notes = db.relationship('InternalNote', backref='conversation', cascade='all, delete-orphan', lazy=True)
    support_tickets = db.relationship('SupportTicket', backref='conversation', cascade='all, delete-orphan', lazy=True)
    tags_rel = db.relationship('Tag', secondary='conversation_tags', backref=db.backref('conversations', lazy='dynamic'))
    audit_logs = db.relationship('ConversationAuditLog', backref='conversation', cascade='all, delete-orphan', lazy=True)

    @property
    def order_draft(self):
        import json
        if self.order_draft_json:
            try:
                return json.loads(self.order_draft_json)
            except Exception:
                return None
        return None

    @order_draft.setter
    def order_draft(self, val):
        import json
        if val is None:
            self.order_draft_json = None
        else:
            self.order_draft_json = json.dumps(val, ensure_ascii=False)

    # Backward compatibility properties
    @property
    def status(self):
        return self.conversation_status

    @status.setter
    def status(self, val):
        if val in ['open', 'closed']:
            self.conversation_status = val

    @property
    def ai_enabled(self):
        return self.ai_status == 'active'

    @ai_enabled.setter
    def ai_enabled(self, val):
        if val:
            self.ai_status = 'active'
        else:
            self.ai_status = 'human_handled'

    def to_dict(self, include_messages=False):
        last_msg = self.messages.order_by(db.desc('created_at')).first()
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer": self.customer.to_dict() if self.customer else None,
            "platform": self.platform,
            "platform_conversation_id": self.platform_conversation_id,
            "assigned_agent_id": self.assigned_agent_id,
            "assigned_agent": self.assigned_agent.to_dict() if self.assigned_agent else None,
            "conversation_status": self.conversation_status,
            "ai_status": self.ai_status,
            "status": self.conversation_status,
            "ai_enabled": self.ai_enabled,
            "requires_human": self.requires_human,
            "welcome_sent": self.welcome_sent,
            "order_draft": self.order_draft,
            "priority": self.priority,
            "unread_count": self.unread_count,
            "last_message": last_msg.to_dict() if last_msg else None,
            "tags": [t.to_dict() for t in self.tags_rel],
            "internal_notes": [note.to_dict() for note in self.internal_notes],
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "human_handoff_at": self.human_handoff_at.isoformat() if self.human_handoff_at else None,
            "ai_enabled_at": self.ai_enabled_at.isoformat() if self.ai_enabled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "messages": [m.to_dict() for m in self.messages.all()] if include_messages else []
        }

class ConversationAuditLog(db.Model):
    __tablename__ = 'conversation_audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    actor_type = db.Column(db.String(20), default='system') # system, ai, agent, customer
    actor_id = db.Column(db.String(50), nullable=True)
    previous_ai_status = db.Column(db.String(20), nullable=True)
    new_ai_status = db.Column(db.String(20), nullable=True)
    previous_conv_status = db.Column(db.String(20), nullable=True)
    new_conv_status = db.Column(db.String(20), nullable=True)
    reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "previous_ai_status": self.previous_ai_status,
            "new_ai_status": self.new_ai_status,
            "previous_conv_status": self.previous_conv_status,
            "new_conv_status": self.new_conv_status,
            "reason": self.reason,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class InternalNote(db.Model):
    __tablename__ = 'internal_notes'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "author_id": self.author_id,
            "author_name": self.author.name if self.author else "System",
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(30), unique=True, nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='open') # open, in_progress, resolved, closed
    priority = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "ticket_number": self.ticket_number,
            "conversation_id": self.conversation_id,
            "customer_id": self.customer_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
