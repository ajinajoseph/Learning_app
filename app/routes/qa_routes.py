from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.extensions import db, socketio
from app.middleware.role_required import role_required
from app.models.answer import Answer
from app.models.course import Course
from app.models.qa_message import QAMessage
from app.models.question_thread import QuestionThread
from app.models.user import User, UserRole
from app.services.course_access import user_has_course_access
from app.services.email_service import send_email
from app.services.notification_service import create_notification





qa_bp = Blueprint(

    "qa",

    __name__,

    url_prefix="/api/qa",

)



FORUM_CHANNEL = "forum"

CHAT_CHANNEL = "chat"





def _can_moderate_course(user, course):

    return (

        user.role == UserRole.ADMIN

        or (

            user.role == UserRole.MENTOR

            and course.mentor_id == user.id

        )

    )





def _forum_thread_payload(question):

    answers = Answer.query.filter_by(

        question_id=question.id,

    ).all()



    return {

        "channel": FORUM_CHANNEL,

        "question": question.to_dict(),

        "answers": [answer.to_dict() for answer in answers],

    }





def _ask_forum_question(course_id, user_id):

    course = Course.query.get(course_id)



    if not course:

        return jsonify({"message": "Course not found"}), 404



    if not user_has_course_access(user_id, course_id):

        return jsonify({"message": "Enroll in the course first"}), 403



    data = request.get_json() or {}

    question_text = data.get("question", "").strip()



    if not question_text:

        return jsonify({"message": "Question is required"}), 400



    question = QuestionThread(

        course_id=course_id,

        student_id=user_id,

        question=question_text,

    )



    db.session.add(question)

    db.session.commit()



    create_notification(

        course.mentor_id,

        "New Question",

        "A student asked a question.",

    )



    return jsonify(_forum_thread_payload(question)), 201





def _answer_forum_question(question_id, user_id):

    question = QuestionThread.query.get(question_id)



    if not question:

        return jsonify({"message": "Question not found"}), 404



    course = Course.query.get(question.course_id)



    if course.mentor_id != user_id:

        return jsonify({"message": "You do not own this course"}), 403



    data = request.get_json() or {}

    answer_text = data.get("answer", "").strip()



    if not answer_text:

        return jsonify({"message": "Answer is required"}), 400



    answer = Answer(

        question_id=question_id,

        mentor_id=user_id,

        answer=answer_text,

    )



    db.session.add(answer)

    db.session.commit()



    create_notification(

        question.student_id,

        "Question Answered",

        "Your question has been answered.",

    )



    student = User.query.get(question.student_id)

    if student:

        send_email(

            student.email,

            "Question Answered",

            "Your question has received an answer.",

        )



    return jsonify({

        "channel": FORUM_CHANNEL,

        "answer": answer.to_dict(),

    }), 201





def _get_forum_questions(course_id, user_id):

    if not user_has_course_access(user_id, course_id):

        return jsonify({"message": "Access denied"}), 403



    questions = QuestionThread.query.filter_by(

        course_id=course_id,

    ).order_by(QuestionThread.created_at.asc()).all()



    return jsonify({

        "channel": FORUM_CHANNEL,

        "threads": [

            _forum_thread_payload(question)

            for question in questions

        ],

    }), 200





def _delete_forum_question(question_id, user):

    question = QuestionThread.query.get(question_id)



    if not question:

        return jsonify({"message": "Question not found"}), 404



    course = Course.query.get(question.course_id)

    if not _can_moderate_course(user, course):

        return jsonify({"message": "Access denied"}), 403



    Answer.query.filter_by(question_id=question_id).delete()

    db.session.delete(question)

    db.session.commit()



    return jsonify({

        "channel": FORUM_CHANNEL,

        "message": "Question deleted",

    }), 200





def _get_chat_history(course_id, user_id):

    if not user_has_course_access(user_id, course_id):

        return jsonify({"message": "Access denied"}), 403



    messages = QAMessage.query.filter_by(
    course_id=course_id,
    is_deleted=False,
    channel='chat'     
).order_by(QAMessage.created_at.asc()).all()



    return jsonify({

        "channel": CHAT_CHANNEL,

        "messages": [message.to_dict() for message in messages],

    }), 200





