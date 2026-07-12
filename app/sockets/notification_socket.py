from flask_socketio import emit, join_room

from app.extensions import socketio
from app.sockets.socket_auth import get_socket_user_id


@socketio.on("join")
def handle_join(data):
    user_id = get_socket_user_id()
    if not user_id:
        emit("error", {"message": "Unauthorized"})
        return

    join_room(user_id)
