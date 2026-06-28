"""The translate tool.

Unlike the file tools, this one calls back out to Sarvam — but to a *different*
endpoint than the chat loop. The chat model (`sarvam-30b`) is multilingual and
could translate by prompting alone, but Sarvam's dedicated Translate model is
purpose-built and exposes controls the chat path doesn't: `mode` (formal vs
colloquial vs code-mixed), `output_script` (native script, roman
transliteration, spoken form), speaker gender and numeral formatting.

Two things differ from the chat call in main.py:
  * endpoint is `https://api.sarvam.ai/translate` (not chat completions)
  * auth is the `api-subscription-key` header (not `Authorization: Bearer`)

We read SARVAM_API_KEY from the environment here so the ToolDefinition stays a
plain `args -> str` callable, matching the other tools.
"""

import json
import os
from typing import Any

import httpx

from tool import ToolDefinition

TRANSLATE_URL = "https://api.sarvam.ai/translate"

# sarvam-translate:v1 covers all 22 scheduled languages, allows 2000 input chars,
# and supports every mode; mayura:v1 is the older 1000-char model.
TRANSLATE_MODEL = "sarvam-translate:v1"

# Supported language codes (BCP-47-ish), e.g. kn-IN for Kannada.
LANGUAGE_CODES = [
    "auto", "en-IN", "hi-IN", "bn-IN", "gu-IN", "kn-IN", "ml-IN", "mr-IN",
    "od-IN", "pa-IN", "ta-IN", "te-IN", "as-IN", "brx-IN", "doi-IN", "kok-IN",
    "ks-IN", "mai-IN", "mni-IN", "ne-IN", "sa-IN", "sat-IN", "sd-IN", "ur-IN",
]


def translate(args: dict[str, Any]) -> str:
    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        return json.dumps({"error": "SARVAM_API_KEY is not set"})

    body: dict[str, Any] = {
        "input": args["input"],
        "source_language_code": args.get("source_language_code", "auto"),
        "target_language_code": args["target_language_code"],
        "model": TRANSLATE_MODEL,
    }
    # Only forward optional controls when the model supplied them.
    for key in ("mode", "output_script", "speaker_gender", "numerals_format"):
        if args.get(key):
            body[key] = args[key]

    resp = httpx.post(
        TRANSLATE_URL,
        headers={
            "api-subscription-key": api_key,
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60.0,
    )

    try:
        data = resp.json()
    except ValueError:
        return json.dumps({"error": f"translate returned {resp.status_code}: {resp.text}"})

    if resp.status_code != 200:
        return json.dumps({"error": data})

    return json.dumps(
        {
            "translated_text": data.get("translated_text", ""),
            "source_language_code": data.get("source_language_code"),
        }
    )


TranslateTool = ToolDefinition(
    name="translate",
    description=(
        "Translate text between Indian languages (and English) using Sarvam's "
        "dedicated translation model. Use this for accurate, controllable "
        "translation rather than translating in your own reply. Language codes "
        "are BCP-47 style, e.g. 'en-IN' (English), 'kn-IN' (Kannada), "
        "'hi-IN' (Hindi). Use 'auto' as the source to auto-detect."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "input": {
                "type": "string",
                "description": "The text to translate (up to 2000 characters).",
            },
            "source_language_code": {
                "type": "string",
                "enum": LANGUAGE_CODES,
                "description": "Source language code, or 'auto' to detect. Defaults to 'auto'.",
            },
            "target_language_code": {
                "type": "string",
                "enum": [c for c in LANGUAGE_CODES if c != "auto"],
                "description": "Target language code, e.g. 'kn-IN' for Kannada.",
            },
            "mode": {
                "type": "string",
                "enum": ["formal", "modern-colloquial", "classic-colloquial", "code-mixed"],
                "description": "Translation register. Optional; defaults to formal.",
            },
            "output_script": {
                "type": "string",
                "enum": ["roman", "fully-native", "spoken-form-in-native"],
                "description": "Script of the output. Optional; defaults to native script.",
            },
        },
        "required": ["input", "target_language_code"],
    },
    function=translate,
)
