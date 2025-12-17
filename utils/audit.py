import json
import time
import hashlib
from typing import Optional, Dict, Any


def _hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]


def audit_event(
    *,
    api_key: str,
    action: str,
    job_id: Optional[str] = None,
    status: str,
    meta: Optional[Dict[str, Any]] = None,
):
    event = {
        "ts": int(time.time()),
        "actor": _hash_api_key(api_key),
        "action": action,
        "job_id": job_id,
        "status": status,
        "meta": meta or {},
    }

    # For now: stdout (Docker-friendly, log-aggregator-ready)
    print(json.dumps(event))
