from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime


def generate_certificate_pdf(student_name, course_name, certificate_id):

    buffer = BytesIO()

    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 150, "CERTIFICATE OF COMPLETION")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 250, "This is to certify that")
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 300, student_name)
    c.setFont("Helvetica", 16)
    c.drawCentredString(
        width / 2,
        height - 350,
        f"has successfully completed the course"
    )
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width / 2, height - 400, course_name)
    c.setFont("Helvetica", 12)
    c.drawCentredString(
        width / 2,
        height - 500,
        f"Certificate ID: {certificate_id}"
    )

    c.drawCentredString(
        width / 2,
        height - 530,
        f"Issued on: {datetime.utcnow().strftime('%Y-%m-%d')}"
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer