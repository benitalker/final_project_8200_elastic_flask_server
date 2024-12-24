from dotenv import load_dotenv
import os

load_dotenv(verbose=True)


class Config:
    # API Keys
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')

    # Elasticsearch Configuration
    ES_HOST = os.getenv('ES_HOST', 'http://localhost:9200')
    ES_USER = os.getenv('ES_USER', 'elastic')
    ES_PASSWORD = os.getenv('ES_PASSWORD', '123456')
    ES_INDEX_FOR_NEWS = os.getenv('ES_INDEX_FOR_NEWS', 'news_index')
    ES_INDEX_FOR_TERROR = os.getenv('ES_INDEX_FOR_TERROR', 'terror_index')

    # News Fetching Configuration
    FETCH_INTERVAL_MINUTES = int(os.getenv('FETCH_INTERVAL_MINUTES', '2'))
    MAX_ARTICLES_PER_FETCH = int(os.getenv('MAX_ARTICLES_PER_FETCH', '100'))

    # Elastic Search Mapping
    NEWS_MAPPING = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "content": {"type": "text"},
                "body": {"type": "text"},
                "category": {"type": "keyword"},
                "location": {"type": "keyword"},
                "publication_date": {
                    "type": "date",
                    "format": "strict_date_optional_time||epoch_millis"
                },
                "dateTime": {
                    "type": "date",
                    "format": "strict_date_optional_time||epoch_millis"
                },
                "coordinates": {
                    "properties": {
                        "lat": {"type": "float"},
                        "lon": {"type": "float"}
                    }
                },
                "source": {"type": "keyword"},
                "source_url": {"type": "keyword"},
                "url": {"type": "keyword"},
                "confidence": {"type": "float"}
            }
        }
    }