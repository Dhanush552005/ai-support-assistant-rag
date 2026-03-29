
from __future__ import annotations

from typing import Any

from generator import generate_support_response
from retriever import get_relevant_docs

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


def resolution_agent(
    ticket: str,
    retrieved_docs: list[dict[str, Any]],
    order_context: dict
) -> str:
    """Draft structured resolution from ticket + retrieved evidence + order context."""
    return generate_support_response(ticket, retrieved_docs, order_context)


def compliance_agent(response: str) -> str | None:
    """
    Check that the resolution includes required section headers.
    Returns a warning string if something is missing, else None.
    """
    if not response:
        return "Warning: empty response from model"

    lower = response.lower()
    missing: list[str] = []

    if "decision:" not in lower:
        missing.append("Decision")
    if "citations:" not in lower:
        missing.append("Citations")

    if missing:
        return f"Warning: response missing required sections: {', '.join(missing)}"

    return None


def run_agents(ticket: str, order_context: dict) -> str:
    """
    Run triage → retrieval → resolution → compliance.
    Returns the final response text (compliance warning appended if needed).
    """
    issue_type = triage_agent(ticket)

    retrieved = retriever_agent(ticket)

    resolution = resolution_agent(ticket, retrieved, order_context)

    warning = compliance_agent(resolution)

    if warning:
        return f"{resolution.rstrip()}\n\n---\n{warning}\n"

    return resolution


def main() -> None:
    sample = "My cookies arrived melted and the box was crushed. I want a refund."

    order_context = {
        "order_date": "2026-03-20",
        "delivery_date": "2026-03-25",
        "item_category": "perishable",
        "fulfillment_type": "first-party",
        "shipping_region": "India",
        "order_status": "delivered",
        "payment_method": "prepaid"
    }

    print("Ticket:", sample, "\n")

    out = run_agents(sample, order_context)

    print(out)


if __name__ == "__main__":
    main()