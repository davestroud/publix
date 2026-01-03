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


from langchain.schema import HumanMessage, SystemMessage
import json

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize LangChain LLM with LangSmith
llm = ChatOpenAI(
    model_name="gpt-4-turbo-preview",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)


@traceable(name="llm_call")
def call_llm(
    messages: List[Dict[str, str]],
    model: str = "gpt-4-turbo-preview",
    temperature: float = 0.7,
    response_format: Optional[Dict] = None,
) -> str:
    """Call OpenAI API with LangSmith tracing"""
    try:
        response = openai_client.chat.completions.create(
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
