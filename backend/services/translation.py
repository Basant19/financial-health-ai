# backend/services/translation.py

from typing import Optional
import os
from backend.services.ai_service import FinancialAIService
from backend.utils.logger import get_logger
from langchain.messages import HumanMessage
from langchain.chat_models import init_chat_model

# -----------------------------
# Logger
# -----------------------------
logger = get_logger("TranslationService")


class Translator:
    """
    Handles multilingual translation of AI-generated financial reports.
    Supports English (en), Hindi (hi), Spanish (es).
    """

    SUPPORTED_LANGUAGES = {"en", "hi", "es"}

    def __init__(self, ai_service: Optional[FinancialAIService] = None):
        """
        Initialize translator. Uses the base_llm from FinancialAIService if available.
        """
        self.ai_service = ai_service or FinancialAIService()
        
        # We ensure we have a plain-text LLM reference
        # If the ai_service has base_llm, use it; otherwise init a clean one
        if hasattr(self.ai_service, 'base_llm'):
            self.model = self.ai_service.base_llm
        else:
            self.model = init_chat_model(
                "google_genai:gemini-2.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.1
            )
        
        logger.info("Translator initialized with plain-text model")

    def translate_report(self, text: str, target_language: str) -> str:
        """
        Translates report using the base LLM to avoid JSON schema conflicts.
        """
        if not target_language or target_language.lower() == "en":
            return text

        target_lang_clean = target_language.lower()
        if target_lang_clean not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Unsupported language '{target_lang_clean}' — skipping")
            return text

        logger.info(f"Translating report to: {target_lang_clean}")

        # Precise prompt for high-quality financial translation
        prompt = f"""You are a professional financial translator. 
Translate the following SME financial report into {target_lang_clean}.
Maintain the formal tone and preserve all financial metrics and terms (e.g. Net Cashflow, Margin).
Return ONLY the translated text without any preamble or quotes.

Report:
{text}"""

        try:
            # We use the PLAIN model here, so .content will exist!
            response = self.model.invoke([HumanMessage(content=prompt)])
            translated_text = response.content.strip()

            if not translated_text:
                raise ValueError("LLM returned an empty string for translation")

            # Clean up potential markdown formatting
            translated_text = translated_text.replace("```", "").strip()

            logger.info(f"Translation successfully completed for {target_lang_clean}")
            return translated_text

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            # Return original English text so the user still sees something
            return text