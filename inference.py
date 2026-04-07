import os
import sys
from llama_cpp import Llama

class InferenceEngine:
    def __init__(self):
        self.llm = None
        self.current_model_path = None

    def load_model(self, model_path, n_gpu_layers=-1):
        """Loads a model from the specified path."""
        if self.current_model_path == model_path and self.llm is not None:
            return

        print(f"Loading model from {model_path}...")

        # In a real scenario, we would detect GPU availability.
        # Here we assume llama-cpp-python is installed correctly.
        # -ngl -1 (or 99) usually means all layers on GPU if available.
        self.llm = Llama(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_ctx=0, # 0 means auto-fit or use model default
            verbose=False
        )
        self.current_model_path = model_path
        print("Model loaded.")

    def chat_completion(self, messages, temperature=0.5, max_tokens=2048, stream=True):
        """Sends a chat completion request to the loaded model."""
        if self.llm is None:
            raise RuntimeError("Model not loaded. Call load_model first.")

        return self.llm.create_chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

# Global engine instance
engine = InferenceEngine()
