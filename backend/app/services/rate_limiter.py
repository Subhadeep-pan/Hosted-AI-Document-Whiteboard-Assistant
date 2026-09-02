from backend.app.core.config import MAX_REQUESTS_PER_MINUTE
from backend.app.services.redis_service import redis_client


def is_rate_limited(session_id):
    key = f"rate_limit:{session_id}"

    count = redis_client.incr(key)

    if count == 1:
        redis_client.expire(key, 60)

    return count > MAX_REQUESTS_PER_MINUTE