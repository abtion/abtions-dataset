import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    REDIS_HOST = os.getenv("REDIS_HOST") or "localhost"
    REDIS_PORT = os.getenv("REDIS_PORT") or 6379
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or None
