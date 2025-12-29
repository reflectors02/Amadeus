from langchain_openai import ChatOpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_llm = None

def reset_llm():
    """
    Force recreation of the ChatOpenAI client (e.g. when model or API key changes).
    """
    global _llm
    _llm = None

def get_llm(api_key: str, model: str) -> ChatOpenAI:
    """
    Returns a cached ChatOpenAI instance configured for OpenRouter.
    """
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            timeout=60,
            default_headers={
                "X-Title": "Amadeus",
            },
        )
    return _llm