def _moderate_chat_message(message_id, user):

    message = QAMessage.query.get(message_id)



    if not message or message.is_deleted:

        return jsonify({"message": "Not found"}), 404



    course = Course.query.get(message.course_id)

    if not course or not _can_moderate_course(user, course):

        return jsonify({"message": "Access denied"}), 403



    message.is_deleted = True

    db.session.commit()



    socketio.emit(

        "message_moderated",

        {

            "channel": CHAT_CHANNEL,

            "message_id": message.id,

            "course_id": message.course_id,

        },

        room=message.course_id,

    )



    return jsonify({

        "channel": CHAT_CHANNEL,

        "message": "Message moderated",

    }), 200





@qa_bp.route("/info", methods=["GET"])

def qa_info():

    return jsonify({

        "channels": {

            FORUM_CHANNEL: {

                "description": (

                    "Structured Q&A with threaded questions and mentor answers."

                ),

                "endpoints": {

                    "list": "GET /api/qa/forum/course/<course_id>",

                    "ask": "POST /api/qa/forum/course/<course_id>",

                    "answer": "POST /api/qa/forum/answer/<question_id>",

                    "delete": "DELETE /api/qa/forum/question/<question_id>",

                },

            },

            CHAT_CHANNEL: {

                "description": (

                    "Real-time course chat over Socket.IO with message history."

                ),

                "socket_events": [

                    "join_course",

                    "leave_course",

                    "send_message",

                    "new_message",

                    "message_moderated",

                ],

                "endpoints": {

                    "history": "GET /api/qa/chat/<course_id>",

                    "moderate": "PUT /api/qa/chat/message/<message_id>/delete",

                },

            },

        },

    }), 200





@qa_bp.route("/forum/course/<course_id>", methods=["POST"])

@jwt_required()

@role_required(UserRole.STUDENT)

def forum_ask_question(course_id):

    return _ask_forum_question(course_id, get_jwt_identity())





@qa_bp.route("/forum/answer/<question_id>", methods=["POST"])

@jwt_required()

@role_required(UserRole.MENTOR)

def forum_answer_question(question_id):

    return _answer_forum_question(question_id, get_jwt_identity())





@qa_bp.route("/forum/course/<course_id>", methods=["GET"])

@jwt_required()

def forum_get_course_questions(course_id):

    return _get_forum_questions(course_id, get_jwt_identity())





@qa_bp.route("/forum/question/<question_id>", methods=["DELETE"])

@jwt_required()

@role_required(UserRole.ADMIN, UserRole.MENTOR)

def forum_delete_question(question_id):

    user = User.query.get(get_jwt_identity())

    return _delete_forum_question(question_id, user)





@qa_bp.route("/chat/<course_id>", methods=["GET"])

@jwt_required()

def course_chat(course_id):

    return _get_chat_history(course_id, get_jwt_identity())





@qa_bp.route("/chat/message/<message_id>/delete", methods=["PUT"])

@jwt_required()

@role_required(UserRole.MENTOR, UserRole.ADMIN)

def moderate_chat_message(message_id):

    user = User.query.get(get_jwt_identity())

    return _moderate_chat_message(message_id, user)





@qa_bp.route("/course/<course_id>", methods=["POST"])

@jwt_required()

@role_required(UserRole.STUDENT)

def ask_question(course_id):

    payload, status = _ask_forum_question(course_id, get_jwt_identity())

    if status == 201:

        data = payload.get_json()

        data["deprecated"] = True

        data["message"] = "Use POST /api/qa/forum/course/<course_id> instead"

        return jsonify(data), status

    return payload, status





@qa_bp.route("/answer/<question_id>", methods=["POST"])

@jwt_required()

@role_required(UserRole.MENTOR)

def answer_question(question_id):

    payload, status = _answer_forum_question(question_id, get_jwt_identity())

    if status == 201:

        data = payload.get_json()

        data["deprecated"] = True

        data["message"] = "Use POST /api/qa/forum/answer/<question_id> instead"

        return jsonify(data), status

    return payload, status





@qa_bp.route("/course/<course_id>", methods=["GET"])

@jwt_required()

def get_course_questions(course_id):

    payload, status = _get_forum_questions(course_id, get_jwt_identity())

    if status == 200:

        data = payload.get_json()

        data["deprecated"] = True

        data["message"] = "Use GET /api/qa/forum/course/<course_id> instead"

        return jsonify(data), status

    return payload, status





@qa_bp.route("/message/<message_id>/delete", methods=["PUT"])

@jwt_required()

