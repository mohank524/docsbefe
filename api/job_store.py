import os
import uuid
import json
from typing import Any, Dict, Optional

import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
)


def _job_key(job_id: str) -> str:
    return f"job:{job_id}"


def create_job() -> str:
    job_id = str(uuid.uuid4())
    job = {
        "status": "pending",
        "progress": [],
        "result": None,
        "error": None,
    }
    r.set(_job_key(job_id), json.dumps(job), ex=3600)
    return job_id


def update_job(job_id: str, message: str) -> None:
    key = _job_key(job_id)
    job = r.get(key)
    if not job:
        return

    data = json.loads(job)
    data["progress"].append(message)
    r.set(key, json.dumps(data))


def complete_job(job_id: str, result: Any) -> None:
    key = _job_key(job_id)
    job = r.get(key)
    if not job:
        return

    data = json.loads(job)
    data["status"] = "completed"
    data["result"] = result
    r.set(key, json.dumps(data))


def fail_job(job_id: str, error: str) -> None:
    key = _job_key(job_id)
    job = r.get(key)
    if not job:
        return

    data = json.loads(job)
    data["status"] = "failed"
    data["error"] = error
    r.set(key, json.dumps(data))


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    job = r.get(_job_key(job_id))
    return json.loads(job) if job else None
