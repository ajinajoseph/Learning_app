import io
from unittest.mock import patch
class TestLessons:

    def test_create_lesson(
        self,
        client,
        mentor_token,
        sample_module
    ):
        res = client.post(
            "/api/lessons",
            json={
                "title":"Lesson A",
                "content":"Hello",
                "module_id":sample_module.id
            },
            headers={
                "Authorization":f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 201

    def test_create_lesson_invalid_module(
    self,
    client,
    mentor_token
):
        res = client.post(
            "/api/lessons",
            json={
                "title":"Lesson",
                "module_id":"abc"
            },
            headers={
                "Authorization":f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 404

    def test_get_lessons(
    self,
    client,
    student_token,
    sample_module,
    enrolled_student,
    sample_lesson
):

        res=client.get(
            f"/api/lessons/module/{sample_module.id}",
            headers={
                "Authorization":f"Bearer {student_token}"
            }
        )

        assert res.status_code==200

    def test_get_lessons_invalid_module(
    self,
    client,
    student_token
):

        res=client.get(
            "/api/lessons/module/abc",
            headers={
                "Authorization":f"Bearer {student_token}"
            }
        )

        assert res.status_code==404

    def test_get_lessons_without_enrollment(
    self,
    client,
    student_token,
    sample_module
):

        res=client.get(
            f"/api/lessons/module/{sample_module.id}",
            headers={
                "Authorization":f"Bearer {student_token}"
            }
        )

        assert res.status_code==403
    def test_get_lesson(
    self,
    client,
    student_token,
    enrolled_student,
    sample_lesson
):

        res=client.get(
            f"/api/lessons/{sample_lesson.id}",
            headers={
                "Authorization":f"Bearer {student_token}"
            }
        )

        assert res.status_code==200



    def test_get_invalid_lesson(
        self,
        client,
        student_token
    ):
        res = client.get(
            "/api/lessons/invalid-id",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 404


    def test_update_lesson(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        res = client.put(
            f"/api/lessons/{sample_lesson.id}",
            json={
                "title": "Updated Lesson",
                "content": "Updated Content"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 200
        data = res.get_json()
        assert data["title"] == "Updated Lesson"

    def test_update_invalid_lesson(
        self,
        client,
        mentor_token
    ):
        res = client.put(
            "/api/lessons/invalid-id",
            json={
                "title": "ABC"
            },
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 404


    def test_student_cannot_update_lesson(
        self,
        client,
        student_token,
        sample_lesson
    ):
        res = client.put(
            f"/api/lessons/{sample_lesson.id}",
            json={
                "title": "Hack"
            },
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 403


    @patch("app.routes.lesson_routes.upload_file")
    def test_upload_attachment(
        self,
        mock_upload,
        client,
        mentor_token,
        sample_lesson
    ):
        mock_upload.return_value = "lesson-attachments/file.pdf"

        data = {
            "title": "Notes",
            "file": (
                io.BytesIO(b"dummy pdf"),
                "notes.pdf"
            )
        }

        res = client.post(
            f"/api/lessons/{sample_lesson.id}/attachments",
            data=data,
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
            content_type="multipart/form-data"
        )

        assert res.status_code == 201


    @patch("app.routes.lesson_routes.upload_file")
    def test_upload_attachment_invalid_extension(
        self,
        mock_upload,
        client,
        mentor_token,
        sample_lesson
    ):
        data = {
            "file": (
                io.BytesIO(b"abc"),
                "virus.exe"
            )
        }

        res = client.post(
            f"/api/lessons/{sample_lesson.id}/attachments",
            data=data,
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
            content_type="multipart/form-data"
        )

        assert res.status_code == 400


    def test_upload_attachment_no_file(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        res = client.post(
            f"/api/lessons/{sample_lesson.id}/attachments",
            data={},
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
            content_type="multipart/form-data"
        )

        assert res.status_code == 400


    def test_delete_attachment_not_found(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        res = client.delete(
            f"/api/lessons/{sample_lesson.id}/attachments/invalid-id",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 404


    def test_upload_pdf_invalid_file(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        data = {
            "file": (
                io.BytesIO(b"abc"),
                "image.jpg"
            )
        }

        res = client.post(
            f"/api/lessons/{sample_lesson.id}/upload-pdf",
            data=data,
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
            content_type="multipart/form-data"
        )

        assert res.status_code == 400


    def test_upload_pdf_no_file(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        res = client.post(
            f"/api/lessons/{sample_lesson.id}/upload-pdf",
            data={},
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
            content_type="multipart/form-data"
        )

        assert res.status_code == 400


    def test_upload_video_invalid_extension(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        data = {
            "file": (
                io.BytesIO(b"abc"),
                "video.txt"
            )
        }

        res = client.post(
            f"/api/lessons/{sample_lesson.id}/upload-video",
            data=data,
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
            content_type="multipart/form-data"
        )

        assert res.status_code == 400


    def test_upload_video_no_file(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        res = client.post(
            f"/api/lessons/{sample_lesson.id}/upload-video",
            data={},
            headers={
                "Authorization": f"Bearer {mentor_token}"
            },
            content_type="multipart/form-data"
        )

        assert res.status_code == 400


    def test_delete_invalid_lesson(
        self,
        client,
        mentor_token
    ):
        res = client.delete(
            "/api/lessons/invalid-id",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 404


    def test_student_cannot_delete_lesson(
        self,
        client,
        student_token,
        sample_lesson
    ):
        res = client.delete(
            f"/api/lessons/{sample_lesson.id}",
            headers={
                "Authorization": f"Bearer {student_token}"
            }
        )

        assert res.status_code == 403


    def test_delete_lesson(
        self,
        client,
        mentor_token,
        sample_lesson
    ):
        res = client.delete(
            f"/api/lessons/{sample_lesson.id}",
            headers={
                "Authorization": f"Bearer {mentor_token}"
            }
        )

        assert res.status_code == 200


    def test_get_lessons_requires_auth(
        self,
        client,
        sample_module
    ):
        res = client.get(
            f"/api/lessons/module/{sample_module.id}"
        )

        assert res.status_code == 401


    def test_get_lesson_requires_auth(
        self,
        client,
        sample_lesson
    ):
        res = client.get(
            f"/api/lessons/{sample_lesson.id}"
        )

        assert res.status_code == 401

        

        

        