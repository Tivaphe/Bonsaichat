import os
from huggingface_hub import snapshot_download

# Define model repositories for Bonsai GGUF models
MODELS = {
    "Bonsai-1.7B": "prism-ml/Bonsai-1.7B-gguf",
    "Bonsai-4B": "prism-ml/Bonsai-4B-gguf",
    "Bonsai-8B": "prism-ml/Bonsai-8B-gguf"
}

def get_models_dir():
    """Returns the path to the models directory."""
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    return models_dir

def list_downloaded_models():
    """Lists the models already downloaded in the models/ directory."""
    models_dir = get_models_dir()
    downloaded = []
    for model_name in MODELS.keys():
        model_path = os.path.join(models_dir, model_name)
        if os.path.exists(model_path) and any(f.endswith('.gguf') for f in os.listdir(model_path)):
            downloaded.append(model_name)
    return downloaded

def download_model(model_name):
    """Downloads the specified model from HuggingFace."""
    if model_name not in MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    models_dir = get_models_dir()
    repo_id = MODELS[model_name]
    local_dir = os.path.join(models_dir, model_name)

    print(f"Downloading {model_name} from {repo_id}...")
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        allow_patterns="*.gguf"
    )
    print(f"{model_name} downloaded to {local_dir}")
    return local_dir

def get_model_file(model_name):
    """Returns the path to the GGUF file for the specified model."""
    models_dir = get_models_dir()
    model_path = os.path.join(models_dir, model_name)
    if os.path.exists(model_path):
        for f in os.listdir(model_path):
            if f.endswith('.gguf'):
                return os.path.join(model_path, f)
    return None

if __name__ == "__main__":
    # Test script
    print("Available models:", list(MODELS.keys()))
    print("Downloaded models:", list_downloaded_models())
