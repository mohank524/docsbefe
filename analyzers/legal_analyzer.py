import json
from json import JSONDecodeError
from typing import List, Dict, Any

from pydantic import ValidationError

from llm.prompt_builder import build_mistral_prompt
from utils.section_detector import detect_sections
from utils.chunker import chunk_sections
from api.schemas_legal import LegalAnalysisResult
from pydantic import ValidationError

MAX_REPAIR_ATTEMPTS = 1

SYSTEM_PROMPT = (
    "You are Lexi-Clarity, a legal analysis assistant. "
    "Respond ONLY with valid JSON that strictly matches the provided schema. "
    "Do not include explanations, markdown, or extra text."
)

REPAIR_SYSTEM_PROMPT = (
    "You are a JSON repair engine. "
    "Your ONLY task is to fix the structure of invalid JSON so that it "
    "conforms EXACTLY to the required schema. "
    "Do NOT add new analysis, facts, risks, or obligations. "
    "Do NOT remove existing meaning. "
    "Do NOT explain anything. "
    "Output ONLY valid JSON."
)


def _build_analysis_prompt(section_title: str, section_content: str) -> str:
    user_prompt = f"""
Analyze the following legal document section and return JSON
that strictly conforms to the schema.

Schema requirements:
- All fields are required
- Do not add extra keys
- overall_risk_score must be between 0 and 100

Section title:
{section_title}

Section content:
\"\"\"
{section_content}
\"\"\"
"""
    return build_mistral_prompt(SYSTEM_PROMPT, user_prompt)


def _build_repair_prompt(
    invalid_json: str,
    validation_errors,
) -> str:
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
- overall_risk_score is an integer between 0 and 100
- Enum values match exactly

Return ONLY the repaired JSON.
"""
    return build_mistral_prompt(REPAIR_SYSTEM_PROMPT, user_prompt)

def analyze_document(llm, document: str) -> List[Dict[str, Any]]:
    sections = chunk_sections(detect_sections(document))
    results: List[Dict[str, Any]] = []

    for section in sections:
        prompt = _build_analysis_prompt(
            section["title"],
            section["content"],
        )

        response = llm(
            prompt,
            max_tokens=512,
            temperature=0.1,
            stop=["</s>"],
        )

        raw_text = response["choices"][0]["text"].strip()

        try:
          parsed_json = json.loads(raw_text)
          validated = LegalAnalysisResult.model_validate(parsed_json)
          results.append(validated.model_dump())
        except (JSONDecodeError, ValidationError) as first_error:
          repaired = False

          for _ in range(MAX_REPAIR_ATTEMPTS):
              repair_prompt = _build_repair_prompt(
                  invalid_json=raw_text,
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

                  results.append(validated.model_dump())
                  repaired = True
                  break

              except Exception:
                  raw_text = repaired_text  # carry forward for error reporting

          if not repaired:
              results.append({
                  "section_title": section["title"],
                  "error": "Validation failed after repair attempt",
                  "raw_output": raw_text,
              })

    return results
