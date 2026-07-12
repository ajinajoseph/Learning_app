import uuid
from app.models.module import Module
from app.models.lesson import Lesson


class TestProgress:

    def test_mark_lesson_complete(self, client, student_token,
                                   enrolled_student, db, sample_course):
        module = Module(
            id=str(uuid.uuid4()),
            title='Test Module',
            course_id=sample_course.id,
            sort_order=1
        )
        db.session.add(module)
        db.session.commit()

        lesson = Lesson(
            id=str(uuid.uuid4()),
            title='Test Lesson',
            content='Test content',
            module_id=module.id,
            sort_order=1
        )
        db.session.add(lesson)
        db.session.commit()

        res = client.post(
            f'/api/progress/complete/{lesson.id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code in [200, 201]

    def test_get_course_progress(self, client, student_token,
                                  enrolled_student, sample_course):
        res = client.get(
            f'/api/progress/course/{sample_course.id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert 'completed_lessons' in data

    def test_progress_requires_enrollment(self, client, student_token):
        fake_id = str(uuid.uuid4())
        res = client.get(
            f'/api/progress/course/{fake_id}',
            headers={'Authorization': f'Bearer {student_token}'}
        )
        assert res.status_code in [403, 404]