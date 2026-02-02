import os
from dotenv import load_dotenv
from langchain_cerebras import ChatCerebras

load_dotenv()

_llm_instance = None


def get_shared_llm() -> ChatCerebras:
    global _llm_instance
    
    if _llm_instance is None:
        api_key = os.getenv('CEREBRAS_API_KEY')
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY not set in environment")
        
        _llm_instance = ChatCerebras(
            api_key=api_key,
            model=os.getenv('CEREBRAS_MODEL', 'llama-3.3-70b'),
            temperature=float(os.getenv('LLM_TEMPERATURE', '0.7')),
            max_tokens=int(os.getenv('LLM_MAX_TOKENS', '8192')),
        )
    
    return _llm_instance
