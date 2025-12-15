import json
from utils.diff_engine import compute_diff
from utils.section_detector import detect_sections
from utils.chunker import chunk_sections
from llm.prompt_builder import build_mistral_prompt

SYSTEM_PROMPT = "You are Lexi-Clarity. Respond ONLY with valid JSON."

def compare_documents(llm, old_doc, new_doc):
    old_sections = chunk_sections(detect_sections(old_doc))
    new_sections = chunk_sections(detect_sections(new_doc))
    results = []

    for o, n in zip(old_sections, new_sections):
        diff = compute_diff(o["content"], n["content"])
        if not diff.strip():
            continue

        prompt = build_mistral_prompt(
            SYSTEM_PROMPT,
            f'''Return JSON:
{{
  "section_title": "{n['title']}",
  "change_summary": "",
  "risk_change": "",
  "recommended_action": ""
}}

Diff:
{diff}
'''
        )

        out = llm(prompt, max_tokens=500, stop=["</s>"])
        raw = out["choices"][0]["text"].strip()

        try:
            results.append(json.loads(raw))
        except:
            results.append({"section_title": n["title"], "raw_output": raw})

    return results
