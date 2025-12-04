import logging
from typing import Dict, Optional

from .qwen_model import QwenModel
from .llama_model import LlamaModel

logger = logging.getLogger(__name__)

# model_name -> {"gpu": instance or None, "cpu": instance or None}
_models: Dict[str, Dict[str, Optional[object]]] = {
    "qwen": {"gpu": None, "cpu": None},
    "llama": {"gpu": None, "cpu": None},
}


def _preload_qwen_gpu():
    try:
        logger.info("Preloading Qwen GPU model at startup...")
        _models["qwen"]["gpu"] = QwenModel(gpu=True)
        logger.info("Qwen GPU model loaded")
    except Exception as e:
        logger.error(f"Failed to preload Qwen GPU model: {e}")


# Preload only Qwen GPU at import time
_preload_qwen_gpu()


def get_model(model_name: str = "qwen", use_gpu: bool = True):
    """
    Returns a cached model instance (lazy-load when needed).
    model_name: "qwen" or "llama"
    use_gpu: True -> GPU instance, False -> CPU instance
    """
    name = model_name.lower()
    if name not in _models:
        raise ValueError(f"Unknown model_name: {model_name}")

    mode = "gpu" if use_gpu else "cpu"

    if _models[name][mode] is None:
        logger.info(f"Lazy-loading {name.upper()} ({mode}) model...")
        if name == "qwen":
            _models[name][mode] = QwenModel(gpu=use_gpu)
        elif name == "llama":
            _models[name][mode] = LlamaModel(gpu=use_gpu)
        logger.info(f"{name.upper()} ({mode}) model loaded")

    return _models[name][mode]
