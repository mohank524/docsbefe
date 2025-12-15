from huggingface_hub import hf_hub_download
from config.model_config import MODEL_REPO_ID, MODEL_FILENAME

def download_model():
    hf_hub_download(
        repo_id=MODEL_REPO_ID,
        filename=MODEL_FILENAME,
        local_dir=".",
        local_dir_use_symlinks=False
    )

if __name__ == "__main__":
    download_model()
