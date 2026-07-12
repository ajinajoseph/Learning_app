import pytest
class TestAuth:
    def test_register_student(self, client):
        res = client.post('/api/auth/register', json={
            'name': 'New Student',
            'email': 'newstudent@test.com',
            'password': 'Test@1234',
            'role': 'student'
        })
        assert res.status_code == 201
        data = res.get_json()
        assert data["message"] == "User registered successfully"

    def test_register_duplicate_email(self, client, student_user):
        res = client.post('/api/auth/register', json={
            'name': 'Duplicate',
            'email': 'student@test.com',
            'password': 'Test@1234',
            'role': 'student'
        })
        assert res.status_code == 400
        data = res.get_json()
        assert data["message"] == "Email already exists"

    def test_login_success(self, client, student_user):
        res = client.post('/api/auth/login', json={
            'email': 'student@test.com',
            'password': 'Test@1234'
        })
        print(res.get_json())

        assert res.status_code == 200

    def test_login_wrong_password(self, client, student_user):
        res = client.post('/api/auth/login', json={
            'email': 'student@test.com',
            'password': 'wrongpassword'
        })
        assert res.status_code == 401

    def test_login_nonexistent_user(self, client):
        res = client.post('/api/auth/login', json={
            'email': 'nobody@test.com',
            'password': 'Test@1234'
        })
        assert res.status_code == 401

    def test_get_profile(self, client, student_token):
        res = client.get('/api/auth/profile', headers={
            'Authorization': f'Bearer {student_token}'
        })
        assert res.status_code == 200
        data = res.get_json()
        assert data['email'] == 'student@test.com'

    def test_get_profile_unauthorized(self, client):
        res = client.get('/api/auth/profile')
        assert res.status_code == 401

    def test_refresh_token(self, client, student_user):
        login_res = client.post('/api/auth/login', json={
            'email': 'student@test.com',
            'password': 'Test@1234'
        })
        refresh_token = login_res.get_json()['refresh_token']
        
        res = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })
        print(res.get_json())
        data = res.get_json()
        assert "access_token" in data