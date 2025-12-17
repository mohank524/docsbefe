import time
import os
import redis
from fastapi import HTTPException, status, Depends

from api.auth import require_api_key

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)

REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT_RPM", 30))
WINDOW_SECONDS = 60


def rate_limit(api_key: str = Depends(require_api_key)):
    """
    Rate limit per API key using Redis.
    """
    now = int(time.time())
    window = now // WINDOW_SECONDS
    key = f"rate:{api_key}:{window}"

    count = r.incr(key)
    if count == 1:
        r.expire(key, WINDOW_SECONDS)

    if count > REQUESTS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
