"""
CLI entry point for the e-commerce support pipeline (triage → RAG → resolution).

Run from project root:
    python src/main.py
"""

from __future__ import annotations

from agents import run_agents

EXAMPLE_TICKET = "My order arrived damaged, can I get refund?"


def main() -> None:
    print("E-commerce support assistant")
    print("-" * 48)
    print(f"Example ticket: {EXAMPLE_TICKET}")
    print()

    raw = input("Enter customer ticket (Enter = use example): ").strip()
    ticket = raw if raw else EXAMPLE_TICKET
    if not raw:
        print("(Using example ticket.)\n")

    response = run_agents(ticket)

    width = 64
    print("=" * width)
    print("RESOLUTION")
    print("=" * width)
    print(response.rstrip())
    print("=" * width)


if __name__ == "__main__":
    main()
