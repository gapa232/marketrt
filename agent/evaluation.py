"""
System ewaluacji konwersacji agenta Alexis.
Metryki: hallucination_kb, solved_user_inquiry, positive_interaction.
Opiera się na podejściu LLM-as-Judge z konserwatywną kalibracją (dolna granica ROI).
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
from anthropic import Anthropic


@dataclass
class ConversationTurn:
    role: str  # "user" | "agent"
    content: str


@dataclass
class EvaluationResult:
    hallucination_kb: bool
    solved_user_inquiry: bool
    positive_interaction: bool
    confidence: float  # 0.0–1.0
    reasoning: str
    raw_score: float = field(init=False)

    def __post_init__(self):
        self.raw_score = sum([
            not self.hallucination_kb,
            self.solved_user_inquiry,
            self.positive_interaction,
        ]) / 3.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SessionMetrics:
    session_id: str
    total_conversations: int = 0
    hallucination_count: int = 0
    solved_count: int = 0
    positive_count: int = 0
    empty_calls: int = 0

    @property
    def effective_conversations(self) -> int:
        return self.total_conversations - self.empty_calls

    @property
    def solve_rate(self) -> float:
        if self.effective_conversations == 0:
            return 0.0
        return self.solved_count / self.effective_conversations

    @property
    def hallucination_rate(self) -> float:
        if self.effective_conversations == 0:
            return 0.0
        return self.hallucination_count / self.effective_conversations

    @property
    def positive_rate(self) -> float:
        if self.effective_conversations == 0:
            return 0.0
        return self.positive_count / self.effective_conversations

    def update(self, result: EvaluationResult, is_empty_call: bool = False):
        self.total_conversations += 1
        if is_empty_call:
            self.empty_calls += 1
            return
        if result.hallucination_kb:
            self.hallucination_count += 1
        if result.solved_user_inquiry:
            self.solved_count += 1
        if result.positive_interaction:
            self.positive_count += 1

    def report(self) -> dict:
        return {
            "session_id": self.session_id,
            "total_conversations": self.total_conversations,
            "effective_conversations": self.effective_conversations,
            "empty_calls": self.empty_calls,
            "solve_rate": f"{self.solve_rate:.1%}",
            "hallucination_rate": f"{self.hallucination_rate:.1%}",
            "positive_rate": f"{self.positive_rate:.1%}",
            "target_solve_rate": "80%",
            "meets_target": self.solve_rate >= 0.80,
        }


EVAL_PROMPT = """
You are evaluating a voice support conversation between a user and an AI agent named Alexis.
The agent uses a knowledge base (KB) to answer questions about ElevenLabs products.

Evaluate the conversation on three binary metrics:

1. hallucination_kb: Did the agent state any fact NOT supported by the knowledge base
   or contradict it? Answer true if hallucination occurred, false if the agent stayed
   within the KB.

2. solved_user_inquiry: Was the user's primary question answered correctly,
   OR was a valid handoff made (to docs, email, or external URL)?
   Answer true if resolved, false if the user's need was left unaddressed.

3. positive_interaction: Did the conversation feel natural, concise, and helpful
   from a user experience perspective? Answer true if yes.

Also provide:
- confidence: your confidence in this evaluation (0.0–1.0)
- reasoning: one sentence explaining your judgment

Respond ONLY with valid JSON matching this schema:
{{
  "hallucination_kb": boolean,
  "solved_user_inquiry": boolean,
  "positive_interaction": boolean,
  "confidence": float,
  "reasoning": string
}}

=== CONVERSATION ===
{conversation}
"""


class MockEvaluator:
    """
    Heurystyczny ewaluator offline (bez API).
    Używany gdy ANTHROPIC_API_KEY niedostępny – tryb demo/CI.
    """

    _HALLUCINATION_SIGNALS = ["microsoft", "google tts", "azure", "openai whisper"]
    _UNSOLVED_SIGNALS = ["i don't know", "i cannot", "i'm unable", "not sure"]
    _NEGATIVE_SIGNALS = ["sorry", "unfortunately", "i apologize", "can't help"]

    def evaluate(self, turns: list[ConversationTurn]) -> EvaluationResult:
        if not any(t.role == "user" and t.content.strip() for t in turns):
            return EvaluationResult(
                hallucination_kb=False,
                solved_user_inquiry=False,
                positive_interaction=False,
                confidence=1.0,
                reasoning="Empty call – user did not ask a question.",
            )

        agent_text = " ".join(
            t.content.lower() for t in turns if t.role == "agent"
        )

        hallucination = any(s in agent_text for s in self._HALLUCINATION_SIGNALS)
        unsolved = any(s in agent_text for s in self._UNSOLVED_SIGNALS)
        negative = any(s in agent_text for s in self._NEGATIVE_SIGNALS)

        return EvaluationResult(
            hallucination_kb=hallucination,
            solved_user_inquiry=not unsolved,
            positive_interaction=not negative,
            confidence=0.65,
            reasoning="[mock] Heuristic evaluation – no LLM API available.",
        )

    def batch_evaluate(
        self,
        conversations: list[list[ConversationTurn]],
        session_id: str = "batch",
    ) -> tuple[list[EvaluationResult], SessionMetrics]:
        metrics = SessionMetrics(session_id=session_id)
        results = []
        for turns in conversations:
            is_empty = not any(t.role == "user" and t.content.strip() for t in turns)
            result = self.evaluate(turns)
            metrics.update(result, is_empty_call=is_empty)
            results.append(result)
        return results, metrics


class ConversationEvaluator:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-6"

    def evaluate(self, turns: list[ConversationTurn]) -> EvaluationResult:
        conversation_text = "\n".join(
            f"{t.role.upper()}: {t.content}" for t in turns
        )

        if not any(t.role == "user" and t.content.strip() for t in turns):
            return EvaluationResult(
                hallucination_kb=False,
                solved_user_inquiry=False,
                positive_interaction=False,
                confidence=1.0,
                reasoning="Empty call – user did not ask a question.",
            )

        prompt = EVAL_PROMPT.format(conversation=conversation_text)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.content[0].text.strip()
        data = json.loads(raw)

        return EvaluationResult(
            hallucination_kb=data["hallucination_kb"],
            solved_user_inquiry=data["solved_user_inquiry"],
            positive_interaction=data["positive_interaction"],
            confidence=float(data["confidence"]),
            reasoning=data["reasoning"],
        )

    def batch_evaluate(
        self,
        conversations: list[list[ConversationTurn]],
        session_id: str = "batch",
    ) -> tuple[list[EvaluationResult], SessionMetrics]:
        metrics = SessionMetrics(session_id=session_id)
        results = []

        for turns in conversations:
            is_empty = not any(t.role == "user" and t.content.strip() for t in turns)
            result = self.evaluate(turns)
            metrics.update(result, is_empty_call=is_empty)
            results.append(result)

        return results, metrics
