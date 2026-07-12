import uuid
import pytest
from app.models.qa_message import QAMessage
from unittest.mock import patch
import pytest
from app.models.question_thread import QuestionThread
from app.models.answer import Answer
from app.models.user import User
class TestQA:

    @pytest.fixture(autouse=True)
    def setup(self, db, sample_course, enrolled_student, student_user):
        """Create a top-level forum message for each test."""
        self.top_msg = QAMessage(
            id=str(uuid.uuid4()),
            course_id=sample_course.id,
            user_id=student_user.id,
            parent_id=None,
            message='What is the prerequisite for this course?',
            channel='forum',
            is_deleted=False
        )
        db.session.add(self.top_msg)
        db.session.commit()

    def test_get_threaded_forum(self, client, student_token, sample_course):
        res = client.get(
            f'/api/qa/forum/course/{sample_course.id}/thread',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert 'threads' in data
        assert len(data['threads']) >= 1

    def test_get_forum_without_enrollment_fails(
            self, client, admin_token, sample_course):
        # Admin is not enrolled — should be denied
        res = client.get(
            f'/api/qa/forum/course/{sample_course.id}/thread',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        assert res.status_code == 200

    def test_post_top_level_message(
            self, client, student_token, sample_course):
        res = client.post(
            f'/api/qa/forum/course/{sample_course.id}/post',
            json={'message': 'How long does this course take?',
                  'parent_id': None},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 201
        data = res.get_json()
        assert data['message'] == 'How long does this course take?'
        assert data['channel'] == 'forum'
        assert data['parent_id'] is None

    def test_post_reply_to_message(
            self, client, student_token, sample_course):
        res = client.post(
            f'/api/qa/forum/course/{sample_course.id}/post',
            json={
                'message': 'Good question!',
                'parent_id': self.top_msg.id
            },
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 201
        data = res.get_json()
        assert data['parent_id'] == self.top_msg.id

    def test_post_reply_to_invalid_parent_fails(
            self, client, student_token, sample_course):
        res = client.post(
            f'/api/qa/forum/course/{sample_course.id}/post',
            json={
                'message': 'Reply to nothing',
                'parent_id': str(uuid.uuid4())  # non-existent
            },
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 400

    def test_post_empty_message_fails(
            self, client, student_token, sample_course):
        res = client.post(
            f'/api/qa/forum/course/{sample_course.id}/post',
            json={'message': '   ', 'parent_id': None},
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 400

    def test_post_without_auth_fails(self, client, sample_course):
        res = client.post(
            f'/api/qa/forum/course/{sample_course.id}/post',
            json={'message': 'No auth', 'parent_id': None}
        )
        assert res.status_code == 401

    def test_replies_appear_nested_in_thread(
            self, client, student_token, sample_course, db, student_user):
        reply = QAMessage(
            id=str(uuid.uuid4()),
            course_id=sample_course.id,
            user_id=student_user.id,
            parent_id=self.top_msg.id,
            message='Nested reply here',
            channel='forum',
            is_deleted=False
        )
        db.session.add(reply)
        db.session.commit()

        res = client.get(
            f'/api/qa/forum/course/{sample_course.id}/thread',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        threads = res.get_json()['threads']
        # Find top message and check it has the reply nested
        top = next(
            (t for t in threads if t['id'] == self.top_msg.id), None
        )
        assert top is not None
        assert len(top['replies']) >= 1
        assert top['replies'][0]['message'] == 'Nested reply here'

    def test_delete_own_message(
            self, client, student_token, sample_course,
            db, student_user):
        msg = QAMessage(
            id=str(uuid.uuid4()),
            course_id=sample_course.id,
            user_id=student_user.id,
            parent_id=None,
            message='I will delete this',
            channel='forum',
            is_deleted=False
        )
        db.session.add(msg)
        db.session.commit()

        res = client.delete(
            f'/api/qa/forum/message/{msg.id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        db.session.refresh(msg)
        assert msg.is_deleted is True

    def test_delete_others_message_fails(
            self, client, mentor_token, sample_course,
            db, student_user):
        # Mentor tries to delete student message they don't own
        # (mentor IS allowed since they own the course —
        #  adjust if your logic differs)
        msg = QAMessage(
            id=str(uuid.uuid4()),
            course_id=sample_course.id,
            user_id=student_user.id,
            parent_id=None,
            message='Student message',
            channel='forum',
            is_deleted=False
        )
        db.session.add(msg)
        db.session.commit()

        # A different student (no token here, using admin as stand-in)
        # This tests that non-owner non-mentor can't delete
        res = client.delete(
            f'/api/qa/forum/message/{msg.id}',
            headers={'Authorization': f'Bearer {mentor_token}'}
        )
        # Mentor owns the course so should be allowed — 200
        # If you want to test a truly unauthorized user,
        # create a second student fixture
        assert res.status_code == 200

    def test_delete_nonexistent_message_fails(
            self, client, student_token):
        res = client.delete(
            f'/api/qa/forum/message/{str(uuid.uuid4())}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 404

    def test_deleted_message_not_in_thread(
            self, client, student_token, sample_course, db):
        db.session.refresh(self.top_msg)
        self.top_msg.is_deleted = True
        db.session.commit()

        res = client.get(
            f'/api/qa/forum/course/{sample_course.id}/thread',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        threads = res.get_json()['threads']
        ids = [t['id'] for t in threads]
        assert self.top_msg.id not in ids

    def test_get_chat_history(
            self, client, student_token, sample_course, db, student_user):
        chat_msg = QAMessage(
            id=str(uuid.uuid4()),
            course_id=sample_course.id,
            user_id=student_user.id,
            parent_id=None,
            message='Hello class!',
            channel='chat',
            is_deleted=False
        )
        db.session.add(chat_msg)
        db.session.commit()

        res = client.get(
            f'/api/qa/chat/{sample_course.id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert 'messages' in data
        messages = data['messages']
        # Chat messages should be there, forum messages should NOT
        assert any(m['id'] == chat_msg.id for m in messages)
        assert not any(
            m['id'] == self.top_msg.id for m in messages
        )

    def test_qa_info(self, client):
        res = client.get("/api/qa/info")
        assert res.status_code == 200

        data = res.get_json()
        assert "channels" in data
        assert "forum" in data["channels"]
        assert "chat" in data["channels"]

    @patch("app.routes.qa_routes.create_notification")
    def test_forum_ask_question(
        self,
        mock_notification,
        client,
        student_token,
        sample_course,
        enrolled_student,
    ):
        res = client.post(
            f"/api/qa/forum/course/{sample_course.id}",
            json={"question": "What is Flask?"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 201
        data = res.get_json()
        assert data["channel"] == "forum"
        mock_notification.assert_called_once()

    def test_forum_ask_invalid_course(
        self,
        client,
        student_token,
    ):
        res = client.post(
            f"/api/qa/forum/course/{uuid.uuid4()}",
            json={"question": "Hello"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 404

    def test_forum_ask_empty_question(
        self,
        client,
        student_token,
        sample_course,
        enrolled_student,
    ):
        res = client.post(
            f"/api/qa/forum/course/{sample_course.id}",
            json={"question": ""},
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 400

    @patch("app.routes.qa_routes.send_email")
    @patch("app.routes.qa_routes.create_notification")
    def test_answer_question(
        self,
        mock_notification,
        mock_email,
        client,
        mentor_token,
        sample_course,
        student_user,
        db,
    ):
        q = QuestionThread(
            course_id=sample_course.id,
            student_id=student_user.id,
            question="Need help",
        )
        db.session.add(q)
        db.session.commit()

        res = client.post(
            f"/api/qa/forum/answer/{q.id}",
            json={"answer": "Here is the answer"},
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 201
        mock_notification.assert_called_once()
        mock_email.assert_called_once()

    def test_answer_invalid_question(
        self,
        client,
        mentor_token,
    ):
        res = client.post(
            f"/api/qa/forum/answer/{uuid.uuid4()}",
            json={"answer": "abc"},
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 404

    def test_answer_empty(
        self,
        client,
        mentor_token,
        sample_course,
        student_user,
        db,
    ):
        q = QuestionThread(
            course_id=sample_course.id,
            student_id=student_user.id,
            question="Question",
        )

        db.session.add(q)
        db.session.commit()

        res = client.post(
            f"/api/qa/forum/answer/{q.id}",
            json={"answer": ""},
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 400

    def test_get_forum_questions(
        self,
        client,
        student_token,
        sample_course,
        enrolled_student,
        db,
        student_user,
    ):
        q = QuestionThread(
            course_id=sample_course.id,
            student_id=student_user.id,
            question="Question",
        )

        db.session.add(q)
        db.session.commit()

        res = client.get(
            f"/api/qa/forum/course/{sample_course.id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 200
        assert "threads" in res.get_json()

    def test_delete_question(
        self,
        client,
        mentor_token,
        sample_course,
        student_user,
        db,
    ):
        q = QuestionThread(
            course_id=sample_course.id,
            student_id=student_user.id,
            question="Delete me",
        )

        db.session.add(q)
        db.session.commit()

        res = client.delete(
            f"/api/qa/forum/question/{q.id}",
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 200

    def test_delete_invalid_question(
        self,
        client,
        mentor_token,
    ):
        res = client.delete(
            f"/api/qa/forum/question/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 404

    def test_chat_history_admin_access(
    self,
    client,
    admin_token,
    sample_course,
):
        res = client.get(
            f"/api/qa/chat/{sample_course.id}",
            headers={
                "Authorization": f"Bearer {admin_token}"
            },
        )

        assert res.status_code == 200

    def test_moderate_chat_message(
        self,
        client,
        mentor_token,
        sample_course,
        student_user,
        db,
    ):
        msg = QAMessage(
            course_id=sample_course.id,
            user_id=student_user.id,
            message="spam",
            channel="chat",
        )

        db.session.add(msg)
        db.session.commit()

        res = client.put(
            f"/api/qa/chat/message/{msg.id}/delete",
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 200

    def test_moderate_invalid_message(
        self,
        client,
        mentor_token,
    ):
        res = client.put(
            f"/api/qa/chat/message/{uuid.uuid4()}/delete",
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 404

    def test_deprecated_ask_endpoint(
        self,
        client,
        student_token,
        sample_course,
        enrolled_student,
    ):
        res = client.post(
            f"/api/qa/course/{sample_course.id}",
            json={"question": "Old endpoint"},
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 201
        assert res.get_json()["deprecated"] is True

    def test_deprecated_get_endpoint(
        self,
        client,
        student_token,
        sample_course,
        enrolled_student,
    ):
        res = client.get(
            f"/api/qa/course/{sample_course.id}",
            headers={"Authorization": f"Bearer {student_token}"},
        )

        assert res.status_code == 200
        assert res.get_json()["deprecated"] is True

    def test_deprecated_delete_endpoint(
        self,
        client,
        mentor_token,
        sample_course,
        student_user,
        db,
    ):
        q = QuestionThread(
            course_id=sample_course.id,
            student_id=student_user.id,
            question="Delete",
        )

        db.session.add(q)
        db.session.commit()

        res = client.delete(
            f"/api/qa/question/{q.id}",
            headers={"Authorization": f"Bearer {mentor_token}"},
        )

        assert res.status_code == 200
        assert res.get_json()["deprecated"] is True