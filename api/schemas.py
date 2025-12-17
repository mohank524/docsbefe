from pydantic import BaseModel
from typing import List, Dict, Any

class DocumentRequest(BaseModel):
    document_text: str

class AnalysisResponse(BaseModel):
    results: List[Dict[str, Any]]