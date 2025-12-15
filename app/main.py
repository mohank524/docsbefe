from llm.loader import load_llm
from analyzers.legal_analyzer import analyze_document
import json

doc = '''
2. Early Termination
Tenant may terminate this lease with 60 days notice and two months rent penalty.
'''

llm = load_llm()
print(json.dumps(analyze_document(llm, doc), indent=2))
