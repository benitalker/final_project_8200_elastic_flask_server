from dotenv import load_dotenv
import os

load_dotenv(verbose=True)

class Config:
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    ES_INDEX_FOR_NEWS = os.getenv('ES_INDEX_FOR_NEWS')
    ES_INDEX_FOR_TERROR = os.getenv('ES_INDEX_FOR_TERROR')