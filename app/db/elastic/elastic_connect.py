from elasticsearch import Elasticsearch
from functools import lru_cache
from app.db.elastic.config import Config

@lru_cache()
def get_elasticsearch_client() -> Elasticsearch:
    return Elasticsearch(
        Config.ES_HOST,
        basic_auth=(Config.ES_USER, Config.ES_PASSWORD),
        verify_certs=False
    )

def init_indices():
    client = get_elasticsearch_client()
    if not client.indices.exists(index=Config.ES_INDEX_FOR_NEWS):
        client.indices.create(
            index=Config.ES_INDEX_FOR_NEWS,
            body=Config.NEWS_MAPPING
        )
        print(f"Created index {Config.ES_INDEX_FOR_NEWS}")
    if not client.indices.exists(index=Config.ES_INDEX_FOR_TERROR):
        client.indices.create(
            index=Config.ES_INDEX_FOR_TERROR,
            body=Config.NEWS_MAPPING
        )
        print(f"Created index {Config.ES_INDEX_FOR_TERROR}")

elastic_client = get_elasticsearch_client()