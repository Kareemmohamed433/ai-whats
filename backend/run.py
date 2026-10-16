import os
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    print(f"🌿 Khams Sinaa AI Dashboard Backend running on http://localhost:{port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
