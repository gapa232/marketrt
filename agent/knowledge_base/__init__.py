from .docs import PRODUCT_DOCS
from .faq import FAQ
from .urls import URLS, DOC_TOPIC_MAP, resolve_doc_url

FULL_KNOWLEDGE_BASE = f"{PRODUCT_DOCS}\n\n{FAQ}"

__all__ = [
    "PRODUCT_DOCS",
    "FAQ",
    "URLS",
    "DOC_TOPIC_MAP",
    "FULL_KNOWLEDGE_BASE",
    "resolve_doc_url",
]
