"""
Planning commission scraper for monitoring meeting agendas and identifying Publix-like projects
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class PlanningCommissionScraper:
    """Scraper for planning commission meeting records"""

    def __init__(self):
        try:
            from app.services.llm_service import call_llm

            self.call_llm = call_llm
        except ImportError:
            logger.warning("LLM service not available")
            self.call_llm = None

    def scrape_meeting_agendas(
        self, city: str, state: str, months_back: int = 6
    ) -> List[Dict]:
        """
        Scrape planning commission meeting agendas

        Args:
            city: City name
            state: State abbreviation
            months_back: How many months back to search

        Returns:
            List of meeting agenda records
        """
        logger.info(f"Scraping planning commission agendas for {city}, {state}")

        # Find planning commission website
        base_url = self._find_planning_commission_url(city, state)
        if not base_url:
            logger.warning(
                f"Could not find planning commission URL for {city}, {state}"
            )
            return []

        # Get meeting agendas
        agendas = self._get_meeting_agendas(base_url, months_back)
        if not agendas:
            return []

        # Extract project information from agendas
        records = []
        for agenda in agendas:
            projects = self._extract_projects_from_agenda(agenda, city, state)
            records.extend(projects)

        return records

    def _find_planning_commission_url(self, city: str, state: str) -> Optional[str]:
        """Find planning commission website URL"""
        patterns = [
            f"https://www.{city.lower().replace(' ', '')}.gov/planning",
            f"https://www.{city.lower().replace(' ', '')}.gov/planning-commission",
            f"https://www.{city.lower().replace(' ', '')}.gov/planning-board",
            f"https://www.{city.lower().replace(' ', '')}.gov/development/planning",
        ]

        for url in patterns:
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code == 200:
                    return url
            except:
                continue

        return None

    def _get_meeting_agendas(self, base_url: str, months_back: int) -> List[Dict]:
        """Get meeting agenda URLs"""
        try:
            response = requests.get(base_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Look for agenda links (common patterns)
            agenda_links = []
            for link in soup.find_all("a", href=True):
                href = link.get("href", "")
                text = link.get_text().lower()

                if any(
                    keyword in text or keyword in href.lower()
                    for keyword in ["agenda", "meeting", "planning commission"]
                ):
                    full_url = requests.compat.urljoin(base_url, href)
                    agenda_links.append({"url": full_url, "title": link.get_text()})

            return agenda_links[:20]  # Limit to 20 most recent

        except Exception as e:
            logger.error(f"Failed to get meeting agendas: {e}")
            return []

    def _extract_projects_from_agenda(
        self, agenda: Dict, city: str, state: str
    ) -> List[Dict]:
        """Extract project information from agenda"""
        url = agenda.get("url")
        if not url:
            return []

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            text_content = soup.get_text()

            # Extract meeting date
            meeting_date = self._extract_meeting_date(text_content)

            # Look for Publix-like projects using keywords
            projects = self._find_publix_like_projects(
                text_content, city, state, meeting_date, url
            )

            return projects

        except Exception as e:
            logger.error(f"Failed to extract projects from agenda: {e}")
            return []

    def _extract_meeting_date(self, text: str) -> Optional[datetime]:
        """Extract meeting date from text"""
        # Common date patterns
        date_patterns = [
            r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}",
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    # Parse date (simplified - would need better parsing)
                    return datetime.now()  # Placeholder
                except:
                    pass

        return None

    def _find_publix_like_projects(
        self,
        text: str,
        city: str,
        state: str,
        meeting_date: Optional[datetime],
        source_url: str,
    ) -> List[Dict]:
        """Find projects matching Publix characteristics"""
        # Keywords that indicate grocery/retail development
        keywords = [
            "grocery",
            "supermarket",
            "100,000",
            "100000",
            "sq ft",
            "square feet",
            "commercial",
            "retail",
            "rezoning",
            "commercial development",
        ]

        # Check if text contains relevant keywords
        text_lower = text.lower()
        matches = [kw for kw in keywords if kw.lower() in text_lower]

        if not matches:
            return []

        # Use LLM to extract structured project data
        if self.call_llm:
            projects = self._extract_projects_with_llm(
                text, city, state, meeting_date, source_url
            )
            return projects

        # Fallback: return basic record
        return [
            {
                "city": city,
                "state": state,
                "meeting_date": meeting_date,
                "project_description": text[:500],  # First 500 chars
                "source_url": source_url,
                "project_type": "potential_grocery",
            }
        ]

    def _extract_projects_with_llm(
        self,
        text: str,
        city: str,
        state: str,
        meeting_date: Optional[datetime],
        source_url: str,
    ) -> List[Dict]:
        """Use LLM to extract structured project information"""
        if not self.call_llm:
            return []

        prompt = f"""Extract project information from the following planning commission agenda text for {city}, {state}.

Look for projects that might be grocery stores or retail developments, especially:
- Projects mentioning "grocery", "supermarket", "100,000 sq ft" or similar
- Commercial rezoning applications
- Large retail developments

For each project found, extract:
- agenda_item: Agenda item number/identifier
- project_description: Description of the project
- parcel_address: Address or location mentioned
- application_status: pending, approved, denied
- project_type: grocery, commercial, rezoning, etc.
- square_feet: Square footage if mentioned

Return as JSON array.

Text:
{text[:10000]}  # Limit to 10000 chars
"""

        try:
            response = self.call_llm(prompt)
            # Parse LLM response and return structured projects
            # For now, return basic structure
            return [
                {
                    "city": city,
                    "state": state,
                    "meeting_date": meeting_date,
                    "agenda_item": None,
                    "project_description": text[:1000],
                    "parcel_address": None,
                    "application_status": "pending",
                    "project_type": "potential_grocery",
                    "square_feet": None,
                    "source_url": source_url,
                }
            ]
        except Exception as e:
            logger.error(f"LLM project extraction failed: {e}")
            return []
