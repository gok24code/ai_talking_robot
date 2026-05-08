from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, SYSTEM_PROMPT

_client = Groq(api_key=GROQ_API_KEY)


def get_response(conversation_history: list) -> str:
    """Konuşma geçmişine göre LLM yanıtı üretir."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        max_tokens=512,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
