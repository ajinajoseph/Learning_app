from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.middleware.role_required import role_required
from app.models.user import UserRole
from app.services.elasticsearch_service import (
    autocomplete,
    reindex_all,
    search_courses,
    search_mentors,
)


search_bp = Blueprint(
    "search",
    __name__,
    url_prefix="/api/search",
)


def _search_params():
    return {
        "q": request.args.get("q", ""),
        "min_price": request.args.get("min_price", type=float),
        "max_price": request.args.get("max_price", type=float),
        "level": request.args.get("level"),
        "min_duration": request.args.get("min_duration", type=float),
        "max_duration": request.args.get("max_duration", type=float),
        "language": request.args.get("language"),
        "min_rating": request.args.get("min_rating", type=float),
        "tags": request.args.get("tags"),
        "page": request.args.get("page", 1, type=int),
        "per_page": request.args.get("per_page", 10, type=int),
    }


@search_bp.route("/courses", methods=["GET"])
def search_courses_route():
    return jsonify(search_courses(_search_params())), 200


@search_bp.route("/mentors", methods=["GET"])
def search_mentors_route():
    return jsonify(search_mentors(_search_params())), 200


@search_bp.route("/autocomplete", methods=["GET"])
def autocomplete_route():
    prefix = request.args.get("q", "")
    return jsonify(autocomplete(prefix)), 200


@search_bp.route("/reindex", methods=["POST"])
@jwt_required()
@role_required(UserRole.ADMIN)
def reindex_route():
    result = reindex_all()
    status_code = 200 if result["status"] == "ok" else 503
    return jsonify(result), status_code
