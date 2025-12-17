from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal


class Evidence(BaseModel):
    quote: str
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)

    def validate_positions(self):
        if self.char_end < self.char_start:
            raise ValueError("char_end must be >= char_start")
        return self


class Obligation(BaseModel):
    text: str
    evidence: Evidence


class Risk(BaseModel):
    type: Literal["Financial", "Legal", "Time", "Other"]
    severity: Literal["Low", "Medium", "High"]
    description: str
    evidence: Evidence


class LegalAnalysisResult(BaseModel):
    section_title: str
    summary: str
    key_obligations: List[Obligation]
    risks: List[Risk]
    overall_risk_score: int = Field(ge=0, le=100)
