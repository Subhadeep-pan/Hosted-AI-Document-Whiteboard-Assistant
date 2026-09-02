import redis
from backend.app.core.config import REDIS_URL, REDIS_HOST, REDIS_PORT

# UPGRADED for hosted deployments: Render's managed Redis, Upstash, etc
# give you a full connection URL (auth + TLS included), not just a
# host/port pair - the old host/port-only client couldn't authenticate
# against those at all. REDIS_URL is used when set; otherwise falls
# back to plain host/port for local dev.
if REDIS_URL:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
else:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )
