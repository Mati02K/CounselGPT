import logging
from typing import Literal, Optional
from llm.model_factory import get_model
from prompt import SYSTEM_PROMPT, RAG_SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CounselGPTModel:
    """
    Thin wrapper that:
      - chooses the right model via the factory (qwen/llama, gpu/cpu)
      - attaches system prompt (with or without RAG context)
      - injects a dynamic length constraint based on max_tokens
    """

    def __init__(
        self,
        model_name: Literal["qwen", "llama"] = "qwen",
        use_gpu: bool = True,
    ):
        self.model_name = model_name
        self.use_gpu = use_gpu

    def infer(
        self, 
        prompt: str, 
        max_tokens: int = 300,
        rag_context: Optional[str] = None
    ) -> str:
        """
        Run inference with optional RAG context.
        
        Args:
            prompt: User prompt or conversation
            max_tokens: Maximum tokens to generate
            rag_context: Optional retrieved document context from RAG
        
        Returns:
            Generated response text
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if max_tokens < 1 or max_tokens > 2048:
            raise ValueError("max_tokens must be between 1 and 2048")

        # Build system message with length constraint
        word_budget = max_tokens
        
        # Choose system prompt based on RAG context
        if rag_context and rag_context.strip():
            # Use RAG-enhanced system prompt with document context
            base_system = RAG_SYSTEM_PROMPT.format(context=rag_context)
            logger.info(f"[{self.model_name}] Using RAG context ({len(rag_context)} chars)")
        else:
            # Use standard system prompt
            base_system = SYSTEM_PROMPT
            logger.info(f"[{self.model_name}] No RAG context, using standard prompt")
        
        system_message = (
            f"{base_system.strip()}\n\n"
            f"IMPORTANT: Keep your response under {word_budget} words. "
            f"Be concise and direct."
        )
        
        # Use proper Qwen chat template
        # Format: <|im_start|>role\ncontent<|im_end|>
        final_prompt = (
            f"<|im_start|>system\n{system_message}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        logger.info(
            f"[{self.model_name}] Final prompt length={len(final_prompt)}, "
            f"word_budget={word_budget}, "
            f"rag_context={'yes' if rag_context else 'no'}"
        )

        # Get the underlying llama.cpp model (qwen/llama, gpu/cpu)
        model = get_model(self.model_name, self.use_gpu)

        # Delegate to BaseLlamaModel.infer (which calls llama_cpp with max_tokens)
        return model.infer(final_prompt, max_tokens=max_tokens)
