from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from toolz import curry, pipe
from app.db.elastic.models import SearchParams
from cytoolz import memoize

@memoize
def create_base_query(query: str, boost: float = 2.0) -> Dict[str, Any]:
    return {
        "bool": {
            "should": [
                {"match": {"title": {"query": query, "boost": boost}}},
                {"match": {"content": query}},
                {"match": {"location": query}}
            ],
            "minimum_should_match": 1
        }
    }

@curry
def add_date_range(params: SearchParams, query: Dict[str, Any]) -> Dict[str, Any]:
    if not (params.start_date or params.end_date):
        return query
    date_range = {
        k: v.isoformat()
        for k, v in {
            "gte": params.start_date,
            "lte": params.end_date
        }.items() if v is not None
    }
    query["bool"]["must"] = [{"range": {"publication_date": date_range}}]
    return query

@curry
def create_search_body(limit: int, query: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "size": min(limit, 1000),
        "query": query,
        "_source": ["title", "content", "publication_date", "category", "location", "coordinates"],
        "sort": [{"_score": "desc"}]
    }

def get_indices_by_source(source: Optional[str]) -> List[str]:
    return {
        None: ["news_events", "terror_data"],
        "news": ["news_events"],
        "historic": ["terror_data"]
    }.get(source, ["news_events", "terror_data"])

@curry
def validate_coordinates(doc: Dict[str, Any]) -> Dict[str, Any]:
    coords = doc.get('coordinates', {})
    if not isinstance(coords, dict) or not all(
            isinstance(coords.get(k), (int, float))
            for k in ('lat', 'lon')
    ):
        doc['coordinates'] = None
    return doc

@curry
def execute_elasticsearch_query(
        client: Elasticsearch,
        indices: List[str],
        query: Dict[str, Any]
) -> List[Dict[str, Any]]:
    results = client.search(index=indices, body=query)
    return [hit['_source'] for hit in results['hits']['hits']]

def execute_search(
        client: Elasticsearch,
        params: SearchParams
) -> List[Dict[str, Any]]:
    if not params.query:
        return []
    return pipe(
        params.query,
        create_base_query,
        add_date_range(params),
        create_search_body(params.limit),
        execute_elasticsearch_query(
            client,
            get_indices_by_source(params.source)
        ),
        lambda results: map(validate_coordinates, results),
        list
    )