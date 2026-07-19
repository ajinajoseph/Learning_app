from sqlalchemy import func

from app.extensions import db
from app.models.review import Review, ReviewStatus
from app.models.review_report import ReportStatus, ReviewReport

PRIOR_WEIGHT = 10
DEFAULT_GLOBAL_RATING = 3.0


def _approved_reviews(course_id):
    flagged_ids = {
        report.review_id
        for report in ReviewReport.query.filter_by(
            status=ReportStatus.PENDING,
        ).all()
    }

    reviews = Review.query.filter_by(
        course_id=course_id,
        status=ReviewStatus.APPROVED,
    ).all()

    return [review for review in reviews if review.id not in flagged_ids]


def calculate_average_rating(course_id):
    reviews = _approved_reviews(course_id)
    if not reviews:
        return 0.0

    return round(
        sum(float(review.rating) for review in reviews) / len(reviews),
        2,
    )


def calculate_weighted_rating(course_id):
    reviews = _approved_reviews(course_id)
    if not reviews:
        return 0.0

    course_avg = sum(float(review.rating) for review in reviews) / len(reviews)
    global_avg = db.session.query(
        func.avg(Review.rating),
    ).filter(
        Review.status == ReviewStatus.APPROVED,
    ).scalar() or DEFAULT_GLOBAL_RATING
    
    global_avg = float(global_avg)
    vote_count = float(len(reviews))
    weighted = (
        (vote_count / (vote_count + PRIOR_WEIGHT)) * course_avg
        + (PRIOR_WEIGHT / (vote_count + PRIOR_WEIGHT)) * global_avg
    )
    return round(weighted, 2)


def get_course_rating_stats(course_id):
    approved_reviews = _approved_reviews(course_id)

    return {
        "total_reviews": len(approved_reviews),
        "average_rating": calculate_average_rating(course_id),
        "weighted_rating": calculate_weighted_rating(course_id),

        "five_star": sum(1 for r in approved_reviews if r.rating == 5),
        "four_star": sum(1 for r in approved_reviews if r.rating == 4),
        "three_star": sum(1 for r in approved_reviews if r.rating == 3),
        "two_star": sum(1 for r in approved_reviews if r.rating == 2),
        "one_star": sum(1 for r in approved_reviews if r.rating == 1),
    }
