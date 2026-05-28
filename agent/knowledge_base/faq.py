"""
FAQ i instrukcje specyficzne dla powtarzalnych problemów technicznych.
"""

FAQ = """
=== FAQ – PROBLEMY TECHNICZNE ===

## Błąd 401 Unauthorized
Przyczyna: nieprawidłowy lub wygasły klucz API.
Rozwiązanie: sprawdź klucz w dashboardzie → Profile → API Keys. Upewnij się, że nagłówek to
xi-api-key, a nie Authorization Bearer.

## Błąd 422 Unprocessable Entity
Przyczyna: niepoprawny format body żądania lub brakujące wymagane pole.
Rozwiązanie: sprawdź dokumentację endpointu, zweryfikuj JSON, użyj walidatora.

## Dźwięk jest zniekształcony lub ma artefakty
Przyczyna: zbyt wysokie wartości similarity_boost lub stability poniżej 0.3.
Rozwiązanie: ustaw stability między 0.4–0.7, similarity_boost między 0.5–0.8.

## Agent Conversational AI nie odbiera połączeń
Przyczyna: webhook URL nie jest publicznie dostępny lub certyfikat TLS wygasł.
Rozwiązanie: użyj ngrok do testów lokalnych, upewnij się, że URL zwraca 200 OK.

## Jak zintegrować z Twilio?
Kroki:
1. W dashboardzie ElevenLabs utwórz agenta i skopiuj jego ID.
2. W Twilio skonfiguruj Stream na WebSocket URL agenta ElevenLabs.
3. Użyj TwiML <Stream> z url="wss://api.elevenlabs.io/v1/convai/conversation?agent_id=X"
4. Dodaj xi-api-key w parametrach WebSocket.

## Jak zmienić LLM w agencie?
W konfiguracji agenta (POST /v1/convai/agents) zmień pole:
"llm": { "model": "claude-sonnet-4-5" }
Dostępne opcje: claude-sonnet-4-5, gpt-4o, gemini-1.5-pro

## Jak korzystać z Voice Cloning?
1. Nagraj min. 60 sekund czystego głosu (bez szumów tła).
2. Prześlij przez POST /v1/voices/add lub dashboard.
3. Skopiuj voice_id z odpowiedzi.
4. Użyj voice_id w żądaniach TTS.

## Obsługiwane języki – jak ustawić?
W parametrze body TTS nie ma pola "language" – model automatycznie wykrywa język tekstu.
Dla najlepszych wyników z wielojęzycznością używaj eleven_multilingual_v2.

## Jak sprawdzić zużycie znaków?
GET /v1/user/subscription – pole "character_count" i "character_limit".

## Jak działa interruption handling w Conversational AI?
Agent automatycznie wykrywa, gdy użytkownik zaczyna mówić podczas wypowiedzi agenta.
Przerwa powoduje zatrzymanie syntezy i ponowne przetworzenie pytania użytkownika.
Czułość można konfigurować parametrem interruption_threshold (0.0–1.0).

## Jak połączyć agenta z własną bazą wiedzy?
1. W dashboardzie agenta wybierz zakładkę "Knowledge Base".
2. Dodaj dokumenty (PDF, TXT, URL).
3. Agent używa RAG (Retrieval-Augmented Generation) do odpowiedzi.

=== MODELE CENOWE ===
- Rozliczenie: per znak (character-based billing)
- Znaki liczone są po stronie TTS, nie STT
- Conversational AI: znaki na wyjściu agenta
- API vs Dashboard: te same ceny
- Roczny abonament: 20% taniej vs miesięczny
"""
