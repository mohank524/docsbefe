import json
from json import JSONDecodeError
from typing import List, Dict, Any

from pydantic import ValidationError

from llm.prompt_builder import build_mistral_prompt
from utils.section_detector import detect_sections
from utils.chunker import chunk_sections
from utils.metrics import timed
from utils.confidence import compute_confidence
from api.schemas_legal import LegalAnalysisResult


# =========================
# Prompts
# =========================

SYSTEM_PROMPT = (
    "You are Lexi-Clarity, a legal analysis assistant. "
    "Respond ONLY with valid JSON that strictly matches the required schema. "
    "Do not include explanations, markdown, or extra text."
)

REPAIR_SYSTEM_PROMPT = (
    "You are a JSON repair engine. "
    "Fix the structure of the JSON so it EXACTLY matches the required schema. "
    "Do NOT add new analysis, facts, or meaning. "
    "Do NOT explain anything. "
    "Output ONLY valid JSON."
)

MAX_REPAIR_ATTEMPTS = 1


# =========================
# Prompt builders
# =========================

def _build_analysis_prompt(section_title: str, section_content: str) -> str:
    user_prompt = f"""
Analyze the following legal document section and return JSON
that strictly conforms to the required schema.

Rules:
- All fields are required
- Do not add extra keys
- overall_risk_score must be an integer between 0 and 100

Section title:
{section_title}

Section content:
\"\"\"
{section_content}
\"\"\"
"""
    return build_mistral_prompt(SYSTEM_PROMPT, user_prompt)


def _build_repair_prompt(invalid_json: str, validation_errors: str) -> str:
    user_prompt = f"""
The following JSON is invalid or does not match the required schema.

Validation errors:
{validation_errors}

Invalid JSON:
\"\"\"
{invalid_json}
\"\"\"

Fix the JSON so that:
- All required fields are present
- Field types are correct
- No extra keys exist
- Enum values match exactly
- overall_risk_score is between 0 and 100

Return ONLY the repaired JSON.
"""
    return build_mistral_prompt(REPAIR_SYSTEM_PROMPT, user_prompt)


# =========================
# Main analyzer
# =========================

def analyze_document(llm, document: str) -> List[Dict[str, Any]]:
    sections = chunk_sections(detect_sections(document))
    results: List[Dict[str, Any]] = []

    for section in sections:
        repair_attempted = False
        repair_succeeded = False

        prompt = _build_analysis_prompt(
            section_title=section["title"],
            section_content=section["content"],
        )

        with timed() as timing:
            response = llm(
                prompt,
                max_tokens=512,
                temperature=0.1,
                stop=["</s>"],
            )

        usage = response.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")

        raw_text = response["choices"][0]["text"].strip()

        try:
            parsed_json = json.loads(raw_text)
            validated = LegalAnalysisResult.model_validate(parsed_json)

            confidence = compute_confidence(
                validation_passed=True,
                repair_attempted=False,
                repair_succeeded=False,
                obligations=validated.key_obligations,
                risks=validated.risks,
            )

            results.append({
                "analysis": validated.model_dump(),
                "confidence": confidence,
                "meta": {
                    "duration_ms": timing["duration_ms"],
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "repair_attempted": False,
                    "repair_succeeded": False,
                }
            })
            continue

        except (JSONDecodeError, ValidationError) as first_error:
            repair_attempted = True
            last_output = raw_text

            for _ in range(MAX_REPAIR_ATTEMPTS):
                repair_prompt = _build_repair_prompt(
                    invalid_json=last_output,
                    validation_errors=str(first_error),
                )

                repair_response = llm(
                    repair_prompt,
                    max_tokens=512,
                    temperature=0.0,
                    stop=["</s>"],
                )

                repaired_text = repair_response["choices"][0]["text"].strip()

                try:
                    repaired_json = json.loads(repaired_text)
                    validated = LegalAnalysisResult.model_validate(repaired_json)
                    repair_succeeded = True

                    confidence = compute_confidence(
                        validation_passed=True,
                        repair_attempted=True,
                        repair_succeeded=True,
                        obligations=validated.key_obligations,
                        risks=validated.risks,
                    )

                    results.append({
                        "analysis": validated.model_dump(),
                        "confidence": confidence,
                        "meta": {
                            "duration_ms": timing["duration_ms"],
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                            "repair_attempted": True,
                            "repair_succeeded": True,
                        }
                    })
                    break

                except Exception:
                    last_output = repaired_text

            if not repair_succeeded:
                confidence = {
                    "score": 0.0,
                    "band": "Low",
                    "reasons": [
                        "Output failed schema validation",
                        "Repair attempt unsuccessful",
                    ],
                }

                results.append({
                    "section_title": section["title"],
                    "error": "Validation failed after repair attempt",
                    "raw_output": last_output,
                    "confidence": confidence,
                    "meta": {
                        "duration_ms": timing["duration_ms"],
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "repair_attempted": True,
                        "repair_succeeded": False,
                    }
                })

        except Exception as e:
            results.append({
                "section_title": section["title"],
                "error": "Unexpected analysis error",
                "details": str(e),
                "confidence": {
                    "score": 0.0,
                    "band": "Low",
                    "reasons": ["Unexpected system error"],
                },
            })

    return results
