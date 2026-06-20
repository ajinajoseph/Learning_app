from app.extensions import db

from app.models.notification import Notification


def create_notification(
    user_id,
    title,
    message
):

    notification = Notification(
        user_id=user_id,
        title=title,
        message=message
    )

    db.session.add(notification)

    db.session.commit()

    return notification