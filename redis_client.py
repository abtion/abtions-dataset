import redis

from config import Config


class RedisClient(redis.Redis):
    def __init__(self):
        super().__init__(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
        )


if __name__ == "__main__":
    redis_client = RedisClient()
    try:
        redis_client.ping()
        print(f"Connected to {Config.REDIS_HOST}:{Config.REDIS_PORT}")
    except redis.exceptions.ConnectionError as e:
        print(e)
