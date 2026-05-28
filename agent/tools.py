"""
Narzędzia handoff agenta Alexis.
Trzy ścieżki wyjścia zapobiegające "ślepym zaułkom" w UX.
"""

import os
from dataclasses import dataclass
from enum import Enum
from agent.knowledge_base.urls import resolve_doc_url, URLS


class HandoffType(str, Enum):
    DOCS = "docs"
    EMAIL = "email"
    EXTERNAL_URL = "external_url"


@dataclass
class HandoffResult:
    type: HandoffType
    destination: str
    message: str
    success: bool = True


def przekierujDoDokumenty(topic: str) -> HandoffResult:
    """
    Trigger: zapytania wymagające instrukcji krok po kroku lub złożonych detali technicznych.
    Dokumentacja tekstowa jest efektywniejsza niż przekaz głosowy dla złożonych procesów.
    """
    url = resolve_doc_url(topic)
    message = (
        f"I'll direct you to our documentation for {topic}. "
        f"You'll find step-by-step instructions there — "
        f"it's much clearer in written form than I can explain over voice."
    )
    return HandoffResult(
        type=HandoffType.DOCS,
        destination=url,
        message=message,
    )


def redirectToEmailSupport(reason: str) -> HandoffResult:
    """
    Trigger: problemy z kontem, błędy weryfikacji, kwestie wrażliwe (prywatność, billing).
    Wymaga dostępu do wewnętrznych danych – agent AI nie ma uprawnień.
    """
    support_email = os.getenv("SUPPORT_EMAIL", "support@elevenlabs.io")
    message = (
        f"For {reason}, you'll need to contact our support team directly — "
        f"they have secure access to account data that I don't. "
        f"Please email us at support at elevenlabs dot io "
        f"and include your account email and a description of the issue."
    )
    return HandoffResult(
        type=HandoffType.EMAIL,
        destination=support_email,
        message=message,
    )


def przekierujDoZewnętrznegoURL(destination_key: str) -> HandoffResult:
    """
    Trigger: zapytania o Enterprise Sales, Discord, lub zgłoszenia deweloperskie.
    Budowanie relacji biznesowych i społeczności wymaga specyficznych platform.
    """
    destination_map = {
        "enterprise": URLS["enterprise_sales"],
        "discord": URLS["discord"],
        "pricing": URLS["pricing"],
        "changelog": URLS["changelog"],
        "status": URLS["status"],
    }

    url = destination_map.get(destination_key, URLS["docs_main"])

    messages = {
        "enterprise": (
            "For Enterprise plans, I'll connect you with our sales team. "
            "They'll walk you through custom pricing and dedicated support options."
        ),
        "discord": (
            "Our developer community on Discord is the best place for that conversation. "
            "I'll send you the invite link."
        ),
        "pricing": (
            "Let me direct you to our pricing page where you can compare all plans."
        ),
        "changelog": (
            "You'll find all recent updates and releases on our changelog page."
        ),
        "status": (
            "Check our status page for real-time information on API availability."
        ),
    }

    message = messages.get(
        destination_key,
        "I'll send you a link with the information you need.",
    )

    return HandoffResult(
        type=HandoffType.EXTERNAL_URL,
        destination=url,
        message=message,
    )


TOOL_SCHEMAS = [
    {
        "name": "przekierujDoDokumenty",
        "description": (
            "Redirect the user to written documentation when the question requires "
            "step-by-step instructions or complex technical details that are better "
            "conveyed in text form than over voice."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The technical topic the user is asking about (e.g., 'Twilio integration', 'voice cloning').",
                }
            },
            "required": ["topic"],
        },
    },
    {
        "name": "redirectToEmailSupport",
        "description": (
            "Escalate to human email support when the issue involves account access, "
            "billing, identity verification, privacy, or any matter requiring secure "
            "internal data access."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Brief description of why email support is needed (e.g., 'account verification issue').",
                }
            },
            "required": ["reason"],
        },
    },
    {
        "name": "przekierujDoZewnętrznegoURL",
        "description": (
            "Redirect to an external destination: Enterprise sales, Discord community, "
            "pricing page, changelog, or status page."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "destination_key": {
                    "type": "string",
                    "enum": ["enterprise", "discord", "pricing", "changelog", "status"],
                    "description": "The target destination key.",
                }
            },
            "required": ["destination_key"],
        },
    },
]

TOOL_DISPATCH = {
    "przekierujDoDokumenty": przekierujDoDokumenty,
    "redirectToEmailSupport": redirectToEmailSupport,
    "przekierujDoZewnętrznegoURL": przekierujDoZewnętrznegoURL,
}


def dispatch_tool(tool_name: str, parameters: dict) -> HandoffResult:
    fn = TOOL_DISPATCH.get(tool_name)
    if fn is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    return fn(**parameters)
