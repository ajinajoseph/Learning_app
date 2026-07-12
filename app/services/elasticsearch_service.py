from flask import current_app

from app.extensions import db
from app.models.course import Course
from app.models.user import User, UserRole
from app.services.review_service import calculate_weighted_rating

COURSES_INDEX = "courses"
MENTORS_INDEX = "mentors"

SYNONYMS = [
    "js, javascript",
    "py, python",
    "ml, machine learning",
    "ai, artificial intelligence",
    "beginner, basics, intro, introduction, starter",
    "intermediate, medium, moderate",
    "advanced, expert, pro, professional",
    "course, class, tutorial, training",
    "mentor, instructor, teacher, coach",
]

INDEX_SETTINGS = {
    "analysis": {
        "filter": {
            "course_synonyms": {
                "type": "synonym",
                "synonyms": SYNONYMS,
            }
        },
        "analyzer": {
            "course_search": {
                "tokenizer": "standard",
                "filter": ["lowercase", "course_synonyms"],
            }
        },
    }
}

COURSE_MAPPINGS = {
    "properties": {
        "id": {"type": "keyword"},
        "title": {
            "type": "text",
            "analyzer": "course_search",
            "fields": {"keyword": {"type": "keyword"}},
        },
        "description": {"type": "text", "analyzer": "course_search"},
        "price": {"type": "float"},
        "level": {"type": "keyword"},
        "duration_hours": {"type": "float"},
        "language": {"type": "keyword"},
        "tags": {"type": "text", "analyzer": "course_search"},
        "mentor_id": {"type": "keyword"},
        "mentor_name": {
            "type": "text",
            "analyzer": "course_search",
            "fields": {"keyword": {"type": "keyword"}},
        },
        "rating": {"type": "float"},
        "is_approved": {"type": "boolean"},
        "suggest": {
            "type": "completion",
            "analyzer": "course_search",
            "preserve_separators": True,
            "preserve_position_increments": True,
            "max_input_length": 50,
        },
    }
}

MENTOR_MAPPINGS = {
    "properties": {
        "id": {"type": "keyword"},
        "name": {
            "type": "text",
            "analyzer": "course_search",
            "fields": {"keyword": {"type": "keyword"}},
        },
        "email": {"type": "keyword"},
        "course_count": {"type": "integer"},
        "suggest": {
            "type": "completion",
            "analyzer": "course_search",
        },
    }
}


import time

_es_client = None
_es_checked_time = 0


def _client():
    global _es_client, _es_checked_time
    if not current_app.config.get("ELASTICSEARCH_ENABLED", True):
        return None

    now = time.time()
    # If checked less than 30 seconds ago, reuse the cached client status
    if now - _es_checked_time < 30:
        return _es_client

    try:
        from elasticsearch import Elasticsearch
    except ImportError:
        _es_checked_time = now
        _es_client = None
        return None

    url = current_app.config.get(
        "ELASTICSEARCH_URL",
        "http://localhost:9200",
    )
    try:
        # Use a short timeout of 1 second for ping
        client = Elasticsearch(url, request_timeout=1.0)
        if client.ping():
            _es_client = client
        else:
            _es_client = None
    except Exception:
        _es_client = None

    _es_checked_time = now
    return _es_client


def ensure_indices():
    client = _client()
    if not client:
        return False

    for index, mappings in (
        (COURSES_INDEX, COURSE_MAPPINGS),
        (MENTORS_INDEX, MENTOR_MAPPINGS),
    ):
        if not client.indices.exists(index=index):
            client.indices.create(
                index=index,
                settings=INDEX_SETTINGS,
                mappings=mappings,
            )
    return True


def _course_document(course):
    mentor = course.mentor or User.query.get(course.mentor_id)
    tags = course.tags or []
    rating = calculate_weighted_rating(course.id)
    suggest_inputs = [course.title, mentor.name if mentor else ""]
    suggest_inputs.extend(tags)

    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "price": course.price,
        "level": course.level.value,
        "duration_hours": course.duration_hours,
        "language": course.language.lower(),
        "tags": tags,
        "mentor_id": course.mentor_id,
        "mentor_name": mentor.name if mentor else "",
        "rating": rating,
        "is_approved": course.is_approved,
        "suggest": {
            "input": [value for value in suggest_inputs if value],
            "weight": max(int(rating * 10), 1),
        },
    }


