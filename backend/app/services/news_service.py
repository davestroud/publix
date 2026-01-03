"""
News Monitoring Service - Collects news articles about Publix and competitors
Uses NewsAPI and Google News API
"""

import os
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import re

load_dotenv()
logger = logging.getLogger(__name__)


class NewsService:
    """Service for monitoring news about Publix and competitors"""

    def __init__(self):
        self.newsapi_key = os.getenv("NEWS_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        self.available = bool(self.newsapi_key or self.google_api_key)

        if not self.available:
            logger.warning(
                "NEWS_API_KEY or GOOGLE_PLACES_API_KEY not set. News service unavailable."
            )
        else:
            logger.info("News service initialized")

        self.newsapi_url = "https://newsapi.org/v2/everything"
        self.google_news_url = "https://www.googleapis.com/customsearch/v1"

    def search_publix_news(
        self, city: Optional[str] = None, state: Optional[str] = None, days: int = 30
    ) -> List[Dict]:
        """
        Search for news articles about Publix

        Args:
            city: Optional city name
            state: Optional state abbreviation
            days: Number of days to look back

        Returns:
            List of news article dictionaries
        """
        articles = []

        # Build query
        query = "Publix"
        if city and state:
            query += f" {city} {state}"
        elif state:
            query += f" {state}"

        # Try NewsAPI first
        if self.newsapi_key:
            articles.extend(self._search_newsapi(query, days))

        # Try Google News as fallback
        if not articles and self.google_api_key:
            articles.extend(self._search_google_news(query, days))

        # Filter and process articles
        processed = []
        for article in articles:
            processed_article = self._process_article(article, city, state)
            if processed_article:
                processed.append(processed_article)

        logger.info(f"Found {len(processed)} Publix news articles")
        return processed

    def search_competitor_news(
        self,
        competitor: str,
        city: Optional[str] = None,
        state: Optional[str] = None,
        days: int = 30,
    ) -> List[Dict]:
        """
        Search for news articles about competitors

        Args:
            competitor: Competitor name (Walmart, Kroger, etc.)
            city: Optional city name
            state: Optional state abbreviation
            days: Number of days to look back

        Returns:
            List of news article dictionaries
        """
        articles = []

        # Build query
        query = competitor
        if city and state:
            query += f" opening store {city} {state}"
        elif state:
            query += f" opening store {state}"

        # Try NewsAPI first
        if self.newsapi_key:
            articles.extend(self._search_newsapi(query, days))

        # Try Google News as fallback
        if not articles and self.google_api_key:
            articles.extend(self._search_google_news(query, days))

        # Filter and process articles
        processed = []
        for article in articles:
            processed_article = self._process_article(article, city, state, competitor)
            if processed_article:
                processed.append(processed_article)

        logger.info(f"Found {len(processed)} {competitor} news articles")
        return processed

    def _search_newsapi(self, query: str, days: int) -> List[Dict]:
        """Search using NewsAPI"""
        if not self.newsapi_key:
            return []

        try:
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            params = {
                "q": query,
                "apiKey": self.newsapi_key,
                "language": "en",
                "sortBy": "publishedAt",
                "from": from_date,
                "pageSize": 50,
            }

            response = requests.get(self.newsapi_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("status") == "ok":
                return data.get("articles", [])

        except Exception as e:
            logger.error(f"NewsAPI error: {e}", exc_info=True)

        return []

    def _search_google_news(self, query: str, days: int) -> List[Dict]:
        """Search using Google News (via Custom Search API)"""
        if not self.google_api_key:
            return []

        try:
            # Note: Requires Custom Search Engine ID
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            if not search_engine_id:
                logger.warning("GOOGLE_SEARCH_ENGINE_ID not set")
                return []

            params = {
                "key": self.google_api_key,
                "cx": search_engine_id,
                "q": query,
                "num": 10,
            }

            response = requests.get(self.google_news_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for item in data.get("items", []):
                articles.append(
                    {
                        "title": item.get("title"),
                        "description": item.get("snippet"),
                        "url": item.get("link"),
                        "publishedAt": item.get("publishDate"),
                        "source": {"name": item.get("displayLink")},
                    }
                )

            return articles

        except Exception as e:
            logger.error(f"Google News error: {e}", exc_info=True)

        return []

    def _process_article(
        self,
        article: Dict,
        city: Optional[str] = None,
        state: Optional[str] = None,
        competitor: Optional[str] = None,
    ) -> Optional[Dict]:
        """Process and enrich article data"""
        title = article.get("title", "")
        content = article.get("description", "") or article.get("content", "")
        url = article.get("url", "")

        if not title or not url:
            return None

        # Extract published date
        published_str = article.get("publishedAt", "")
        published_date = None
        if published_str:
            try:
                # Try parsing ISO format
                published_date = datetime.fromisoformat(
                    published_str.replace("Z", "+00:00")
                )
            except:
                try:
                    # Try other formats
                    published_date = datetime.strptime(
                        published_str, "%Y-%m-%dT%H:%M:%S"
                    )
                except:
                    pass

        # Determine topic
        topic = self._classify_topic(title, content)

        # Determine sentiment
        sentiment = self._classify_sentiment(title, content)

        # Check if mentions Publix
        mentions_publix = (
            ("publix" in title.lower() or "publix" in content.lower())
            if not competitor
            else False
        )

        # Calculate relevance score
        relevance_score = self._calculate_relevance(title, content, city, state)

        return {
            "title": title,
            "content": content[:1000] if content else "",  # Limit content length
            "source": article.get("source", {}).get("name", "Unknown"),
            "url": url,
            "published_date": published_date,
            "city": city,
            "state": state,
            "topic": topic,
            "sentiment": sentiment,
            "mentions_publix": mentions_publix,
            "mentions_competitor": competitor if competitor else None,
            "relevance_score": relevance_score,
        }

    def _classify_topic(self, title: str, content: str) -> str:
        """Classify article topic"""
        text = (title + " " + content).lower()

        if any(word in text for word in ["opening", "new store", "coming soon"]):
            return "expansion"
        elif any(word in text for word in ["closing", "closing down", "shutting"]):
            return "closure"
        elif any(word in text for word in ["planning", "proposed", "zoning"]):
            return "planning"
        elif any(word in text for word in ["announcement", "announced"]):
            return "announcement"
        else:
            return "general"

    def _classify_sentiment(self, title: str, content: str) -> str:
        """Classify article sentiment"""
        text = (title + " " + content).lower()

        positive_words = ["great", "excited", "welcome", "success", "growth"]
        negative_words = ["oppose", "concern", "worried", "against", "protest"]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _calculate_relevance(
        self, title: str, content: str, city: Optional[str], state: Optional[str]
    ) -> float:
        """Calculate relevance score (0.0 to 1.0)"""
        score = 0.5  # Base score

        text = (title + " " + content).lower()

        # Boost if mentions location
        if city and city.lower() in text:
            score += 0.2
        if state and state.lower() in text:
            score += 0.2

        # Boost if mentions expansion-related terms
        expansion_terms = ["store", "grocery", "supermarket", "retail", "shopping"]
        if any(term in text for term in expansion_terms):
            score += 0.1

        return min(1.0, score)
