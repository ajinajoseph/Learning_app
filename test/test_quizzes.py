import uuid
import pytest
from app.models.module import Module
from app.models.lesson import Lesson
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.option import Option


class TestQuizzes:

    @pytest.fixture(autouse=True)
    def setup(self, db, sample_course, enrolled_student):
        """Create module, lesson, and quiz for each test."""
        self.module = Module(
            id=str(uuid.uuid4()),
            title='Test Module',
            course_id=sample_course.id,
            sort_order=1
        )
        db.session.add(self.module)
        db.session.commit()

        self.lesson = Lesson(
            id=str(uuid.uuid4()),
            title='Test Lesson',
            content='Test content',
            module_id=self.module.id,
            sort_order=1
        )
        db.session.add(self.lesson)
        db.session.commit()

        self.quiz = Quiz(
            id=str(uuid.uuid4()),
            title='Test Quiz',
            lesson_id=self.lesson.id,
            pass_percentage=70.0
        )
        db.session.add(self.quiz)
        db.session.commit()

        self.question = Question(
            id=str(uuid.uuid4()),
            quiz_id=self.quiz.id,
            question_text='What is Python?'
        )
        db.session.add(self.question)
        db.session.commit()

        self.correct_option = Option(
            id=str(uuid.uuid4()),
            question_id=self.question.id,
            option_text='A programming language',
            is_correct=True
        )
        self.wrong_option = Option(
            id=str(uuid.uuid4()),
            question_id=self.question.id,
            option_text='A snake',
            is_correct=False
        )
        db.session.add(self.correct_option)
        db.session.add(self.wrong_option)
        db.session.commit()

    def test_get_quiz(self, client, student_token):
        res = client.get(
            f'/api/quizzes/{self.quiz.id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert 'quiz' in data
        assert 'questions' in data
        assert data['quiz']['title'] == 'Test Quiz'

    def test_get_quiz_without_auth_fails(self, client):
        res = client.get(f'/api/quizzes/{self.quiz.id}')
        assert res.status_code == 401

    def test_create_quiz(self, client, mentor_token, db, sample_course):
        # Create a lesson without a quiz
        module = Module(
            id=str(uuid.uuid4()),
            title='New Module',
            course_id=sample_course.id,
            sort_order=2
        )
        db.session.add(module)
        db.session.commit()

        lesson = Lesson(
            id=str(uuid.uuid4()),
            title='New Lesson',
            content='Content',
            module_id=module.id,
            sort_order=1
        )
        db.session.add(lesson)
        db.session.commit()

        res = client.post('/api/quizzes', json={
            'title': 'New Quiz',
            'lesson_id': lesson.id,
            'pass_percentage': 80
        }, headers={'Authorization': f'Bearer {mentor_token}'})
        assert res.status_code == 201
        data = res.get_json()
        assert data['title'] == 'New Quiz'
        assert data['pass_percentage'] == 80.0

    def test_create_quiz_as_student_fails(self, client, student_token):
        res = client.post('/api/quizzes', json={
            'title': 'Student Quiz',
            'lesson_id': self.lesson.id,
            'pass_percentage': 70
        }, headers={'Authorization': f'Bearer {student_token}'})
        assert res.status_code == 403

    def test_add_question(self, client, mentor_token):
        res = client.post('/api/quizzes/question', json={
            'quiz_id': self.quiz.id,
            'question_text': 'What is Flask?'
        }, headers={'Authorization': f'Bearer {mentor_token}'})
        assert res.status_code == 201
        data = res.get_json()
        assert data['question_text'] == 'What is Flask?'

    def test_add_option(self, client, mentor_token):
        res = client.post('/api/quizzes/option', json={
            'question_id': self.question.id,
            'option_text': 'A web framework',
            'is_correct': False
        }, headers={'Authorization': f'Bearer {mentor_token}'})
        assert res.status_code == 201

    def test_submit_quiz_correct_answer(self, client, student_token):
        res = client.post(
            f'/api/quizzes/submit/{self.quiz.id}',
            json={
                'answers': [{
                    'question_id': self.question.id,
                    'option_id': self.correct_option.id
                }]
            },
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert 'score' in data
        assert 'passed' in data
        assert data['score'] == 1
        assert data['passed'] is True

    def test_submit_quiz_wrong_answer(self, client, student_token, db):
        # Clear previous attempt if any
        from app.models.quiz_attempt import QuizAttempt
        QuizAttempt.query.filter_by(quiz_id=self.quiz.id).delete()
        db.session.commit()

        res = client.post(
            f'/api/quizzes/submit/{self.quiz.id}',
            json={
                'answers': [{
                    'question_id': self.question.id,
                    'option_id': self.wrong_option.id
                }]
            },
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data['score'] == 0
        assert data['passed'] is False

    def test_submit_quiz_twice_fails(self, client, student_token):
        # First submission
        client.post(
            f'/api/quizzes/submit/{self.quiz.id}',
            json={
                'answers': [{
                    'question_id': self.question.id,
                    'option_id': self.correct_option.id
                }]
            },
            headers={'Authorization': f'Bearer {student_token}'}
        )
        # Second submission should fail
        res = client.post(
            f'/api/quizzes/submit/{self.quiz.id}',
            json={
                'answers': [{
                    'question_id': self.question.id,
                    'option_id': self.correct_option.id
                }]
            },
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 400
        assert 'already submitted' in res.get_json()['message'].lower()

    def test_update_question(self, client, mentor_token):
        res = client.put(
            f'/api/quizzes/question/{self.question.id}',
            json={
                'question_text': 'Updated question text',
                'options': [{
                    'id': self.correct_option.id,
                    'option_text': 'Updated option',
                    'is_correct': True
                }]
            },
            headers={'Authorization': f'Bearer {mentor_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data['question']['question_text'] == 'Updated question text'

    def test_delete_question(self, client, mentor_token, db):
        new_question = Question(
            id=str(uuid.uuid4()),
            quiz_id=self.quiz.id,
            question_text='Question to delete'
        )
        db.session.add(new_question)
        db.session.commit()

        res = client.delete(
            f'/api/quizzes/question/{new_question.id}',
            headers={'Authorization': f'Bearer {mentor_token}'}
        )
        assert res.status_code == 200
        assert Question.query.get(new_question.id) is None

    def test_delete_quiz(self, client, mentor_token, db, sample_course):
        # Create separate quiz to delete
        module = Module(
            id=str(uuid.uuid4()),
            title='Delete Module',
            course_id=sample_course.id,
            sort_order=99
        )
        db.session.add(module)
        db.session.commit()

        lesson = Lesson(
            id=str(uuid.uuid4()),
            title='Delete Lesson',
            content='Content',
            module_id=module.id,
            sort_order=1
        )
        db.session.add(lesson)
        db.session.commit()

        quiz = Quiz(
            id=str(uuid.uuid4()),
            title='Quiz to Delete',
            lesson_id=lesson.id,
            pass_percentage=70.0
        )
        db.session.add(quiz)
        db.session.commit()

        res = client.delete(
            f'/api/quizzes/{quiz.id}',
            headers={'Authorization': f'Bearer {mentor_token}'}
        )
        assert res.status_code == 200
        assert Quiz.query.get(quiz.id) is None

    def test_my_quiz_attempts(self, client, student_token):
        res = client.get(
            '/api/quizzes/my-attempts',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        assert isinstance(res.get_json(), list)