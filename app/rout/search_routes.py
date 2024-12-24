from typing import Callable, Dict, Any
from datetime import datetime
from flask import Blueprint, request, jsonify
from toolz import compose, pipe, curry
from functools import partial
from app.db.elastic.elastic_connect import elastic_client
from app.service.map_service import create_map_from_results
from app.db.elastic.models import SearchParams
from flask_cors import CORS
import logging
from app.service.search_service import execute_search

logger = logging.getLogger(__name__)

@curry
def safe_int(default: int, value: Any) -> int:
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

@curry
def parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None

@curry
def extract_search_params(req: request, source: str | None = None) -> SearchParams:
    return SearchParams(
        query=req.args.get('query', ''),
        limit=safe_int(100)(req.args.get('limit')),
        start_date=parse_date(req.args.get('start_date')),
        end_date=parse_date(req.args.get('end_date')),
        source=source
    )

def handle_search_errors(f: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.error(f"Value error in search: {e}")
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Unexpected error in search: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500
    return wrapper

def create_blueprint(name: str) -> Blueprint:
    bp = Blueprint(name, __name__)
    CORS(bp)
    return bp

def create_search_handler(source: str | None = None) -> Callable:
    return compose(
        create_map_from_results,
        partial(execute_search, elastic_client),
        extract_search_params(source=source)
    )

def register_routes(bp: Blueprint) -> Blueprint:
    def make_handler(source: str | None = None) -> Callable:
        return handle_search_errors(
            lambda: create_search_handler(source)(request)
        )
    routes = {
        '/keywords': ('keywords', None),
        '/news': ('news', 'news'),
        '/historic': ('historic', 'historic'),
        '/combined': ('combined', None)
    }
    for path, (endpoint, source) in routes.items():
        bp.add_url_rule(
            path,
            endpoint,
            make_handler(source)
        )
    return bp

def create_search_routes() -> Blueprint:
    return pipe(
        create_blueprint('search'),
        register_routes
    )