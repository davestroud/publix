"""Orchestrator - Coordinates multi-agent workflow"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.agents.data_collector import DataCollectorAgent
from app.agents.analyst import AnalystAgent
from app.agents.site_evaluator import SiteEvaluatorAgent
from app.agents.reporter import ReporterAgent
from app.models.schemas import AnalysisRun, Prediction

# from langsmith import traceable  # COMMENTED OUT: LangSmith causing 403 errors


# No-op decorator to replace @traceable
def traceable(name=None):
    def decorator(func_or_class):
        return func_or_class

    return decorator


import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@traceable(name="orchestrator")
class Orchestrator:
    """Orchestrates multi-agent workflow for Publix expansion analysis"""

    def __init__(self, db: Session):
        self.db = db
        self.data_collector = DataCollectorAgent(db)
        self.analyst = AnalystAgent(db)
        self.site_evaluator = SiteEvaluatorAgent(db)
        self.reporter = ReporterAgent(db)

    def run_analysis(
        self, region: str, cities: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Run complete analysis workflow"""
        logger.info(f"Starting analysis workflow for region: {region}")

        # Create analysis run record
        analysis_run = AnalysisRun(
            region=region, status="running", started_at=datetime.utcnow()
        )
        self.db.add(analysis_run)
        self.db.commit()

        try:
            # Phase 1: Data Collection
            logger.info("Phase 1: Data Collection")
            collection_results = self.data_collector.execute_collection_plan(region)

            # Phase 2: Analysis
            logger.info("Phase 2: Analysis")
            density_analysis = self.analyst.calculate_store_density(state=region)
            expansion_patterns = self.analyst.identify_expansion_patterns(state=region)
            competitor_comparison = self.analyst.compare_competitor_presence(
                state=region
            )
            saturation_analysis = self.analyst.calculate_market_saturation(state=region)

            # Phase 3: Site Evaluation
            logger.info("Phase 3: Site Evaluation")
            if cities:
                city_evaluations = []
                for city_info in cities:
                    evaluation = self.site_evaluator.evaluate_city(
                        city=city_info["city"], state=city_info["state"]
                    )
                    city_evaluations.append(evaluation)
            else:
                city_evaluations = []

            # Phase 4: Generate Predictions
            logger.info("Phase 4: Generating Predictions")
            predictions = self._generate_predictions(
                region=region,
                analysis_data={
                    "density": density_analysis,
                    "patterns": expansion_patterns,
                    "competitors": competitor_comparison,
                    "saturation": saturation_analysis,
                    "city_evaluations": city_evaluations,
                },
            )

            # Phase 5: Reporting
            logger.info("Phase 5: Reporting")
            report = self.reporter.generate_prediction_report(
                predictions=predictions,
                analysis_context={
                    "region": region,
                    "density_analysis": density_analysis,
                    "expansion_patterns": expansion_patterns,
                    "saturation": saturation_analysis,
                },
            )

            # Update analysis run
            analysis_run.status = "completed"
            analysis_run.completed_at = datetime.utcnow()
            analysis_run.additional_data = {
                "predictions_count": len(predictions),
                "collection_results": {
                    "publix_stores": len(collection_results.get("publix_stores", [])),
                    "competitor_stores": sum(
                        len(v)
                        for v in collection_results.get(
                            "competitor_stores", {}
                        ).values()
                    ),
                },
            }
            self.db.commit()

            return {
                "analysis_run_id": analysis_run.id,
                "status": "completed",
                "predictions": predictions,
                "report": report,
                "analysis_data": {
                    "density": density_analysis,
                    "patterns": expansion_patterns,
                    "saturation": saturation_analysis,
                },
            }

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            analysis_run.status = "failed"
            analysis_run.error_message = str(e)
            analysis_run.completed_at = datetime.utcnow()
            self.db.commit()
            raise

    def _generate_predictions(
        self, region: str, analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate predictions based on analysis data"""
        logger.info("Generating predictions from analysis data")

        # Use Reporter agent to synthesize predictions
        context = """You are generating Publix expansion predictions based on comprehensive analysis.
        Create specific predictions with locations, confidence scores, and reasoning."""

        task = f"""Based on this analysis data for {region}, generate specific Publix expansion predictions:

{analysis_data}

For each prediction, provide:
- City and state
- Latitude/longitude (if available)
- Confidence score (0.0 to 1.0)
- Detailed reasoning
- Key factors supporting the prediction
- Predicted store size (square feet)

Generate 5-10 high-confidence predictions."""

        predictions_data = (
            self.reporter.db.query(Prediction).filter(Prediction.state == region).all()
        )

        # Use LLM to generate new predictions
        from app.services.llm_service import call_llm_structured, create_agent_prompt

        llm_predictions = call_llm_structured(system_prompt=context, user_prompt=task)

        # Store predictions in database
        stored_predictions = []
        if isinstance(llm_predictions, dict) and "predictions" in llm_predictions:
            pred_list = llm_predictions["predictions"]
        elif isinstance(llm_predictions, list):
            pred_list = llm_predictions
        else:
            pred_list = []

        for pred_data in pred_list:
            if isinstance(pred_data, dict):
                prediction = Prediction(
                    city=pred_data.get("city", ""),
                    state=pred_data.get("state", region),
                    latitude=pred_data.get("latitude"),
                    longitude=pred_data.get("longitude"),
                    confidence_score=float(pred_data.get("confidence_score", 0.5)),
                    reasoning=pred_data.get("reasoning", ""),
                    predicted_store_size=pred_data.get("predicted_store_size"),
                    key_factors=pred_data.get("key_factors", []),
                )
                self.db.add(prediction)
                stored_predictions.append(
                    self.reporter.format_prediction_for_api(prediction)
                )

        self.db.commit()
        return stored_predictions

    def analyze_single_city(self, city: str, state: str) -> Dict[str, Any]:
        """Run focused analysis for a single city"""
        logger.info(f"Analyzing single city: {city}, {state}")

        # Collect data for city
        city_data = {"city": city, "state": state}

        # Evaluate city
        city_evaluation = self.site_evaluator.evaluate_city(city, state)

        # Generate insights
        insights = self.reporter.generate_city_insights(
            city=city, state=state, data=city_evaluation
        )

        return {
            "city": city,
            "state": state,
            "evaluation": city_evaluation,
            "insights": insights,
        }
