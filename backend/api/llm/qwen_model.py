import logging
import os
from typing import Optional
from pathlib import Path

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
        # Get API directory (where app.py is located)
        # This file is in llm/, so go up one level to get api/
        api_dir = Path(__file__).parent.parent.absolute()
        models_dir = api_dir / "models" / "qwen"
        
        # Default paths: use local models directory if env vars not set
        default_model_path = str(models_dir / "Qwen2.5-7B-Instruct-Q8_0.gguf")
        default_lora_path = str(models_dir / "legal_lora_adapter_only_25k.gguf")
        
        model_path = os.getenv("QWEN_MODEL_PATH", default_model_path)
        lora_path = os.getenv("QWEN_LORA_PATH", default_lora_path)
        
        # Verify files exist (for better error messages)
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Qwen model not found at: {model_path}\n"
                f"Please set QWEN_MODEL_PATH environment variable or place the model file at: {default_model_path}"
            )
        if not os.path.exists(lora_path):
            raise FileNotFoundError(
                f"Qwen LoRA adapter not found at: {lora_path}\n"
                f"Please set QWEN_LORA_PATH environment variable or place the adapter file at: {default_lora_path}"
            )
        
        logger.info(f"Using Qwen model: {model_path}")
        logger.info(f"Using Qwen LoRA: {lora_path}")

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
            lora_paths=[lora_path],
            lora_scaling=[1.0],
            use_mmap=True,
        )
