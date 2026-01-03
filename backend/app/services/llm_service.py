"""OpenAI LLM service with LangSmith integration"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI

# from langsmith import traceable  # COMMENTED OUT: LangSmith causing 403 errors
from langchain_openai import ChatOpenAI


# No-op decorator to replace @traceable
def traceable(name=None):
    def decorator(func_or_class):
        return func_or_class

    return decorator


from langchain_core.messages import HumanMessage, SystemMessage
import json

openai_client = None
llm = None

def _get_openai_client():
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai_client = OpenAI(api_key=api_key)
    return openai_client

def _get_llm():
    global llm
    if llm is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        llm = ChatOpenAI(
            model_name="gpt-4-turbo-preview",
            temperature=0.7,
            openai_api_key=api_key,
        )
    return llm


@traceable(name="llm_call")
def call_llm(
    messages: List[Dict[str, str]],
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    response_format: Optional[Dict] = None,
) -> str:
    """Call OpenAI API with LangSmith tracing"""
    try:
        client = _get_openai_client()
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=response_format,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"LLM call failed: {str(e)}")


@traceable(name="structured_llm_call")
def call_llm_structured(
    system_prompt: str,
    user_prompt: str,
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
) -> Dict[str, Any]:
    """Call LLM with structured JSON response"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response_format = {"type": "json_object"}

    response = call_llm(
        messages=messages,
        model=model,
        temperature=temperature,
        response_format=response_format,
    )

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON response", "raw": response}


def create_agent_prompt(
    agent_name: str, context: str, task: str
) -> List[Dict[str, str]]:
    """Create formatted prompt for agent"""
    system_prompt = f"""You are a {agent_name} agent in a multi-agent system for predicting Publix grocery store expansion locations.

{context}

Your task: {task}

Provide clear, data-driven analysis and reasoning."""

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]
