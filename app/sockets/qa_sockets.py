from flask_socketio import emit, join_room, leave_room

from app.extensions import db, socketio
from app.models.qa_message import QAMessage
from app.services.course_access import user_has_course_access
from app.sockets.socket_auth import get_socket_user_id


CHAT_CHANNEL = "chat"


def _chat_payload(data):
    return {"channel": CHAT_CHANNEL, **data}


@socketio.on("join_course")
def join_course(data):
    user_id = get_socket_user_id()
    if not user_id:
        emit("error", {"message": "Unauthorized"})
        return

    course_id = data.get("course_id")
    if not course_id:
        emit("error", {"message": "Course ID required"})
        return

    if not user_has_course_access(user_id, course_id):
        emit("error", {"message": "Access denied"})
        return

    join_room(course_id)
    join_room(f"course_{course_id}")
    emit("joined", _chat_payload({"course_id": course_id}))


@socketio.on("leave_course")
def leave_course(data):
    course_id = data.get("course_id")
    if not course_id:
        return

    leave_room(course_id)
    leave_room(f"course_{course_id}")


@socketio.on("send_message")
def send_message(data):
    user_id = get_socket_user_id()
    if not user_id:
        emit("error", {"message": "Unauthorized"})
        return

    course_id = data.get("course_id")
    message_text = (data.get("message") or "").strip()
    parent_id = data.get("parent_id")

    if not course_id or not message_text:
        emit("error", {"message": "Invalid message payload"})
        return

    if not user_has_course_access(user_id, course_id):
        emit("error", {"message": "Access denied"})
        return

    message = QAMessage(
        course_id=course_id,
        user_id=user_id,
        parent_id=parent_id,
        message=message_text,
        channel='chat'     # ADD THIS — distinguishes chat from forum
    )

    db.session.add(message)
    db.session.commit()

    from app.models.user import User
    user = User.query.get(user_id)
    user_name = user.name if user else data.get("user_name", "Student")

    payload = {
        "id": str(message.id),
        "message": message_text,
        "user_name": user_name,
        "created_at": message.created_at.isoformat() if message.created_at else None,
        "course_id": course_id,
        "user_id": user_id,
        "channel": "chat",
        "user": {"name": user_name}
    }

    emit("new_message", payload, room=f"course_{course_id}")
    emit("new_message", payload, room=course_id)