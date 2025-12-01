import logging
import os
from typing import Optional

from .base_model import BaseLlamaModel

logger = logging.getLogger(__name__)


class LlamaModel(BaseLlamaModel):
    """
    LLaMA 2 7B Chat (no LoRA for now).
    """

    def __init__(
        self,
        gpu: bool,
        n_ctx: Optional[int] = None,
        n_gpu_layers: Optional[int] = None,
        n_threads: Optional[int] = None,
    ):
        model_path = os.getenv(
            "LLAMA_MODEL_PATH", "/models/llama/llama-2-7b-chat.Q4_K_M.gguf"
        )

        ctx = n_ctx or int(os.getenv("LLAMA_N_CTX", "2048"))
        threads = n_threads or int(os.getenv("LLM_N_THREADS", "8"))

        if gpu:
            gpu_layers = n_gpu_layers or int(os.getenv("LLAMA_GPU_LAYERS", "35"))
        else:
            gpu_layers = 0

        super().__init__(
            name=f"llama2-7b-{'gpu' if gpu else 'cpu'}",
            model_path=model_path,
            n_ctx=ctx,
            n_gpu_layers=gpu_layers,
            n_threads=threads,
            lora_paths=None,
            lora_scaling=None,
            use_mmap=True,
        )
