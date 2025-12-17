import os
from fastapi import Header, HTTPException, status
from typing import Optional, Set

API_KEYS: Set[str] = set(
    k.strip() for k in os.getenv("API_KEYS", "").split(",") if k.strip()
)

if not API_KEYS:
    raise RuntimeError("No API_KEYS configured")


def require_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key
