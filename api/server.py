from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from api.schemas import DocumentRequest
from api.job_store import create_job, get_job
from api.background_tasks import run_analysis
from llm.loader import load_llm
from fastapi import UploadFile, File
from utils.file_loader import extract_text
from fastapi import Depends
from api.auth import require_api_key
from api.rate_limit import rate_limit
from api.auth import require_api_key
from utils.audit import audit_event
from fastapi import Depends
import time
import json

app = FastAPI(title="LLM Document Analyzer")

print("🚀 Loading LLM...")
llm = load_llm()
print("✅ LLM loaded")

@app.post("/analyze/document", dependencies=[Depends(rate_limit)])
def submit_document(
    request: DocumentRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(require_api_key),
):
    job_id = create_job()

    audit_event(
        api_key=api_key,
        action="submit_document",
        job_id=job_id,
        status="accepted",
    )

    background_tasks.add_task(
        run_analysis,
        job_id,
        llm,
        request.document_text,
        api_key,
    )
    return {"job_id": job_id, "status": "submitted"}

@app.get("/jobs/{job_id}", dependencies=[
    Depends(require_api_key),
    Depends(rate_limit),
])
def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/stream", dependencies=[
    Depends(require_api_key),
    Depends(rate_limit),
])
def stream_job(job_id: str):
    def event_generator():
        last_index = 0
        while True:
            job = get_job(job_id)
            if not job:
                yield "event: error\ndata: Job not found\n\n"
                return

            progress = job["progress"]
            while last_index < len(progress):
                msg = progress[last_index]
                yield f"data: {json.dumps(msg)}\n\n"
                last_index += 1

            if job["status"] in ("completed", "failed"):
                yield f"event: done\ndata: {job['status']}\n\n"
                return

            time.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/analyze/file", dependencies=[
    Depends(require_api_key),
    Depends(rate_limit),
])
async def analyze_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(require_api_key),
):
    contents = await file.read()

    try:
        text = extract_text(file.filename, contents)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    job_id = create_job()
    background_tasks.add_task(run_analysis, job_id, llm, text, api_key)

    return {
        "job_id": job_id,
        "filename": file.filename,
        "status": "submitted"
    }
