import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Type, List, Optional
from langchain_core.tools import BaseTool
from langchain_core.messages import AIMessage

from dexter.prompts import DEFAULT_SYSTEM_PROMPT

# Global LLM instance (lazy initialization)
_llm = None
_current_model = None

# Available models
AVAILABLE_MODELS = [
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-4.1",
    "gpt-4.1-mini"
]

def reset_llm():
    """Reset the LLM instance to force re-initialization with new API key or model."""
    global _llm, _current_model
    _llm = None
    _current_model = None

def get_llm(model_name=None):
    """Get or create the LLM instance with lazy initialization."""
    global _llm, _current_model

    # Use environment variable or default if no model specified
    if model_name is None:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    # Reset LLM if model changed
    if _current_model != model_name:
        _llm = None
        _current_model = model_name

    if _llm is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before using the agent.")
        _llm = ChatOpenAI(model=model_name, temperature=0, api_key=api_key)
        _current_model = model_name
    return _llm

def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    tools: Optional[List[BaseTool]] = None,
    model_name: Optional[str] = None,
) -> AIMessage:
    final_system_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT

    # Get LLM instance with optional model name
    llm = get_llm(model_name)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", final_system_prompt),
        ("user", "{prompt}")
    ])

    runnable = llm
    if output_schema:
        runnable = llm.with_structured_output(output_schema)
    elif tools:
        runnable = llm.bind_tools(tools)

    chain = prompt_template | runnable
    return chain.invoke({"prompt": prompt})
