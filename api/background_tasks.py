from analyzers.legal_analyzer import analyze_document
from api.job_store import update_job, complete_job, fail_job

def run_analysis(job_id: str, llm, document_text: str):
    try:
        update_job(job_id, "Started analysis")

        results = []

        for idx, chunk_result in enumerate(analyze_document(llm, document_text)):
            update_job(job_id, f"Processed section {idx + 1}")
            results.append(chunk_result)

        complete_job(job_id, results)
        update_job(job_id, "Analysis complete")

    except Exception as e:
        fail_job(job_id, str(e))
