"""
LLM Chat Service for Publix Expansion Predictor

Provides conversational interface to query the database and get insights
about Publix stores, parcels, demographics, and expansion predictions.

Integrated with LangSmith for monitoring and tracing.
"""

import os
import logging
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configure LangSmith - MUST be set before importing LangChain
# These environment variables enable automatic tracing
# COMMENTED OUT: LangSmith causing 403 errors, disabling for now
# langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
# langsmith_project = os.getenv("LANGSMITH_PROJECT", "publix-expansion-predictor")
#
# if langsmith_api_key:
#     os.environ["LANGCHAIN_TRACING_V2"] = "true"
#     os.environ["LANGCHAIN_API_KEY"] = langsmith_api_key
#     os.environ["LANGCHAIN_PROJECT"] = langsmith_project
#     logger.info(f"LangSmith tracing configured: project={langsmith_project}")
# else:
#     logger.warning("LANGSMITH_API_KEY not set - LangSmith tracing disabled")

langsmith_api_key = None
langsmith_project = None
logger.info("LangSmith tracing disabled (commented out due to 403 errors)")

try:
    from openai import OpenAI

    # from langsmith import traceable  # COMMENTED OUT: LangSmith causing 403 errors

    OPENAI_AVAILABLE = True
    LANGSMITH_AVAILABLE = False  # Disabled
except ImportError:
    OPENAI_AVAILABLE = False
    LANGSMITH_AVAILABLE = False
    logger.warning(
        "OpenAI or LangSmith not available. Install with: poetry add openai langsmith"
    )


# No-op decorator to replace @traceable
def traceable(name=None):
    def decorator(func_or_class):
        return func_or_class

    return decorator


