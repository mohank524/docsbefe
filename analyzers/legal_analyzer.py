import json
from llm.prompt_builder import build_mistral_prompt
from utils.section_detector import detect_sections
from utils.chunker import chunk_sections

SYSTEM_PROMPT = "You are Lexi-Clarity. Respond ONLY with valid JSON."

def analyze_document(llm, document):
    sections = chunk_sections(detect_sections(document))
    results = []

    for s in sections:
        prompt = build_mistral_prompt(
            SYSTEM_PROMPT,
            f'''Analyze and return JSON:
{{
  "section_title": "{s['title']}",
  "summary": "",
  "key_obligations": [],
  "risks": [],
  "overall_risk_score": 1
}}

Text:
{s['content']}
'''
        )

        out = llm(prompt, max_tokens=600, stop=["</s>"])
        raw = out["choices"][0]["text"].strip()

        try:
            results.append(json.loads(raw))
        except:
            results.append({"section_title": s["title"], "raw_output": raw})

    return results