def _mentor_document(mentor):
    course_count = Course.query.filter_by(
        mentor_id=mentor.id,
        is_approved=True,
    ).count()

    return {
        "id": mentor.id,
        "name": mentor.name,
        "email": mentor.email,
        "course_count": course_count,
        "suggest": {
            "input": [mentor.name],
            "weight": max(course_count, 1),
        },
    }


def index_course(course):
    client = _client()
    if not client or not ensure_indices():
        return False

    client.index(
        index=COURSES_INDEX,
        id=course.id,
        document=_course_document(course),
    )

    mentor = course.mentor or User.query.get(course.mentor_id)
    if mentor and mentor.role == UserRole.MENTOR:
        index_mentor(mentor)

    return True


def index_mentor(mentor):
    client = _client()
    if not client or not ensure_indices():
        return False

    if mentor.role != UserRole.MENTOR:
        return False

    client.index(
        index=MENTORS_INDEX,
        id=mentor.id,
        document=_mentor_document(mentor),
    )
    return True


def delete_course_from_index(course_id):
    client = _client()
    if not client:
        return False

    if client.indices.exists(index=COURSES_INDEX):
        client.delete(index=COURSES_INDEX, id=course_id, ignore=[404])
    return True


def reindex_all():
    if not ensure_indices():
        return {"courses": 0, "mentors": 0, "status": "unavailable"}

    courses = Course.query.all()
    mentors = User.query.filter_by(role=UserRole.MENTOR).all()

    for course in courses:
        index_course(course)

    for mentor in mentors:
        index_mentor(mentor)

    return {
        "courses": len(courses),
        "mentors": len(mentors),
        "status": "ok",
    }


def _build_filters(params):
    filters = [{"term": {"is_approved": True}}]

    min_price = params.get("min_price")
    max_price = params.get("max_price")
    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None:
            price_range["gte"] = float(min_price)
        if max_price is not None:
            price_range["lte"] = float(max_price)
        filters.append({"range": {"price": price_range}})

    level = params.get("level")
    if level:
        filters.append({"term": {"level": level.lower()}})

    min_duration = params.get("min_duration")
    max_duration = params.get("max_duration")
    if min_duration is not None or max_duration is not None:
        duration_range = {}
        if min_duration is not None:
            duration_range["gte"] = float(min_duration)
        if max_duration is not None:
            duration_range["lte"] = float(max_duration)
        filters.append({"range": {"duration_hours": duration_range}})

    language = params.get("language")
    if language:
        filters.append({"term": {"language": language.lower()}})

    min_rating = params.get("min_rating")
    if min_rating is not None:
        filters.append({"range": {"rating": {"gte": float(min_rating)}}})

    tags = params.get("tags")
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        for tag in tag_list:
            filters.append({"match": {"tags": tag}})

    return filters


def search_courses(params):
    client = _client()
    query_text = (params.get("q") or "").strip()
    page = max(int(params.get("page", 1)), 1)
    per_page = min(max(int(params.get("per_page", 10)), 1), 50)
    offset = (page - 1) * per_page

    if not client or not ensure_indices():
        return _sql_search_courses(params, page, per_page)

    must = []
    if query_text:
        must.append({
            "multi_match": {
                "query": query_text,
                "fields": [
                    "title^4",
                    "description^2",
                    "tags^3",
                    "mentor_name^2",
                ],
                "analyzer": "course_search",
                "fuzziness": "AUTO",
            }
        })
    else:
        must.append({"match_all": {}})

    body = {
        "from": offset,
        "size": per_page,
        "query": {
            "bool": {
                "must": must,
                "filter": _build_filters(params),
            }
        },
        "sort": [
            "_score",
            {"rating": {"order": "desc"}},
        ],
    }

    response = client.search(index=COURSES_INDEX, body=body)
    hits = response["hits"]["hits"]
    total = response["hits"]["total"]["value"]

    return {
        "courses": [hit["_source"] for hit in hits],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total else 0,
        "engine": "elasticsearch",
    }