class ChatService:
    """Service for LLM-powered chat about Publix expansion data with LangSmith tracing"""

    def __init__(self, db: Session):
        self.db = db
        self.api_key = os.getenv("OPENAI_API_KEY")
        # LangSmith disabled - not using anymore
        # self.langsmith_project = os.getenv("LANGSMITH_PROJECT", "publix-expansion-predictor")
        # self.langsmith_api_key = os.getenv("LANGSMITH_API_KEY")

        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI not installed")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # Using cost-effective model

        # Disable LangChain tracing completely
        os.environ.pop("LANGCHAIN_TRACING_V2", None)
        os.environ.pop("LANGCHAIN_API_KEY", None)
        os.environ.pop("LANGCHAIN_PROJECT", None)

        logger.info("LangSmith/LangChain tracing disabled - using direct OpenAI client")

    def get_context_summary(self) -> str:
        """Get summary of available data for context"""
        from app.models.schemas import (
            PublixStore,
            CompetitorStore,
            Parcel,
            Demographics,
            Prediction,
        )

        total_stores = self.db.query(PublixStore).count()
        total_competitors = self.db.query(CompetitorStore).count()
        total_parcels = self.db.query(Parcel).count()
        total_demographics = self.db.query(Demographics).count()
        total_predictions = self.db.query(Prediction).count()

        # Get stores by state
        stores_by_state = (
            self.db.query(PublixStore.state, text("COUNT(*)"))
            .group_by(PublixStore.state)
            .all()
        )

        states_summary = ", ".join(
            [f"{state}: {count}" for state, count in stores_by_state[:5]]
        )

        context = f"""You are an AI assistant helping with Publix grocery store expansion analysis.

Available Data:
- {total_stores} Publix stores across multiple states
- {total_competitors} competitor stores (Walmart, Kroger, Chick-fil-A, etc.)
- {total_parcels} commercial parcels (15-25 acres) suitable for development
- {total_demographics} cities with demographic data
- {total_predictions} expansion predictions

Store Distribution: {states_summary}

You can answer questions about:
- Store locations and distribution
- Parcel availability and characteristics
- Demographics and market analysis
- Expansion predictions and opportunities
- Competitor presence and market saturation

Be helpful, accurate, and cite specific numbers when available."""

        return context

    @traceable(name="chat_database_query")
    def query_database(self, query_type: str, params: Dict) -> Optional[List[Dict]]:
        """Query the database based on the query type"""
        from app.models.schemas import (
            PublixStore,
            CompetitorStore,
            Parcel,
            Demographics,
            Prediction,
        )

        try:
            if query_type == "stores":
                q = self.db.query(PublixStore)
                if params.get("state"):
                    q = q.filter(PublixStore.state == params["state"])
                if params.get("city"):
                    q = q.filter(PublixStore.city.ilike(f"%{params['city']}%"))
                return [
                    {"address": s.address, "city": s.city, "state": s.state}
                    for s in q.limit(10).all()
                ]

            elif query_type == "parcels":
                q = self.db.query(Parcel)
                if params.get("state"):
                    q = q.filter(Parcel.state == params["state"])
                if params.get("city"):
                    q = q.filter(Parcel.city.ilike(f"%{params['city']}%"))
                if params.get("min_acreage"):
                    q = q.filter(Parcel.acreage >= params["min_acreage"])
                return [
                    {
                        "address": p.address,
                        "city": p.city,
                        "state": p.state,
                        "acreage": p.acreage,
                        "zoning": p.current_zoning,
                    }
                    for p in q.limit(10).all()
                ]

            elif query_type == "demographics":
                q = self.db.query(Demographics)
                if params.get("state"):
                    q = q.filter(Demographics.state == params["state"])
                if params.get("city"):
                    q = q.filter(Demographics.city.ilike(f"%{params['city']}%"))
                return [
                    {
                        "city": d.city,
                        "state": d.state,
                        "population": d.population,
                        "median_income": d.median_income,
                        "growth_rate": d.growth_rate,
                    }
                    for d in q.limit(10).all()
                ]

            elif query_type == "predictions":
                q = self.db.query(Prediction)
                if params.get("state"):
                    q = q.filter(Prediction.state == params["state"])
                return [
                    {
                        "city": p.city,
                        "state": p.state,
                        "confidence": p.confidence_score,
                        "reasoning": p.reasoning,
                    }
                    for p in q.limit(10).all()
                ]

        except Exception as e:
            logger.error(f"Database query error: {e}", exc_info=True)
            return None

        return None

    @traceable(name="chat_llm_call")
    def chat(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Process a chat message and return AI response
        Traced with LangSmith for monitoring.

        Args:
            user_message: User's question/message
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]

        Returns:
            Dict with "response" and optionally "data" fields
        """
        if conversation_history is None:
            conversation_history = []

        # Get context about available data
        context = self.get_context_summary()

        # Build system message
        system_message = {
            "role": "system",
            "content": context
            + "\n\nWhen users ask about specific data, use the available query functions to fetch real data from the database. Always cite specific numbers and be accurate.",
        }

        # Build messages
        messages = (
            [system_message]
            + conversation_history
            + [{"role": "user", "content": user_message}]
        )

        try:
            # Use direct OpenAI client (LangChain/LangSmith disabled)
            # COMMENTED OUT: LangChain ChatOpenAI automatically traces to LangSmith
            # Using direct OpenAI client to avoid LangSmith 403 errors
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
            )
            assistant_message = response.choices[0].message.content

            return {
                "response": assistant_message,
                "model": self.model,
            }

        except Exception as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "error": True,
            }

    @traceable(name="chat_with_data")
    def chat_with_data(
        self, user_message: str, conversation_history: List[Dict] = None
    ) -> Dict:
        """
        Enhanced chat that can query database and include results in response
        Traced with LangSmith for monitoring.
        """
        # Simple keyword-based query detection
        query_type = None
        params = {}

        user_lower = user_message.lower()

        # Detect query type
        if any(word in user_lower for word in ["store", "publix store", "location"]):
            query_type = "stores"
            # Extract state/city if mentioned
            states = ["FL", "GA", "AL", "SC", "NC", "TN", "VA", "KY"]
            for state in states:
                if state.lower() in user_lower or state in user_message:
                    params["state"] = state
                    break

        elif any(word in user_lower for word in ["parcel", "land", "property", "acre"]):
            query_type = "parcels"
            states = ["FL", "GA", "AL", "SC", "NC", "TN", "VA", "KY"]
            for state in states:
                if state.lower() in user_lower or state in user_message:
                    params["state"] = state
                    break

        elif any(
            word in user_lower
            for word in ["demographic", "population", "income", "growth"]
        ):
            query_type = "demographics"
            states = ["FL", "GA", "AL", "SC", "NC", "TN", "VA", "KY"]
            for state in states:
                if state.lower() in user_lower or state in user_message:
                    params["state"] = state
                    break

        elif any(
            word in user_lower
            for word in ["prediction", "expand", "opportunity", "next"]
        ):
            query_type = "predictions"
            states = ["FL", "GA", "AL", "SC", "NC", "TN", "VA", "KY"]
            for state in states:
                if state.lower() in user_lower or state in user_message:
                    params["state"] = state
                    break

        # Query database if needed
        data = None
        if query_type:
            data = self.query_database(query_type, params)

        # Enhance user message with data if available
        enhanced_message = user_message
        if data:
            enhanced_message += f"\n\nRelevant data: {str(data)[:500]}"

        # Get AI response
        result = self.chat(enhanced_message, conversation_history)

        # Add data to result
        if data:
            result["data"] = data
            result["query_type"] = query_type

        return result
