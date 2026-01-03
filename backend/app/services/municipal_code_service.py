"""
Municipal code service for extracting zoning regulations, setbacks, and parking requirements

Uses LLM to extract structured data from municipal code PDFs and websites
"""

import os
import logging
import requests
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import pdfplumber  # Would need: poetry add pdfplumber

logger = logging.getLogger(__name__)


class MunicipalCodeService:
    """Service for extracting municipal zoning code data"""

    def __init__(self):
        try:
            from app.services.llm_service import call_llm

            self.call_llm = call_llm
        except ImportError:
            logger.warning("LLM service not available")
            self.call_llm = None

    def extract_zoning_code(
        self, city: str, state: str, source_url: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Extract zoning code data for a city

        Args:
            city: City name
            state: State abbreviation
            source_url: URL to municipal code (optional)

        Returns:
            Dictionary with zoning code data
        """
        logger.info(f"Extracting zoning code for {city}, {state}")

        # Try to find source URL if not provided
        if not source_url:
            source_url = self._find_municipal_code_url(city, state)

        if not source_url:
            logger.warning(f"Could not find municipal code URL for {city}, {state}")
            return None

        # Extract text from source
        text_content = self._extract_text_from_url(source_url)
        if not text_content:
            return None

        # Use LLM to extract structured data
        if self.call_llm:
            structured_data = self._extract_with_llm(text_content, city, state)
            if structured_data:
                structured_data["source_url"] = source_url
                structured_data["raw_text"] = text_content[
                    :5000
                ]  # Store first 5000 chars
                return structured_data

        return None

    def _find_municipal_code_url(self, city: str, state: str) -> Optional[str]:
        """
        Try to find municipal code URL for a city

        Common patterns:
        - {city}.gov/zoning
        - municode.com/library/{state}/{city}
        - ecode360.com/{city_code}
        """
        # Common URL patterns
        patterns = [
            f"https://www.{city.lower().replace(' ', '')}.gov/zoning",
            f"https://www.{city.lower().replace(' ', '')}.gov/planning/zoning",
            f"https://library.municode.com/{state.lower()}/{city.lower().replace(' ', '_')}",
        ]

        for url in patterns:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return url
            except:
                continue

        return None

    def _extract_text_from_url(self, url: str) -> Optional[str]:
        """Extract text content from URL (handles PDFs and HTML)"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").lower()

            if "pdf" in content_type:
                return self._extract_text_from_pdf(response.content)
            else:
                # HTML
                soup = BeautifulSoup(response.text, "html.parser")
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                return soup.get_text()

        except Exception as e:
            logger.error(f"Failed to extract text from {url}: {e}")
            return None

    def _extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """Extract text from PDF content"""
        try:
            import pdfplumber
            import io

            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages[:10]:  # First 10 pages
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            logger.warning(
                "pdfplumber not installed. Install with: poetry add pdfplumber"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            return None

    def _extract_with_llm(self, text: str, city: str, state: str) -> Optional[Dict]:
        """Use LLM to extract structured zoning data from text"""
        if not self.call_llm:
            return None

        prompt = f"""Extract zoning code information from the following municipal code text for {city}, {state}.

Extract the following information:
1. Zoning district codes and names (e.g., "C-2 Commercial", "M-1 Industrial")
2. Permitted uses for commercial/retail zones
3. Setback requirements (front, side, rear) in feet
4. Parking requirements (spaces per 1000 sq ft)
5. Maximum building coverage percentage
6. Maximum height restrictions in feet

For each zoning district found, provide:
- zone_code: The code (e.g., "C-2")
- zone_name: Full name
- permitted_uses: List of allowed uses
- setback_front: Front setback in feet
- setback_side: Side setback in feet
- setback_rear: Rear setback in feet
- parking_spaces_per_1000sqft: Parking requirement
- max_coverage: Maximum coverage percentage
- max_height: Maximum height in feet

Return as JSON format with a "zoning_districts" array.

Text to analyze:
{text[:8000]}  # Limit to 8000 chars for LLM
"""

        try:
            response = self.call_llm(prompt)
            # Parse LLM response (would need JSON parsing)
            # For now, return structured format
            return {
                "city": city,
                "state": state,
                "zoning_districts": [],  # Would be populated from LLM response
            }
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return None

    def extract_impact_fees(
        self, city: str, state: str, source_url: Optional[str] = None
    ) -> List[Dict]:
        """
        Extract impact fee schedules

        Args:
            city: City name
            state: State abbreviation
            source_url: URL to fee schedule (optional)

        Returns:
            List of impact fee dictionaries
        """
        logger.info(f"Extracting impact fees for {city}, {state}")

        if not source_url:
            source_url = self._find_impact_fee_url(city, state)

        if not source_url:
            return []

        text_content = self._extract_text_from_url(source_url)
        if not text_content:
            return []

        # Use LLM to extract fee data
        if self.call_llm:
            fees = self._extract_fees_with_llm(text_content, city, state)
            return fees

        return []

    def _find_impact_fee_url(self, city: str, state: str) -> Optional[str]:
        """Try to find impact fee schedule URL"""
        patterns = [
            f"https://www.{city.lower().replace(' ', '')}.gov/impact-fees",
            f"https://www.{city.lower().replace(' ', '')}.gov/fees",
            f"https://www.{city.lower().replace(' ', '')}.gov/development-fees",
        ]

        for url in patterns:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return url
            except:
                continue

        return None

    def _extract_fees_with_llm(self, text: str, city: str, state: str) -> List[Dict]:
        """Use LLM to extract impact fee data"""
        if not self.call_llm:
            return []

        prompt = f"""Extract impact fee information from the following text for {city}, {state}.

Extract:
1. Utility connection fees (by use type)
2. Traffic impact fees (per square foot)
3. School impact fees
4. Other development fees

For each fee type, provide:
- fee_type: Type of fee (utility, traffic, school, etc.)
- use_type: Use category (commercial, retail, grocery, etc.)
- fee_per_sqft: Fee amount per square foot
- fee_methodology: How the fee is calculated

Return as JSON array.

Text:
{text[:8000]}
"""

        try:
            response = self.call_llm(prompt)
            # Parse and return fees
            return []
        except Exception as e:
            logger.error(f"LLM fee extraction failed: {e}")
            return []
