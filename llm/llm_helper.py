import os
from langchain_openai import ChatOpenAI


def get_llm(model: str = "gpt-4o-mini") -> ChatOpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment. Check your .env file.")
    
    return ChatOpenAI(model=model, api_key=api_key)