import eventlet
eventlet.monkey_patch() 
import os
from app import create_app
from app.extensions import socketio

app = create_app()
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_ENV") == "development",
        allow_unsafe_werkzeug=True,
    )