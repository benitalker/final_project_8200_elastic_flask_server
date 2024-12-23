import logging
from typing import List, Dict, Any, Optional
from elasticsearch import Elasticsearch
from functools import lru_cache
from app.db.elastic.models import SearchParams

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@lru_cache(maxsize=128)
def build_elasticsearch_query(params: SearchParams) -> Dict[str, Any]:
    try:
        query = {
            "bool": {
                "should": [
                    {"match": {"title": {"query": params.query, "boost": 2.0}}},
                    {"match": {"content": params.query}},
                    {"match": {"location": params.query}}
                ],
                "minimum_should_match": 1
            }
        }
        if params.start_date or params.end_date:
            date_range = {}
            if params.start_date:
                date_range["gte"] = params.start_date.isoformat()
            if params.end_date:
                date_range["lte"] = params.end_date.isoformat()
            query["bool"]["must"] = [{"range": {"publication_date": date_range}}]
        return {
            "size": min(params.limit, 1000),
            "query": query,
            "_source": ["title", "content", "publication_date", "category", "location", "coordinates"],
            "sort": [{"_score": "desc"}]
        }
    except Exception as e:
        logger.error(f"Error building Elasticsearch query: {e}")
        raise

def get_indices_for_search(source: Optional[str]) -> List[str]:
    if not source:
        return ["news_events", "terror_data"]
    elif source == "news":
        return ["news_events"]
    elif source == "historic":
        return ["terror_data"]
    return ["news_events", "terror_data"]

def execute_search(
        elastic_client: Elasticsearch,
        params: SearchParams
) -> List[Dict[str, Any]]:
    try:
        if not params.query:
            logger.warning("Empty search query received")
            return []
        query = build_elasticsearch_query(params)
        indices = get_indices_for_search(params.source)
        logger.info(f"Searching with query: {query}")
        logger.info(f"Searching in indices: {indices}")
        try:
            results = elastic_client.search(
                index=indices,
                body=query
            )
        except Exception as e:
            logger.error(f"Elasticsearch query error: {e}")
            raise
        hits = results['hits']['hits']
        logger.info(f"Found {len(hits)} results")
        processed_results = []
        for hit in hits:
            try:
                source = hit.get('_source', {})
                if 'coordinates' in source:
                    coords = source['coordinates']
                    if not isinstance(coords, dict):
                        source['coordinates'] = None
                    elif not all(isinstance(v, (int, float)) for v in coords.values()):
                        source['coordinates'] = None
                processed_results.append(source)
            except Exception as proc_error:
                logger.warning(f"Error processing hit: {proc_error}")
        return processed_results
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        raise
