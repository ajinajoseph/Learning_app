import pytest
from app import create_app
from app.config.config import TestConfig
from app.extensions import db as _db
from app.models.user import User, UserRole
from app.models.course import Course, CourseLevel
from app.models.enrollment import Enrollment
from app.models.module import Module
from app.models.lesson import Lesson
import uuid


@pytest.fixture(scope='session')
def app():
    """
    Creates a test Flask app using TestConfig.
    Uses SQLite in-memory database — completely separate
    from your real PostgreSQL database.
    No real data is created, modified, or deleted.
    """
    app = create_app(config=TestConfig)

    with app.app_context():
        _db.create_all()  # creates fresh tables in SQLite memory
        yield app
        _db.session.remove()
        _db.drop_all()    # wipes everything after tests finish


@pytest.fixture(scope='function')
def db(app):
    """
    Each test function gets a clean db state.
    Rolls back any changes after each test so
    tests don't affect each other.
    """
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clean all tables between tests
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope='function')
def client(app):
    """Flask test client — makes HTTP requests without a real server."""
    return app.test_client()


# ── User fixtures ──────────────────────────────────────────────

@pytest.fixture(scope='function')
def student_user(db):
    user = User(
        id=str(uuid.uuid4()),
        name='Test Student',
        email='student@test.com',
        role=UserRole.STUDENT,
        is_approved=True,
    )
    user.set_password('Test@1234')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def mentor_user(db):
    user = User(
        id=str(uuid.uuid4()),
        name='Test Mentor',
        email='mentor@test.com',
        role=UserRole.MENTOR,
        is_approved=True,
    )
    user.set_password('Test@1234')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def admin_user(db):
    user = User(
        id=str(uuid.uuid4()),
        name='Test Admin',
        email='admin@test.com',
        role=UserRole.ADMIN,
        is_approved=True,
    )
    user.set_password('Test@1234')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_module(db, sample_course):
    module = Module(
        title="Module 1",
        course_id=sample_course.id,
        sort_order=1
    )

    db.session.add(module)
    db.session.commit()
    return module

@pytest.fixture
def sample_lesson(db, sample_module):
    lesson = Lesson(
        title="Lesson 1",
        content="Lesson Content",
        module_id=sample_module.id,
        sort_order=1
    )

    db.session.add(lesson)
    db.session.commit()
    return lesson

@pytest.fixture
def other_mentor(db):
    user = User(
        id=str(uuid.uuid4()),
        name="Other Mentor",
        email="othermentor@test.com",
        role=UserRole.MENTOR,
        is_approved=True,
    )
    user.set_password("Test@1234")
    db.session.add(user)
    db.session.commit()
    return user
# ── Token fixtures ─────────────────────────────────────────────

def get_token(client, email, password):
    res = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    return res.get_json().get('access_token')


@pytest.fixture(scope='function')
def student_token(client, student_user):
    return get_token(client, 'student@test.com', 'Test@1234')


@pytest.fixture(scope='function')
def mentor_token(client, mentor_user):
    return get_token(client, 'mentor@test.com', 'Test@1234')


@pytest.fixture(scope='function')
def admin_token(client, admin_user):
    return get_token(client, 'admin@test.com', 'Test@1234')


# ── Data fixtures ──────────────────────────────────────────────

@pytest.fixture(scope='function')
def sample_course(db, mentor_user):
    course = Course(
        id=str(uuid.uuid4()),
        title='Test Python Course',
        description='A test course for pytest',
        price=999.0,
        level=CourseLevel.BEGINNER,
        duration_hours=10.0,
        language='English',
        mentor_id=mentor_user.id,
        is_approved=True,
    )
    db.session.add(course)
    db.session.commit()
    return course


@pytest.fixture(scope='function')
def enrolled_student(db, student_user, sample_course):
    enrollment = Enrollment(
        id=str(uuid.uuid4()),
        student_id=student_user.id,
        course_id=sample_course.id,
    )
    db.session.add(enrollment)
    db.session.commit()
    return enrollment