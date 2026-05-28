"""
Podsumowanie dokumentacji produktowej ElevenLabs.
Źródło prawdy dla agenta – ogranicza halucynacje do ekosystemu ElevenLabs.
"""

PRODUCT_DOCS = """
=== ELEVENLABS – PRZEGLĄD PRODUKTÓW ===

## Text to Speech (TTS)
- Konwertuje tekst na mowę z użyciem modeli głosowych AI.
- Obsługiwane języki: ponad 30, w tym polski, angielski, hiszpański, niemiecki, francuski.
- API endpoint: POST /v1/text-to-speech/{voice_id}
- Parametry: model_id, voice_settings (stability, similarity_boost, style, use_speaker_boost)
- Modele: eleven_multilingual_v2, eleven_turbo_v2_5, eleven_monolingual_v1
- Streaming: POST /v1/text-to-speech/{voice_id}/stream

## Speech to Text (STT)
- Transkrypcja audio na tekst.
- API endpoint: POST /v1/speech-to-text
- Format wejściowy: audio/mpeg, audio/wav, audio/webm
- Obsługuje diarizację (rozróżnianie mówców)

## Voice Cloning
- Klonowanie głosu na podstawie próbki audio.
- Instant Voice Cloning: POST /v1/voices/add (min. 1 minuta czystego audio)
- Professional Voice Cloning: wymaga min. 30 minut materiału
- API endpoint zarządzania: GET/DELETE /v1/voices/{voice_id}

## Conversational AI
- Budowanie agentów głosowych w czasie rzeczywistym.
- Architektura: Speech-to-Text → LLM → Text-to-Speech w pętli.
- WebSocket endpoint: wss://api.elevenlabs.io/v1/convai/conversation
- Obsługiwane LLM: Claude (Anthropic), GPT-4 (OpenAI), Gemini (Google)
- Latencja: zoptymalizowana do <1s end-to-end przy eleven_turbo_v2_5
- Zarządzanie agentami: POST /v1/convai/agents, GET /v1/convai/agents/{agent_id}

## Sound Effects
- Generowanie efektów dźwiękowych z opisu tekstowego.
- API endpoint: POST /v1/sound-generation

## Dubbing
- Automatyczne tłumaczenie i dubbing wideo/audio.
- API endpoint: POST /v1/dubbing
- Obsługuje: mp4, mp3, wav, mov

## Voice Design
- Tworzenie syntetycznych głosów z opisu.
- API endpoint: POST /v1/voice-generation/generate

=== INTEGRACJA Z TELEFONIĄ ===
- ElevenLabs integruje się z Twilio, Vonage oraz SIP trunking.
- Webhook dla połączeń przychodzących: konfiguracja w dashboardzie agenta.
- DTMF (touch-tone): obsługiwane przez parametr dtmf w konfiguracji agenta.
- Nagrywanie rozmów: opcja record_conversation w ustawieniach agenta.

=== MODELE GŁOSOWE ===
| Model                   | Latencja | Jakość | Języki |
|-------------------------|----------|--------|--------|
| eleven_turbo_v2_5       | Niska    | Wysoka | 32     |
| eleven_multilingual_v2  | Średnia  | B. wys | 30+    |
| eleven_monolingual_v1   | Niska    | Dobra  | EN     |

=== LIMITY I PLANY ===
- Free: 10,000 znaków/miesiąc, brak API
- Starter: 30,000 znaków, dostęp do API
- Creator: 100,000 znaków
- Pro: 500,000 znaków
- Scale: 2,000,000 znaków
- Enterprise: nielimitowane, dedykowane wsparcie, SLA
"""
