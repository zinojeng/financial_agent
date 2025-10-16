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

def reset_llm():
    """Reset the LLM instance to force re-initialization with new API key."""
    global _llm
    _llm = None

def get_llm():
    """Get or create the LLM instance with lazy initialization."""
    global _llm
    if _llm is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before using the agent.")
        _llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=api_key)
    return _llm

def call_llm(
    prompt: str,
    system_prompt: Optional[str] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    tools: Optional[List[BaseTool]] = None,
) -> AIMessage:
    final_system_prompt = system_prompt if system_prompt else DEFAULT_SYSTEM_PROMPT

    # Get LLM instance (will be created on first call)
    llm = get_llm()

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
