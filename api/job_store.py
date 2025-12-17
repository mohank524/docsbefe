import uuid
from typing import Dict, Any

jobs: Dict[str, Dict[str, Any]] = {}

def create_job() -> str:
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "progress": [],
        "result": None,
        "error": None,
    }
    return job_id

def update_job(job_id: str, message: str):
    jobs[job_id]["progress"].append(message)

def complete_job(job_id: str, result: Any):
    jobs[job_id]["status"] = "completed"
    jobs[job_id]["result"] = result

def fail_job(job_id: str, error: str):
    jobs[job_id]["status"] = "failed"
    jobs[job_id]["error"] = error

def get_job(job_id: str):
    return jobs.get(job_id)
