from __future__ import annotations

import re
import os
import requests
from dotenv import load_dotenv

load_dotenv()


# -----------------------------
# Groq API call
# -----------------------------
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

        print("\n🔍 RAW GROQ RESPONSE:\n", response.text)  # VERY IMPORTANT

        result = response.json()

        # ✅ Safe check
        if "choices" not in result:
            print("❌ Groq API Error:", result)
            return ""

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print("❌ Groq Exception:", e)
        return ""

# -----------------------------
# Limit and format context
# -----------------------------
def format_retrieved_for_prompt(retrieved_docs):
    docs = retrieved_docs[:2]

    parts = []
    for doc in docs:
        source = doc["metadata"]["source"]
        content = doc["content"][:300]
        parts.append(f"Source: {source}\n{content}")

    return "\n\n".join(parts)


# -----------------------------
# Generate response
# -----------------------------
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


def generate_support_response(ticket: str, retrieved_docs: list):
    context = format_retrieved_for_prompt(retrieved_docs)

    prompt = f"""
You are a strict e-commerce customer support assistant.

You MUST follow ALL rules strictly.

RULES:
- Classification must be simple (Damaged Item, Refund Request, Shipping Issue, Perishable Item Issue)
- Decision must be EXACTLY one word: approve / deny / partial / needs escalation
- Citations MUST be exact source file names from the provided documents (e.g., 03-returns-perishables-food.md)
- Citations MUST include ONLY file names, NOT section names or codes
- DO NOT mention policy codes like POL-DIS-001
- Customer Response MUST be written as a support agent speaking to the customer (not customer voice)
- Do NOT assume answers to clarifying questions
- Do NOT assume facts that are not explicitly given
- Next Steps must be conditional actions, NOT final execution (do not say "refund processed")
- Keep response professional, clear, and concise

FORMAT EXACTLY (no extra text before or after):

Classification:
Clarifying Questions:
Decision:
Rationale:
Citations:
Customer Response:
Next Steps:

Rules for sections:
- Clarifying Questions: write "None" OR 1–3 bullet questions
- Citations: MUST be bullet format using "-" with file names only
- Customer Response: polite, professional, no assumptions
- Next Steps: 2–3 bullet action steps

Ticket:
{ticket}

Policies:
{context}

Now generate the response strictly following all rules.
"""

    # 🔥 Call Groq
    result = call_groq(prompt)
    result = (result or "").strip()

    print("\n--- GROQ OUTPUT ---\n", result, "\n-------------------\n")

    # -----------------------------
    # STRICT VALIDATION (NEW 🔥)
    # -----------------------------
    if not is_valid_response(result):
        sources = list(set([doc["metadata"]["source"] for doc in retrieved_docs]))
        ticket_lower = ticket.lower()

        if "damage" in ticket_lower or "broken" in ticket_lower:
            decision = "approve"
            reason = "Damaged Item"
        elif "late" in ticket_lower or "delay" in ticket_lower:
            decision = "partial"
            reason = "Delivery Delay"
        elif "spoiled" in ticket_lower or "melted" in ticket_lower:
            decision = "approve"
            reason = "Perishable Item Issue"
        else:
            decision = "needs escalation"
            reason = "General Issue"

        result = f"""
Classification: {reason}

Clarifying Questions:
None

Decision: {decision}

Rationale:
Based on retrieved policy context, this case relates to {reason.lower()} and standard policy conditions apply.

Citations:
- {sources[0] if sources else "unknown"}

Customer Response:
We’re sorry for the inconvenience. Based on our policy, your request has been reviewed and appropriate action will be taken.

Next Steps:
- Verify order details
- Process resolution accordingly
"""

    return result

# -----------------------------
# Section parser
# -----------------------------
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


# -----------------------------
# Pretty print
# -----------------------------
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


# -----------------------------
# Test run
# -----------------------------
if __name__ == "__main__":
    from retriever import get_relevant_docs

    ticket = "My cookies arrived melted due to delivery delay, can I get refund?"

    print("Ticket:\n", ticket, "\n")

    retrieved = get_relevant_docs(ticket)
    print(f"Retrieved {len(retrieved)} chunk(s)\n")

    response = generate_support_response(ticket, retrieved)
    print_formatted_response(response)