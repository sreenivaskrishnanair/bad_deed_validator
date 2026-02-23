from abc import ABC, abstractmethod
from .models import DeedExtract
from dataclasses import dataclass
from openai import OpenAI
import json
from typing import Dict, Any, Optional


# ------------------------------------------------------------
#Errors
# ------------------------------------------------------------
class ExtractorError(RuntimeError):
    pass

class LLMParserError(ExtractorError):
    pass

class SchemaValidationError(ExtractorError):
    pass


# ------------------------------------------------------------
# Base Interface
# ------------------------------------------------------------
class Extractor(ABC):
    @abstractmethod
    def extract(self, ocr_text : str) -> DeedExtract:
        pass

# ------------------------------------------------------------
# LLM Config
# ------------------------------------------------------------
@dataclass(frozen=True)
class LLMConfig:
    model : str
    api_key : str
    base_url : Optional[str] = None


# ------------------------------------------------------------
# LLM Extractor - OpenAI compatible
# ------------------------------------------------------------
class LLMExtractor(Extractor):

    def __init__(self, cfg : LLMConfig):
        self._cfg = cfg
        self._client = OpenAI(
            api_key=cfg.api_key,
            base_url=cfg.base_url,
        )

    def extract(self, ocr_text : str) -> DeedExtract:
        system_prompt = (
            "You extract structured data from OCR text.\n"
            "Return ONLY valid JSON. Valid JSON must match JSON Schema. No markdown. No commentary.\n"
            "DO NOT HALLUCINATE. Do not make up values. If you cannot find a field return null.\n"
            "Adhere to JSON Schema."
        )

        json_schema = DeedExtract.model_json_schema()

        user_prompt = (
            "Extract fields from OCR text and return ONLY a JSON object that conforms to the JSON schema provided.\n"
            "Important:\n"
            "- Output must be strict JSON (no trailing text).\n"
            "- Dates must be format YYYY-MM-DD.\n"
            "- amount_numeric must be a JSON string like \"1250000.00\" (not a number).\n"
            "- Keep amount_words exactly as written in words.\n\n"
            f"JSON Schema:\n{json.dumps(json_schema, indent=2)}\n\n"
            f"OCR: \n{ocr_text}"
        )

        resp = self._client.chat.completions.create(
            model=self._cfg.model,
            temperature=0, # hard coding for extraction
            messages=[
                {
                    "role" : "system", 
                    "content" : system_prompt
                },
                {
                    "role" : "user",
                    "content" : user_prompt
                }
            ]
        )

        content = (resp.choices[0].message.content or "").strip()

        try:
            data : Dict[str, Any] = json.loads(content)
        except Exception as e:
            raise LLMParserError(f"LLM returned non-JSON output (model={self._cfg.model}). Response snippet: {content[:400]!r}")

        try:
            return DeedExtract.model_validate(data)
        except Exception as e:
            raise SchemaValidationError(f"extract schema failed validation {e}")
