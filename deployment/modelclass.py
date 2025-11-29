from llama_cpp import Llama
import threading
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CounselGPTModel:
    _instance = None
    _lock = threading.Lock()
    _inference_lock = threading.Lock()  # Lock for inference

    def __new__(cls, model_path: str, n_gpu_layers: int = 35):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CounselGPTModel, cls).__new__(cls)
                    cls._instance._initialize(model_path, n_gpu_layers)
        return cls._instance

    def _initialize(self, model_path, n_gpu_layers):
        try:
            logger.info(f"Loading LLaMA model from {model_path}...")
            self.model = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,
                n_ctx=2048,
                verbose=False
            )
            logger.info("LLaMA model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def infer(self, prompt: str, max_tokens: int = 300) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if max_tokens < 1 or max_tokens > 2048:
            raise ValueError("max_tokens must be between 1 and 2048")
        
        # Allow only one inference at a time
        # TODO need to work around a way to add some sort of queue to overcome this
        with self._inference_lock:
            try:
                logger.info(f"Generating response (max_tokens={max_tokens})...")
                response = self.model(prompt, max_tokens=max_tokens)
                result = response["choices"][0]["text"].strip()
                logger.info(f"Response generated successfully ({len(result)} chars)")
                return result
            except Exception as e:
                logger.error(f"Inference failed: {str(e)}")
                raise RuntimeError(f"Model inference failed: {str(e)}")
