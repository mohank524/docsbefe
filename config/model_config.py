import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MODEL_REPO_ID = "TheBloke/Mistral-7B-Instruct-v0.2-GGUF"
MODEL_FILENAME = "models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"

MODEL_PATH = os.path.join(BASE_DIR, MODEL_FILENAME)

CONTEXT_WINDOW = 4096
GPU_LAYERS = 0
