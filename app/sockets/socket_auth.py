from flask import request
from flask_jwt_extended import decode_token
from app.extensions import socketio

_socket_users = {}


def authenticate_socket(auth):
    if not auth or not isinstance(auth, dict):
        return None

    token = auth.get("token")
    if not token:
        return None

    try:
        decoded = decode_token(token)
        return decoded.get("sub")
    except Exception:
        return None


def get_socket_user_id():
    return _socket_users.get(request.sid)


@socketio.on("connect")
def handle_connect(auth):
    user_id = authenticate_socket(auth)
    if not user_id:
        return False

    _socket_users[request.sid] = user_id
    return True


@socketio.on("disconnect")
def handle_disconnect():
    _socket_users.pop(request.sid, None)