@role_required(UserRole.MENTOR, UserRole.ADMIN)

def moderate_message(message_id):

    user = User.query.get(get_jwt_identity())

    payload, status = _moderate_chat_message(message_id, user)

    if status == 200:

        data = payload.get_json()

        data["deprecated"] = True

        data["message"] = "Use PUT /api/qa/chat/message/<message_id>/delete instead"

        return jsonify(data), status

    return payload, status





@qa_bp.route("/question/<question_id>", methods=["DELETE"])

@jwt_required()

@role_required(UserRole.ADMIN, UserRole.MENTOR)

def delete_question(question_id):

    user = User.query.get(get_jwt_identity())

    payload, status = _delete_forum_question(question_id, user)

    if status == 200:

        data = payload.get_json()

        data["deprecated"] = True

        data["message"] = "Use DELETE /api/qa/forum/question/<question_id> instead"

        return jsonify(data), status

    return payload, status

@qa_bp.route("/forum/course/<course_id>/thread", methods=["GET"])
@jwt_required()
def get_threaded_forum(course_id):
    user_id = get_jwt_identity()
    if not user_has_course_access(user_id, course_id):
        return jsonify({"message": "Access denied"}), 403

    top_level = QAMessage.query.filter_by(
    course_id=course_id,
    parent_id=None,
    is_deleted=False,
    channel='forum'        # ADD THIS
    ).order_by(QAMessage.created_at.asc()).all()

    def build_thread(msg):
        replies = QAMessage.query.filter_by(
            parent_id=msg.id,
            is_deleted=False
        ).order_by(QAMessage.created_at.asc()).all()
        data = msg.to_dict()
        data['replies'] = [build_thread(r) for r in replies]
        return data

    return jsonify({
        "threads": [build_thread(m) for m in top_level]
    })


@qa_bp.route("/forum/course/<course_id>/post", methods=["POST"])
@jwt_required()
def post_forum_message(course_id):
    user_id = get_jwt_identity()
    if not user_has_course_access(user_id, course_id):
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json() or {}
    message_text = data.get("message", "").strip()
    parent_id = data.get("parent_id", None)

    if not message_text:
        return jsonify({"message": "Message is required"}), 400

    # Validate parent if replying
    if parent_id:
        parent = QAMessage.query.get(parent_id)
        if not parent or parent.course_id != course_id or parent.is_deleted:
            return jsonify({"message": "Invalid reply target"}), 400

    msg = QAMessage(
    course_id=course_id,
    user_id=user_id,
    parent_id=parent_id,
    message=message_text,
    channel='forum'        # ADD THIS
    )
    db.session.add(msg)
    db.session.commit()

    from app.models.user import User
    user = User.query.get(user_id)
    
    # Notify mentor if it's a new top-level question
    if not parent_id:
        from app.models.course import Course
        course = Course.query.get(course_id)
        if course:
            create_notification(
                course.mentor_id,
                "New Question",
                f"{user.name if user else 'A student'} posted a question."
            )
    
    result = msg.to_dict()
    result['replies'] = []
    return jsonify(result), 201

@qa_bp.route("/forum/message/<message_id>", methods=["DELETE"])
@jwt_required()
def delete_forum_message(message_id):
    user_id = get_jwt_identity()
    
    msg = QAMessage.query.get(message_id)
    if not msg:
        return jsonify({"message": "Message not found"}), 404
    
    if msg.is_deleted:
        return jsonify({"message": "Already deleted"}), 400
    
    course = Course.query.get(msg.course_id)
    user = User.query.get(user_id)
    
    # Allow if: own message OR mentor of course OR admin
    is_owner = msg.user_id == user_id
    is_mentor = (
        user.role == UserRole.MENTOR 
        and course 
        and course.mentor_id == user_id
    )
    is_admin = user.role == UserRole.ADMIN
    
    if not (is_owner or is_mentor or is_admin):
        return jsonify({"message": "Not authorized to delete this message"}), 403
    
    # Soft delete — also soft delete all replies
    def soft_delete_recursive(message):
        message.is_deleted = True
        replies = QAMessage.query.filter_by(
            parent_id=message.id, 
            is_deleted=False
        ).all()
        for reply in replies:
            soft_delete_recursive(reply)
    
    soft_delete_recursive(msg)
    db.session.commit()
    
    return jsonify({"message": "Deleted successfully"})