import re

def detect_sections(text):
    sections = []
    current = {"title": "Preamble", "content": []}

    for line in text.splitlines():
        if re.match(r"^\d+\.\s+|^[A-Z][A-Z\s]{3,}$", line):
            sections.append({
                "title": current["title"],
                "content": "\n".join(current["content"]).strip()
            })
            current = {"title": line.strip(), "content": []}
        else:
            current["content"].append(line)

    sections.append({
        "title": current["title"],
        "content": "\n".join(current["content"]).strip()
    })
    return [s for s in sections if s["content"]]
