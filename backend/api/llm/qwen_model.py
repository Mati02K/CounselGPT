import logging
import os
from typing import Optional

from .base_model import BaseLlamaModel

logger = logging.getLogger(__name__)


class QwenModel(BaseLlamaModel):
    """
    Qwen2.5-7B-Instruct + LoRA adapter (always applied).
    """

    def __init__(
        self,
        gpu: bool,
        n_ctx: Optional[int] = None,
        n_gpu_layers: Optional[int] = None,
        n_threads: Optional[int] = None,
    ):
        model_path = os.getenv(
            "QWEN_MODEL_PATH", "/models/qwen/Qwen2.5-7B-Instruct-Q8_0.gguf"
        )
        # lora_path = os.getenv(
        #     "QWEN_LORA_PATH", "/models/qwen/legal_lora_adapter_only_25k.gguf"
        # )

        # Optimized for L4 GPU - reduce context for faster inference
        ctx = n_ctx or int(os.getenv("QWEN_N_CTX", "2048"))
        
        # L4 has 24 cores, use all for CPU parts
        threads = n_threads or int(os.getenv("LLM_N_THREADS", "24"))

        if gpu:
            # Load all layers to GPU for maximum speed
            gpu_layers = n_gpu_layers or int(os.getenv("QWEN_GPU_LAYERS", "-1"))
        else:
            gpu_layers = 0

        super().__init__(
            name=f"qwen-7b-{'gpu' if gpu else 'cpu'}",
            model_path=model_path,
            n_ctx=ctx,
            n_gpu_layers=gpu_layers,
            n_threads=threads,
            # lora_paths=[lora_path],
            lora_scaling=[1.0],
            use_mmap=True,
        )
