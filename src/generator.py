from __future__ import annotations

import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def call_groq(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": "You are a strict e-commerce policy assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        print("\n🔍 RAW GROQ RESPONSE:\n", response.text)

        result = response.json()

        if "choices" not in result:
            print("❌ Groq API Error:", result)
            return ""

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ Groq Exception:", e)
        return ""

def format_retrieved_for_prompt(retrieved_docs):
    docs = retrieved_docs[:2]

    parts = []
    for doc in docs:
        source = doc["metadata"]["source"]
        content = doc["content"][:300]
        parts.append(f"Source: {source}\n{content}")

    return "\n\n".join(parts)

def is_valid_response(text: str) -> bool:
    required_sections = [
        "Classification:",
        "Clarifying Questions:",
        "Decision:",
        "Rationale:",
        "Citations:",
        "Customer Response:",
        "Next Steps:"
    ]
    return all(section in text for section in required_sections)

def estimate_confidence(ticket: str) -> float:
    t = ticket.lower()

    if any(k in t for k in ["damaged", "broken", "spoiled", "melted"]):
        return 0.92
    elif any(k in t for k in ["late", "delay"]):
        return 0.85
    elif any(k in t for k in ["refund", "return"]):
        return 0.88
    else:
        return 0.75

def generate_support_response(ticket: str, retrieved_docs: list, order_context: dict):
    context = format_retrieved_for_prompt(retrieved_docs)
    confidence = estimate_confidence(ticket)

    prompt = f"""
You are a strict e-commerce customer support assistant.

You MUST follow ALL rules strictly.

RULES:
- Classification must be simple (Damaged Item, Refund Request, Shipping Issue, Perishable Item Issue)
- Decision must be EXACTLY one word: approve / deny / partial / needs escalation
- Citations MUST be exact source file names only
- DO NOT mention policy codes
- Customer Response must be written as support agent speaking to customer
- Do NOT assume missing facts
- Next Steps must be conditional actions

FORMAT EXACTLY:

Classification:
Clarifying Questions:
Decision:
Rationale:
Citations:
Customer Response:
Next Steps:

Ticket:
{ticket}

Order Context:
{order_context}

Policies:
{context}
"""

    result = call_groq(prompt)
    result = (result or "").strip()

    print("\n--- GROQ OUTPUT ---\n", result, "\n-------------------\n")

    if not is_valid_response(result):
        sources = list(set([doc["metadata"]["source"] for doc in retrieved_docs]))

        result = f"""
Classification: General Issue (confidence: {confidence})

Clarifying Questions:
None

Decision: needs escalation

Rationale:
Model could not confidently generate a structured response based on policy.

Citations:
- {sources[0] if sources else "unknown"}

Customer Response:
We’re sorry for the inconvenience. Your request is being reviewed by our support team.

Next Steps:
- Escalate to human agent
- Verify order details
"""

    else:
        result = re.sub(
            r"Classification:\s*(.*)",
            f"Classification: \\1 (confidence: {confidence})",
            result
        )

    return result


def _split_sections(text: str) -> dict[str, str]:
    pattern = r"(?m)^(Classification|Clarifying Questions|Decision|Rationale|Citations|Customer Response|Next Steps):"
    matches = list(re.finditer(pattern, text))

    sections = {}
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        key = match.group(1)
        sections[key] = text[start:end].strip()

    return sections


def print_formatted_response(text: str):
    sections = _split_sections(text)

    print("\n" + "=" * 70)
    print("POLICY-GROUNDED RESPONSE")
    print("=" * 70)

    for key in [
        "Classification",
        "Clarifying Questions",
        "Decision",
        "Rationale",
        "Citations",
        "Customer Response",
        "Next Steps"
    ]:
        if key in sections:
            print(f"\n{key}:")
            print("-" * 50)
            print(sections[key])

    print("\n" + "=" * 70)

if __name__ == "__main__":
    from retriever import get_relevant_docs

    ticket = "My cookies arrived melted due to delivery delay, can I get refund?"

    order_context = {
        "order_date": "2026-03-20",
        "delivery_date": "2026-03-25",
        "item_category": "perishable",
        "fulfillment_type": "first-party",
        "shipping_region": "India",
        "order_status": "delivered"
    }

    retrieved = get_relevant_docs(ticket)

    response = generate_support_response(ticket, retrieved, order_context)
    print_formatted_response(response)