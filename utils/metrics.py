import time
from contextlib import contextmanager
from typing import Dict, Any


@contextmanager
def timed() -> Dict[str, float]:
    start = time.perf_counter()
    data = {}
    try:
        yield data
    finally:
        data["duration_ms"] = round((time.perf_counter() - start) * 1000, 2)
