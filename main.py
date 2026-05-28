"""
Punkt wejścia systemu agenta głosowego Alexis (ElevenLabs Conversational AI).

Tryby działania:
  python main.py deploy   – rejestruje/aktualizuje agenta w ElevenLabs
  python main.py call     – uruchamia sesję głosową (mikrofon)
  python main.py eval     – uruchamia ewaluację przykładowych rozmów
  python main.py config   – wypisuje aktualną konfigurację (bez kluczy)
"""

import json
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def cmd_deploy():
    from elevenlabs import ElevenLabs
    from agent import AgentConfig, get_system_prompt
    from agent.knowledge_base import FULL_KNOWLEDGE_BASE

    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
    config = AgentConfig()
    payload = config.to_elevenlabs_payload(get_system_prompt(), FULL_KNOWLEDGE_BASE)

    agent_id = os.getenv("AGENT_ID")
    if agent_id:
        result = client.conversational_ai.update_agent(agent_id=agent_id, **payload)
        print(f"Agent updated: {agent_id}")
    else:
        result = client.conversational_ai.create_agent(**payload)
        print(f"Agent created: {result.agent_id}")
        print(f"Add to .env:  AGENT_ID={result.agent_id}")

    return result


def cmd_call():
    from elevenlabs.conversational_ai.conversation import Conversation
    from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
    from elevenlabs import ElevenLabs
    from agent.tools import dispatch_tool

    agent_id = os.environ["AGENT_ID"]
    client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])

    def handle_tool_call(tool_name: str, tool_input: dict) -> str:
        result = dispatch_tool(tool_name, tool_input)
        return json.dumps({"message": result.message, "destination": result.destination})

    conversation = Conversation(
        client=client,
        agent_id=agent_id,
        requires_auth=False,
        audio_interface=DefaultAudioInterface(),
        callback_agent_response=lambda r: print(f"\nAlexis: {r}"),
        callback_user_transcript=lambda t: print(f"You: {t}"),
        callback_agent_response_correction=lambda o, c: print(f"[correction] {o} → {c}"),
        callback_tool_call=handle_tool_call,
    )

    print("Starting voice session with Alexis. Press Ctrl+C to end.\n")
    conversation.start_session()

    try:
        conversation_id = conversation.wait_for_session_end()
        print(f"\nSession ended. ID: {conversation_id}")
    except KeyboardInterrupt:
        print("\nSession terminated by user.")


def cmd_eval():
    from agent.evaluation import ConversationEvaluator, MockEvaluator, ConversationTurn

    if os.getenv("ANTHROPIC_API_KEY"):
        evaluator = ConversationEvaluator()
        print("Mode: LLM-as-Judge (Claude)\n")
    else:
        evaluator = MockEvaluator()
        print("Mode: mock/heuristic (no ANTHROPIC_API_KEY found)\n")

    sample_conversations = [
        [
            ConversationTurn("user", "How do I integrate ElevenLabs with Twilio?"),
            ConversationTurn("agent", "For Twilio integration I'll send you our step-by-step documentation — it's much clearer in written form."),
        ],
        [
            ConversationTurn("user", "My API key isn't working, I keep getting 401."),
            ConversationTurn("agent", "A 401 error means your API key is invalid or expired. Check your dashboard under Profile then API Keys, and make sure you're sending it in the xi-api-key header."),
        ],
        [
            ConversationTurn("user", "I want to talk to enterprise sales."),
            ConversationTurn("agent", "I'll connect you with our enterprise team — they'll walk you through custom pricing and dedicated support options."),
        ],
        [
            ConversationTurn("user", ""),
            ConversationTurn("agent", "Hi, I'm Alexis from ElevenLabs support. What technical question can I help you with today?"),
        ],
    ]

    print("Running evaluation on sample conversations...\n")
    results, metrics = evaluator.batch_evaluate(sample_conversations, session_id="demo")

    for i, result in enumerate(results, 1):
        print(f"Conversation {i}:")
        print(f"  Hallucination: {result.hallucination_kb}")
        print(f"  Solved: {result.solved_user_inquiry}")
        print(f"  Positive: {result.positive_interaction}")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Reasoning: {result.reasoning}\n")

    print("=== SESSION METRICS ===")
    print(json.dumps(metrics.report(), indent=2))


def cmd_config():
    from agent import AgentConfig, get_system_prompt
    from agent.knowledge_base import FULL_KNOWLEDGE_BASE

    config = AgentConfig()
    print(f"Agent name:          {config.name}")
    print(f"TTS model:           {config.tts_model}")
    print(f"LLM model:           {config.llm.model}")
    print(f"Interruption thresh: {config.interruption_threshold}")
    print(f"Daily call target:   {config.daily_call_target}")
    print(f"Target solve rate:   {config.target_solve_rate:.0%}")
    print(f"KB size (chars):     {len(FULL_KNOWLEDGE_BASE):,}")
    print(f"Tools registered:    {len(config.tools)}")
    print(f"System prompt chars: {len(get_system_prompt()):,}")


COMMANDS = {
    "deploy": cmd_deploy,
    "call": cmd_call,
    "eval": cmd_eval,
    "config": cmd_config,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "config"
    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        print(f"Available: {', '.join(COMMANDS)}")
        sys.exit(1)
    COMMANDS[cmd]()
