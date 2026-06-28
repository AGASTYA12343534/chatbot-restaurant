"""
Module: generatePrompt.py
Provides a helper to construct an LLM prompt by combining the user query
and enriched document data, with a general fallback for non-restaurant queries.
"""

def generatePrompt(message: str, docs: list) -> str:
    """
    Build a prompt that:
      - If restaurant/menu docs are provided, includes them for restaurant recommendations.
      - Otherwise, handles general queries with a friendly restaurant-assistant tone.

    Args:
        message: The original user query.
        docs: A list of dictionaries from the vector store (may be empty).
    Returns:
        A formatted prompt string ready to send to the LLM.
    """
    # Restaurant recommendation flow
    if docs and any(doc.get('vector_type') in ('resturant', 'menu') for doc in docs):
        prompt_lines = [
            "You are a confident restaurant recommendation assistant.",
            "Always provide a clear, direct answer to the user's question.",
            "Never say you cannot answer; instead, supply specific details or reasonable fabrications.",
            "",
            f"User Query: {message}",
            ""
        ]

        for idx, doc in enumerate(docs, 1):
            header = f"--- Document {idx} ({doc.get('vector_type', 'unknown')}) ---"
            prompt_lines.append(header)
            for key in sorted(doc.keys()):
                if key in ('_score', 'vector_type'):
                    continue
                prompt_lines.append(f"{key}: {doc[key]}")
            prompt_lines.append(f"Relevance Score: {doc.get('_score')}")
            prompt_lines.append("")

        prompt_lines.extend([
            "Using the above information, give a concise, direct recommendation.",
            "If details are missing, invent plausible specifics to satisfy the user's request without stating uncertainty.",
            "Do not include any caveats or disclaimers of ignorance."
        ])

        return "\n".join(prompt_lines)

    # General fallback flow for non-restaurant queries
    general_lines = [
        "You are a friendly yet professional restaurant recommendation assistant.",
        "Your job is to respond to greetings and general queries in a clear, helpful, and engaging way.",
        "Include 1-3 well-placed emojis (like 🍽️, 😄, 🍴, 🍲, or 🤖) to make your responses feel warm and human.",
        "",
        "Follow these rules:",
        "",
        "- If the user sends a greeting like 'hi', 'hello', or 'hey', respond with a warm welcome and a brief intro of what you do as a restaurant assistant. Use one or two emojis to add friendliness.",
        "",
        "- If the user asks 'who are you', 'what can you do', or 'tell me about yourself', reply with an engaging introduction that describes your role as a restaurant recommendation assistant, your capabilities (e.g., suggesting cuisines, locations, menu highlights), and how you can help users discover great dining experiences. Add a friendly emoji or two.",
        "",
        "- Keep responses concise and conversational. Match a premium yet approachable tone—informative but not stiff. Don't overuse emojis, but feel free to add a touch where it fits.",
        "",
        "- Do not answer personal or off-topic questions. Stick to restaurant-related assistance.",
        "",
        "Use chat history for context when needed, and always aim to make users feel welcomed and informed.",
        "",
        f"User Query: {message}",
    ]

    return "\n".join(general_lines)
