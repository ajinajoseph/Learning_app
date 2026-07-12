import uuid



from app.extensions import db





class Lesson(db.Model):



    __tablename__ = "lessons"



    id = db.Column(

        db.String(36),

        primary_key=True,

        default=lambda: str(uuid.uuid4())

    )



    title = db.Column(

        db.String(200),

        nullable=False

    )



    content = db.Column(

        db.Text,

        nullable=True

    )



    video_url = db.Column(

        db.String(500),

        nullable=True

    )



    pdf_url = db.Column(

        db.String(500),

        nullable=True

    )



    module_id = db.Column(

        db.String(36),

        db.ForeignKey("modules.id"),

        nullable=False

    )



    sort_order = db.Column(

        db.Integer,

        nullable=False,

        default=0,

    )



    created_at = db.Column(

        db.DateTime,

        server_default=db.func.now()

    )



    attachments = db.relationship(

        "LessonAttachment",

        backref="lesson",

        cascade="all, delete-orphan",

        order_by="LessonAttachment.sort_order",

    )



    def to_dict(self, presign_media=False):

        video_url = self.video_url

        pdf_url = self.pdf_url



        if presign_media:

            from app.services.s3_services import resolve_media_url

            video_url = resolve_media_url(self.video_url)

            pdf_url = resolve_media_url(self.pdf_url)



        return {

            "id": self.id,

            "title": self.title,

            "content": self.content,

            "video_url": video_url,

            "pdf_url": pdf_url,

            "module_id": self.module_id,

            "sort_order": self.sort_order,

            "attachments": [

                attachment.to_dict(presign=presign_media)

                for attachment in sorted(

                    self.attachments,

                    key=lambda item: (item.sort_order, item.created_at),

                )

            ],

        }


