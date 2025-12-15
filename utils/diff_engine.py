import difflib

def compute_diff(old, new):
    return "\n".join(difflib.unified_diff(
        old.splitlines(), new.splitlines(), lineterm=""
    ))
