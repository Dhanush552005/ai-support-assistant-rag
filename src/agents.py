"""
Lightweight “agents” for e-commerce support: triage → retrieve → resolve → compliance.

Run from project root:
    python src/agents.py
"""

from __future__ import annotations

from typing import Any

from generator import generate_support_response
from retriever import get_relevant_docs

# Keyword hints for triage (first match wins; order = specificity).
_TRIAGE_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("fraud", "scam", "stolen card", "unauthorized charge", "identity"), "fraud"),
    (("missing item", "not in the box", "empty package", "short ship", "didn't receive"), "missing_items"),
    (("damaged", "broken", "crushed", "torn", "defective", "wrong item", "not as described"), "damage"),
    (("refund", "return", "money back", "charge back", "chargeback"), "refund"),
    (("cancel", "cancellation", "called off my order"), "cancellation"),
    (("coupon", "promo", "promotion", "discount code", "voucher"), "promo"),
    (("charged twice", "double charge", "billing", "payment failed", "card"), "payment"),
    (("late", "lost package", "tracking", "delivery", "shipment", "carrier", "not arrived"), "shipping"),
)


def triage_agent(ticket: str) -> str:
    """Classify issue type from ticket text (simple keyword triage)."""
    t = ticket.lower()
    for keywords, label in _TRIAGE_RULES:
        if any(k in t for k in keywords):
            return label
    return "other"


def retriever_agent(query: str) -> list[dict[str, Any]]:
    """Retrieve top policy chunks for the ticket/query."""
    return get_relevant_docs(query)


def resolution_agent(ticket: str, retrieved_docs: list[dict[str, Any]]) -> str:
    """Draft structured resolution from ticket + retrieved evidence."""
    return generate_support_response(ticket, retrieved_docs)


def compliance_agent(response: str) -> str | None:
    """
    Check that the resolution includes required section headers.
    Returns a warning string if something is missing, else None.
    """
    lower = response.lower()
    missing: list[str] = []
    if "decision:" not in lower:
        missing.append("Decision")
    if "citations:" not in lower:
        missing.append("Citations")
    if missing:
        return f"Warning: response missing required sections: {', '.join(missing)}"
    return None


def run_agents(ticket: str) -> str:
    """
    Run triage → retrieval → resolution → compliance.
    Returns the final response text (compliance warning appended if needed).
    """
    _ = triage_agent(ticket)
    retrieved = retriever_agent(ticket)
    resolution = resolution_agent(ticket, retrieved)
    warning = compliance_agent(resolution)
    if warning:
        return f"{resolution.rstrip()}\n\n---\n{warning}\n"
    return resolution


def main() -> None:
    sample = "My cookies arrived melted and the box was crushed. I want a refund."
    print("Ticket:", sample, "\n")
    out = run_agents(sample)
    print(out)


if __name__ == "__main__":
    main()
