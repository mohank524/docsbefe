from llama_cpp import Llama
from config.model_config import MODEL_PATH, CONTEXT_WINDOW, GPU_LAYERS

def load_llm():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=CONTEXT_WINDOW,
        n_gpu_layers=GPU_LAYERS,
        verbose=False
    )
