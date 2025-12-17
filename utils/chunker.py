def chunk_sections(sections, max_chars=800):
    chunks = []
    for s in sections:
        text = s["content"]
        if len(text) <= max_chars:
            chunks.append(s)
        else:
            parts = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
            for i, p in enumerate(parts):
                chunks.append({
                    "title": f"{s['title']} (Part {i+1})",
                    "content": p
                })
    return chunks
