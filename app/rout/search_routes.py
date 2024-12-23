from flask import Blueprint, request, jsonify
from datetime import datetime
from app.db.elastic.elastic_connect import elastic_client
from app.db.elastic.models import SearchParams
from app.service.map_service import create_map_from_results
from app.service.search_service import execute_search
from flask_cors import CORS
import logging
import traceback

search_routes = Blueprint('search', __name__)
CORS(search_routes)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_date(date_str):
    """
    Parse date from various formats

    Args:
        date_str (str): Date string to parse

    Returns:
        datetime: Parsed datetime object
    """
    try:
        # Try ISO format first (YYYY-MM-DD)
        if '-' in date_str and len(date_str.split('-')[0]) == 4:
            return datetime.fromisoformat(date_str)

        # Try DD-MM-YYYY format
        try:
            return datetime.strptime(date_str, '%d-%m-%Y')
        except ValueError:
            # Try MM-DD-YYYY format
            return datetime.strptime(date_str, '%m-%d-%Y')
    except ValueError as e:
        logger.error(f"Error parsing date {date_str}: {e}")
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD, DD-MM-YYYY, or MM-DD-YYYY. Error: {e}")


def safe_int_convert(value, default=100):
    """
    Safely convert a value to an integer

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        int: Converted integer or default
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default


@search_routes.route('/keywords')
def keywords():
    try:
        params = SearchParams(
            query=request.args.get('query', ''),
            limit=safe_int_convert(request.args.get('limit')),
            start_date=parse_date(request.args.get('start_date')) if request.args.get('start_date') else None,
            end_date=parse_date(request.args.get('end_date')) if request.args.get('end_date') else None
        )
        results = execute_search(elastic_client, params)
        return create_map_from_results(results)
    except ValueError as ve:
        logger.error(f"Value error in keywords search: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in keywords search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@search_routes.route('/news')
def news():
    try:
        params = SearchParams(
            query=request.args.get('query', ''),
            limit=safe_int_convert(request.args.get('limit')),
            source="news"
        )
        results = execute_search(elastic_client, params)
        return create_map_from_results(results)
    except Exception as e:
        logger.error(f"Unexpected error in news search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@search_routes.route('/historic')
def historic():
    try:
        params = SearchParams(
            query=request.args.get('query', ''),
            limit=safe_int_convert(request.args.get('limit')),
            source="historic"
        )
        results = execute_search(elastic_client, params)
        return create_map_from_results(results)
    except Exception as e:
        logger.error(f"Unexpected error in historic search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@search_routes.route('/combined')
def combined():
    try:
        params = SearchParams(
            query=request.args.get('query', ''),
            limit=safe_int_convert(request.args.get('limit')),
            start_date=parse_date(request.args.get('start_date')) if request.args.get('start_date') else None,
            end_date=parse_date(request.args.get('end_date')) if request.args.get('end_date') else None
        )
        results = execute_search(elastic_client, params)
        return create_map_from_results(results)
    except ValueError as ve:
        logger.error(f"Value error in combined search: {ve}")
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in combined search: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500