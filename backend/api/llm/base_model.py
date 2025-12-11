import logging
import os
import threading
from typing import List, Optional

from llama_cpp import Llama

logger = logging.getLogger(__name__)


class BaseLlamaModel:
    """
    Thin wrapper around llama_cpp.Llama with:
      - common init params
      - basic validation
      - single-inference lock
    """

    def __init__(
        self,
        name: str,
        model_path: str,
        n_ctx: int = 2048,
        n_gpu_layers: int = 0,
        n_threads: Optional[int] = None,
        lora_paths: Optional[List[str]] = None,
        lora_scaling: Optional[List[float]] = None,
        use_mmap: bool = True,
        n_batch: Optional[int] = None,  # Batch size for prompt processing
        use_mlock: bool = False,  # Don't lock memory (let OS manage)
    ):
        self.name = name
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.n_threads = n_threads
        self.lora_paths = lora_paths
        self.lora_scaling = lora_scaling
        self.use_mmap = use_mmap
        # Allow n_batch to be configured via env var for CPU optimization
        self.n_batch = n_batch or int(os.getenv("LLM_N_BATCH", "512"))
        self.use_mlock = use_mlock

        self._inference_lock = threading.Lock()

        logger.info(
            f"[{self.name}] Loading model from {self.model_path} "
            f"(ctx={self.n_ctx}, gpu_layers={self.n_gpu_layers}, "
            f"threads={self.n_threads}, batch={self.n_batch}, lora={self.lora_paths})"
        )

        try:
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                n_threads=self.n_threads,
                n_batch=self.n_batch,
                use_mmap=self.use_mmap,
                use_mlock=self.use_mlock,
                lora_paths=self.lora_paths,
                lora_scaling=self.lora_scaling,
                verbose=False,
                # Optimizations
                rope_freq_base=0.0,  # Auto-detect
                rope_freq_scale=0.0,  # Auto-detect
            )
            logger.info(f"[{self.name}] Model loaded successfully")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to load model: {e}")
            raise

    def infer(self, prompt: str, max_tokens: int = 300) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if max_tokens < 1 or max_tokens > 2048:
            raise ValueError("max_tokens must be between 1 and 2048")

        with self._inference_lock:
            try:
                logger.info(f"[{self.name}] Generating response (max_tokens={max_tokens})")
                res = self.model(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=0.7,  # Balanced creativity
                    top_p=0.9,  # Nucleus sampling
                    top_k=40,  # Top-K sampling
                    repeat_penalty=1.1,  # Reduce repetition
                    stop=["<|im_end|>", "<|im_start|>", "User:", "\n\n\n"],  # Qwen chat template stop tokens
                    echo=False,  # Don't echo prompt
                )
                text = res["choices"][0]["text"].strip()
                logger.info(f"[{self.name}] Generated {len(text)} chars")
                return text
            except Exception as e:
                logger.error(f"[{self.name}] Inference failed: {e}")
                raise RuntimeError(f"Model inference failed: {e}")
