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
        """Create a new Instance of the CounselGPTModel

        Args:
            model_path (str): Place where model resides
            n_gpu_layers (int, optional): No of GPU Layers to use (GPU Acceleration). Defaults to 35.

        Returns:
            _type_: Instance of the model which would be a singleton.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CounselGPTModel, cls).__new__(cls)
                    cls._instance._initialize(model_path, n_gpu_layers)
        return cls._instance

    def _initialize(self, model_path, n_gpu_layers):
        """Actual Initilization of the model

        Args:
            model_path (_type_): Place where model resides
            n_gpu_layers (_type_): No of GPU Layers to use (GPU Acceleration). Defaults to 35.
        """
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
            raise FileNotFoundError("Model Not found")

    def infer(self, prompt: str, max_tokens: int = 300) -> str:
        """Inference of the CounselGPT Model

        Args:
            prompt (str): User Prompt
            max_tokens (int, optional): Max Token needed. Defaults to 300.

        Raises:
            ValueError: If prompt is empty
            ValueError: If tokens is over 2048.
            RuntimeError: Any run time error during model inference

        Returns:
            str: Output for the user's prompt
        """
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
