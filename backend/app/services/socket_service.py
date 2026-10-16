from app.extensions import socketio

class SocketService:
    @staticmethod
    def broadcast_new_message(message_model):
        """Emit real-time new message to dashboard clients."""
        try:
            socketio.emit('new_message', {
                "message": message_model.to_dict(),
                "conversation_id": message_model.conversation_id
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_conversation_update(conversation_model):
        """Emit real-time conversation state updates."""
        try:
            socketio.emit('conversation_updated', {
                "conversation": conversation_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_conversation_status_changed(conversation_model, previous_status, new_status):
        """Emit conversation_status_changed event."""
        try:
            socketio.emit('conversation_status_changed', {
                "conversation_id": conversation_model.id,
                "previous_status": previous_status,
                "new_status": new_status,
                "conversation": conversation_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_ai_status_changed(conversation_model, previous_status, new_status):
        """Emit ai_status_changed event."""
        try:
            socketio.emit('ai_status_changed', {
                "conversation_id": conversation_model.id,
                "previous_status": previous_status,
                "new_status": new_status,
                "conversation": conversation_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_human_handoff(conversation_model, reason="customer_requested_human"):
        """Emit human_handoff event."""
        try:
            socketio.emit('human_handoff', {
                "conversation_id": conversation_model.id,
                "reason": reason,
                "conversation": conversation_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_agent_message(message_model):
        """Emit agent_message event when human agent sends a message."""
        try:
            socketio.emit('agent_message', {
                "message": message_model.to_dict(),
                "conversation_id": message_model.conversation_id
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_payment_review_created(review_model):
        """Emit payment_review_created event."""
        try:
            socketio.emit('payment_review_created', {
                "payment_review": review_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_payment_review_updated(review_model):
        """Emit payment_review_updated event."""
        try:
            socketio.emit('payment_review_updated', {
                "payment_review": review_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_customer_updated(customer_model):
        """Emit customer_updated event."""
        try:
            socketio.emit('customer_updated', {
                "customer": customer_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_order_created(order_model):
        """Emit order_created event."""
        try:
            socketio.emit('order_created', {
                "order": order_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")

    @staticmethod
    def broadcast_order_updated(order_model):
        """Emit order_updated event."""
        try:
            socketio.emit('order_updated', {
                "order": order_model.to_dict()
            })
        except Exception as e:
            print(f"SocketIO emit error: {e}")
