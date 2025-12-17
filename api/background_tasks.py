from analyzers.legal_analyzer import analyze_document
from api.job_store import update_job, complete_job, fail_job
from utils.audit import audit_event

def run_analysis(job_id: str, llm, document_text: str, api_key: str):
    try:
        update_job(job_id, "Started analysis")

        results = analyze_document(llm, document_text)

        complete_job(job_id, results)

        audit_event(
            api_key=api_key,
            action="analysis_complete",
            job_id=job_id,
            status="success",
            meta={
                "sections": len(results),
            },
        )

    except Exception as e:
        fail_job(job_id, str(e))

        audit_event(
            api_key=api_key,
            action="analysis_complete",
            job_id=job_id,
            status="failure",
            meta={"error": str(e)},
        )
