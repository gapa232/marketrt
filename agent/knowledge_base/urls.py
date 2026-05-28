"""
Mapowanie URLi dla narzędzi przekierowujących.
"""

URLS = {
    "docs_main": "https://elevenlabs.io/docs",
    "docs_tts": "https://elevenlabs.io/docs/api-reference/text-to-speech",
    "docs_convai": "https://elevenlabs.io/docs/conversational-ai/overview",
    "docs_telephony": "https://elevenlabs.io/docs/conversational-ai/guides/twilio",
    "docs_voice_cloning": "https://elevenlabs.io/docs/voices/voice-cloning",
    "docs_stt": "https://elevenlabs.io/docs/api-reference/speech-to-text",
    "docs_dubbing": "https://elevenlabs.io/docs/dubbing/overview",
    "docs_sdk_python": "https://github.com/elevenlabs/elevenlabs-python",
    "docs_sdk_js": "https://github.com/elevenlabs/elevenlabs-js",
    "enterprise_sales": "https://elevenlabs.io/enterprise",
    "discord": "https://discord.gg/elevenlabs",
    "pricing": "https://elevenlabs.io/pricing",
    "dashboard": "https://elevenlabs.io/app",
    "status": "https://status.elevenlabs.io",
    "changelog": "https://elevenlabs.io/changelog",
}

DOC_TOPIC_MAP = {
    "api": "docs_tts",
    "text to speech": "docs_tts",
    "tts": "docs_tts",
    "conversational": "docs_convai",
    "agent": "docs_convai",
    "telephony": "docs_telephony",
    "twilio": "docs_telephony",
    "voice cloning": "docs_voice_cloning",
    "cloning": "docs_voice_cloning",
    "speech to text": "docs_stt",
    "stt": "docs_stt",
    "transcription": "docs_stt",
    "dubbing": "docs_dubbing",
    "python sdk": "docs_sdk_python",
    "javascript sdk": "docs_sdk_js",
    "js sdk": "docs_sdk_js",
    "pricing": "pricing",
    "enterprise": "enterprise_sales",
    "discord": "discord",
}


def resolve_doc_url(topic: str) -> str:
    topic_lower = topic.lower()
    for key, url_key in DOC_TOPIC_MAP.items():
        if key in topic_lower:
            return URLS[url_key]
    return URLS["docs_main"]
