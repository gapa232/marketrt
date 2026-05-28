"""
Konfiguracja agenta Alexis dla ElevenLabs Conversational AI.
"""

import os
from dataclasses import dataclass, field
from agent.tools import TOOL_SCHEMAS


@dataclass
class VoiceSettings:
    stability: float = 0.55
    similarity_boost: float = 0.70
    style: float = 0.20
    use_speaker_boost: bool = True


@dataclass
class LLMConfig:
    model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "claude-sonnet-4-5"))
    temperature: float = 0.3
    max_tokens: int = 256


@dataclass
class AgentConfig:
    name: str = "Alexis"
    voice_id: str = field(default_factory=lambda: os.getenv("VOICE_ID", ""))
    tts_model: str = "eleven_turbo_v2_5"
    stt_model: str = "nova-2"

    llm: LLMConfig = field(default_factory=LLMConfig)
    voice_settings: VoiceSettings = field(default_factory=VoiceSettings)

    # Interruption handling – wrażliwość wykrywania przerw użytkownika
    interruption_threshold: float = 0.5

    # Limit dzienny połączeń (monitoring)
    daily_call_target: int = 200

    # Cel skuteczności
    target_solve_rate: float = 0.80

    tools: list = field(default_factory=lambda: TOOL_SCHEMAS)

    def to_elevenlabs_payload(self, system_prompt: str, knowledge_base_text: str) -> dict:
        return {
            "name": self.name,
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": system_prompt,
                        "llm": self.llm.model,
                        "temperature": self.llm.temperature,
                        "max_tokens": self.llm.max_tokens,
                        "tools": self.tools,
                        "knowledge_base": [
                            {
                                "type": "text",
                                "name": "ElevenLabs Knowledge Base",
                                "id": "kb_main",
                                "content": knowledge_base_text,
                            }
                        ],
                    },
                    "first_message": (
                        "Hi, I'm Alexis from ElevenLabs support. "
                        "What technical question can I help you with today?"
                    ),
                    "language": "en",
                },
                "tts": {
                    "model_id": self.tts_model,
                    "voice_id": self.voice_id,
                    "voice_settings": {
                        "stability": self.voice_settings.stability,
                        "similarity_boost": self.voice_settings.similarity_boost,
                        "style": self.voice_settings.style,
                        "use_speaker_boost": self.voice_settings.use_speaker_boost,
                    },
                },
                "stt": {
                    "model_id": self.stt_model,
                },
                "conversation": {
                    "interruption_threshold": self.interruption_threshold,
                    "record_conversation": True,
                },
            },
        }
