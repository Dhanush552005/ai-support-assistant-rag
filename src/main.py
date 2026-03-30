
from __future__ import annotations

from agents import run_agents

EXAMPLE_TICKET = "My order arrived damaged, can I get refund?"


def get_default_order_context() -> dict:
    return {
        "order_date": "2026-03-20",
        "delivery_date": "2026-03-25",
        "item_category": "perishable",
        "fulfillment_type": "first-party",
        "shipping_region": "India",
        "order_status": "delivered",
        "payment_method": "prepaid"
    }


def main() -> None:
    print("E-commerce support assistant")
    print("-" * 48)
    print(f"Example ticket: {EXAMPLE_TICKET}")
    print()

    raw = input("Enter customer ticket (Enter = use example): ").strip()
    ticket = raw if raw else EXAMPLE_TICKET
    if not raw:
        print("(Using example ticket.)\n")

    
    order_context = get_default_order_context()

    print("Order Context:")
    for k, v in order_context.items():
        print(f"  {k}: {v}")
    print()


    response = run_agents(ticket, order_context)

    width = 64
    print("=" * width)
    print("RESOLUTION")
    print("=" * width)
    print(response.rstrip())
    print("=" * width)


if __name__ == "__main__":
    main()