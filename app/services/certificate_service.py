def generate_certificate_url(
    student_name,
    course_title
):

    return (
        f"https://certificate.local/"
        f"{student_name.replace(' ','_')}"
        f"_{course_title.replace(' ','_')}.pdf"
    )