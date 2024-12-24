from flask import Blueprint
from app.db.elastic.elastic_connect import elastic_client
from app.db.elastic.models import SearchParams
from app.service.map_service import create_map_from_results
from toolz import pipe
from app.service.search_service import execute_search

def create_map_routes() -> Blueprint:
    map_routes = Blueprint('map', __name__)

    @map_routes.route('/map')
    def show_map():
        return pipe(
            SearchParams(
                query="category:terror_event",
                limit=100,
                source="news"
            ),
            lambda params: execute_search(elastic_client, params),
            create_map_from_results
        )
    return map_routes