
from langchain_groq import ChatGroq

from datapilot.config import get_settings


def get_llm() -> ChatGroq:
    """Create a configured Groq chat model."""
    settings = get_settings()

    # Fail early if the API key is missing.
    if not settings.groq_api_key:
        raise ValueError(
            "Groq API key is missing. Configure "
            "DATAPILOT_GROQ_API_KEY in your .env file."
        )

    return ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key.get_secret_value(),
        temperature=0,
        timeout=30,
        max_retries=2,
    )


def ask_llm(question: str) -> str:
    """Send a question to Groq and return its text response."""
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    llm = get_llm()
    response = llm.invoke(question)

    # Return only the generated text.
    if not isinstance(response.content, str):
     raise TypeError("The model returned an unexpected response.")
    return response.content
