import logging
from typing import Literal
from llm.model_factory import get_model
from prompt import SYSTEM_PROMPT  # your static system instructions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CounselGPTModel:
    """
    Thin wrapper that:
      - chooses the right model via the factory (qwen/llama, gpu/cpu)
      - attaches system prompt
      - injects a dynamic length constraint based on max_tokens
    """

    def __init__(
        self,
        model_name: Literal["qwen", "llama"] = "qwen",
        use_gpu: bool = True,
    ):
        self.model_name = model_name
        self.use_gpu = use_gpu

    def infer(self, prompt: str, max_tokens: int = 300) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if max_tokens < 1 or max_tokens > 2048:
            raise ValueError("max_tokens must be between 1 and 2048")

        # Roughly treat max_tokens as a word budget for the user
        # (you can tune this factor if needed)
        word_budget = max_tokens

        # Dynamic length instruction tied to max_tokens
        length_instruction = (
            f"\n\nLENGTH CONSTRAINT:\n"
            f"- Your answer MUST be at most {word_budget} words.\n"
            f"- Be concise and stop as soon as you reach this word limit.\n"
            f"- Do NOT exceed {word_budget} words under any circumstance."
        )

        #Build final prompt shown to the model
        final_prompt = (
            f"{SYSTEM_PROMPT}"
            f"{length_instruction}\n\n"
            f"User: {prompt}\n\n"
            f"Assistant:"
        )

        logger.info(
            f"[{self.model_name}] Final prompt length={len(final_prompt)}, "
            f"word_budget={word_budget}"
        )

        # Get the underlying llama.cpp model (qwen/llama, gpu/cpu)
        model = get_model(self.model_name, self.use_gpu)

        # Delegate to BaseLlamaModel.infer (which calls llama_cpp with max_tokens)
        return model.infer(final_prompt, max_tokens=max_tokens)
