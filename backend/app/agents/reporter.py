"""Reporter Agent - Generates insights and reports"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.services.llm_service import call_llm, call_llm_structured, create_agent_prompt
from app.models.schemas import Prediction, AnalysisRun, PublixStore

# from langsmith import traceable  # COMMENTED OUT: LangSmith causing 403 errors
import logging

logger = logging.getLogger(__name__)


# No-op decorator to replace @traceable
def traceable(name=None):
    def decorator(func_or_class):
        return func_or_class

    return decorator


@traceable(name="reporter_agent")
class ReporterAgent:
    """Agent responsible for generating insights and reports"""

    def __init__(self, db: Session):
        self.db = db

    def generate_prediction_report(
        self, predictions: List[Dict[str, Any]], analysis_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive prediction report"""
        logger.info(f"Generating prediction report for {len(predictions)} predictions")

        context = """You are generating a comprehensive report on Publix expansion predictions.
        Synthesize findings from data analysis, site evaluations, and market research into
        actionable insights for real estate developers."""

        task = f"""Generate a comprehensive expansion prediction report.

Analysis Context:
{analysis_context}

Predictions Summary:
- Total predictions: {len(predictions)}
- Top predictions: {predictions[:5] if predictions else 'None'}

Create a report with:
1. Executive Summary
2. Key Findings
3. Top Expansion Opportunities (ranked)
4. Market Insights
5. Risk Factors
6. Recommendations"""

        prompt = create_agent_prompt(agent_name="Reporter", context=context, task=task)

        report = call_llm(prompt)

        return {
            "report": report,
            "prediction_count": len(predictions),
            "analysis_context": analysis_context,
        }

    def generate_city_insights(
        self, city: str, state: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights for a specific city"""
        logger.info(f"Generating insights for {city}, {state}")

        context = """You are analyzing a city for Publix expansion opportunity.
        Provide clear, data-driven insights that help identify why this city
        is or isn't a good fit for Publix expansion."""

        task = f"""Generate insights for {city}, {state}:

Data:
{data}

Provide:
1. Market Opportunity Score
2. Key Strengths
3. Key Challenges
4. Competitive Landscape
5. Demographic Fit
6. Expansion Recommendation"""

        insights = call_llm_structured(system_prompt=context, user_prompt=task)

        return {"city": city, "state": state, "insights": insights}

    def create_prediction_summary(self, predictions: List[Prediction]) -> str:
        """Create a summary of predictions"""
        logger.info(f"Creating prediction summary for {len(predictions)} predictions")

        if not predictions:
            return "No predictions available."

        # Group by state
        by_state = {}
        for pred in predictions:
            state = pred.state
            if state not in by_state:
                by_state[state] = []
            by_state[state].append(
                {
                    "city": pred.city,
                    "confidence": pred.confidence_score,
                    "reasoning": pred.reasoning[:200] if pred.reasoning else "",
                }
            )

        context = """You are summarizing Publix expansion predictions.
        Create a concise, actionable summary highlighting top opportunities."""

        task = f"""Summarize these Publix expansion predictions:

Predictions by state:
{by_state}

Create a concise summary highlighting:
- Top expansion markets
- Key patterns
- Highest confidence opportunities"""

        summary = call_llm(
            create_agent_prompt(agent_name="Reporter", context=context, task=task)
        )

        return summary

    def format_prediction_for_api(self, prediction: Prediction) -> Dict[str, Any]:
        """Format prediction for API response"""
        return {
            "id": prediction.id,
            "city": prediction.city,
            "state": prediction.state,
            "latitude": prediction.latitude,
            "longitude": prediction.longitude,
            "confidence_score": prediction.confidence_score,
            "reasoning": prediction.reasoning,
            "predicted_store_size": prediction.predicted_store_size,
            "key_factors": prediction.key_factors,
            "created_at": (
                prediction.created_at.isoformat() if prediction.created_at else None
            ),
        }

    def generate_dashboard_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for dashboard"""
        logger.info("Generating dashboard summary")

        total_stores = self.db.query(PublixStore).count()
        total_predictions = self.db.query(Prediction).count()

        # Get recent predictions
        recent_predictions = (
            self.db.query(Prediction)
            .order_by(Prediction.created_at.desc())
            .limit(10)
            .all()
        )

        # Calculate average confidence
        avg_confidence = (
            self.db.query(func.avg(Prediction.confidence_score)).scalar() or 0.0
        )

        return {
            "total_stores": total_stores,
            "total_predictions": total_predictions,
            "average_confidence": round(float(avg_confidence), 2),
            "recent_predictions": [
                self.format_prediction_for_api(p) for p in recent_predictions
            ],
        }