def search_mentors(params):
    client = _client()
    query_text = (params.get("q") or "").strip()
    page = max(int(params.get("page", 1)), 1)
    per_page = min(max(int(params.get("per_page", 10)), 1), 50)
    offset = (page - 1) * per_page

    if not client or not ensure_indices():
        return _sql_search_mentors(params, page, per_page)

    must = [{"match_all": {}}]
    if query_text:
        must = [{
            "multi_match": {
                "query": query_text,
                "fields": ["name^3", "email"],
                "analyzer": "course_search",
                "fuzziness": "AUTO",
            }
        }]

    body = {
        "from": offset,
        "size": per_page,
        "query": {"bool": {"must": must}},
        "sort": [{"course_count": {"order": "desc"}}, "_score"],
    }

    response = client.search(index=MENTORS_INDEX, body=body)
    hits = response["hits"]["hits"]
    total = response["hits"]["total"]["value"]

    return {
        "mentors": [hit["_source"] for hit in hits],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if total else 0,
        "engine": "elasticsearch",
    }


def autocomplete(prefix):
    client = _client()
    prefix = (prefix or "").strip()

    if not prefix or not client or not ensure_indices():
        return {"suggestions": []}

    body = {
        "suggest": {
            "course_suggest": {
                "prefix": prefix,
                "completion": {
                    "field": "suggest",
                    "fuzzy": {"fuzziness": 1},
                    "size": 5,
                },
            },
            "mentor_suggest": {
                "prefix": prefix,
                "completion": {
                    "field": "suggest",
                    "fuzzy": {"fuzziness": 1},
                    "size": 5,
                },
            },
        }
    }

    course_response = client.search(index=COURSES_INDEX, body=body)
    mentor_response = client.search(index=MENTORS_INDEX, body=body)

    suggestions = []
    seen = set()

    for label, response in (
        ("course", course_response),
        ("mentor", mentor_response),
    ):
        key = f"{label}_suggest"
        options = response.get("suggest", {}).get(key, [])
        for option_group in options:
            for option in option_group.get("options", []):
                text = option["text"]
                if text.lower() in seen:
                    continue
                seen.add(text.lower())
                suggestions.append({
                    "text": text,
                    "type": label,
                    "score": option.get("_score", 0),
                })

    suggestions.sort(key=lambda item: item["score"], reverse=True)
    return {"suggestions": suggestions[:10]}


def _sql_search_courses(params, page, per_page):
    query_text = (params.get("q") or "").strip()
    query = Course.query.filter_by(is_approved=True)

    if query_text:
        query = query.filter(
            db.or_(
                Course.title.ilike(f"%{query_text}%"),
                Course.description.ilike(f"%{query_text}%"),
            )
        )

    min_price = params.get("min_price")
    max_price = params.get("max_price")
    if min_price is not None:
        query = query.filter(Course.price >= float(min_price))
    if max_price is not None:
        query = query.filter(Course.price <= float(max_price))

    level = params.get("level")
    if level:
        from app.models.course import CourseLevel
        try:
            query = query.filter(Course.level == CourseLevel(level.lower()))
        except ValueError:
            pass

    min_duration = params.get("min_duration")
    max_duration = params.get("max_duration")
    if min_duration is not None:
        query = query.filter(Course.duration_hours >= float(min_duration))
    if max_duration is not None:
        query = query.filter(Course.duration_hours <= float(max_duration))

    language = params.get("language")
    if language:
        query = query.filter(Course.language.ilike(language))

    min_rating = params.get("min_rating")
    result = query.paginate(page=page, per_page=per_page, error_out=False)
    courses = []
    for course in result.items:
        rating = calculate_weighted_rating(course.id)
        if min_rating is not None and rating < float(min_rating):
            continue
        data = course.to_dict()
        data["rating"] = rating
        data["mentor_name"] = course.mentor.name if course.mentor else ""
        courses.append(data)

    return {
        "courses": courses,
        "total": result.total,
        "page": page,
        "per_page": per_page,
        "pages": result.pages,
        "engine": "database",
    }


def _sql_search_mentors(params, page, per_page):
    query_text = (params.get("q") or "").strip()
    query = User.query.filter_by(role=UserRole.MENTOR)

    if query_text:
        query = query.filter(
            db.or_(
                User.name.ilike(f"%{query_text}%"),
                User.email.ilike(f"%{query_text}%"),
            )
        )

    result = query.paginate(page=page, per_page=per_page, error_out=False)
    mentors = []
    for mentor in result.items:
        mentors.append({
            "id": mentor.id,
            "name": mentor.name,
            "email": mentor.email,
            "course_count": Course.query.filter_by(
                mentor_id=mentor.id,
                is_approved=True,
            ).count(),
        })

    return {
        "mentors": mentors,
        "total": result.total,
        "page": page,
        "per_page": per_page,
        "pages": result.pages,
        "engine": "database",
    }
