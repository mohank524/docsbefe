def build_mistral_prompt(system_prompt: str, user_prompt: str) -> str:
    return f"[INST] {system_prompt}\n\n{user_prompt} [/INST]"
