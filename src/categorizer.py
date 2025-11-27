"""
Article categorizer module for grouping articles by subject.
"""
from typing import List, Dict
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleCategorizer:
    """Categorizes articles based on keywords."""
    
    def __init__(self, categories: Dict):
        """
        Initialize the categorizer.
        
        Args:
            categories: Dictionary mapping category names to keyword lists
        """
        self.categories = categories
        
    def categorize_articles(self, articles: List) -> Dict[str, List]:
        """
        Categorize articles based on title and summary.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Dictionary mapping category names to lists of articles
        """
        categorized = defaultdict(list)
        
        for article in articles:
            # Combine title and summary for keyword matching
            text = f"{article.title} {article.summary}".lower()
            
            # Find matching categories
            matched_categories = []
            for category_name, category_info in self.categories.items():
                keywords = category_info.get('keywords', [])
                if keywords and self._matches_keywords(text, keywords):
                    matched_categories.append(category_name)
            
            # If no category matched, assign to default category
            if not matched_categories:
                matched_categories = ["Software Engineering & Systems"]
            
            # Add article to all matched categories
            for category in matched_categories:
                categorized[category].append(article)
        
        # Sort articles within each category by date (newest first)
        for category in categorized:
            categorized[category].sort(
                key=lambda x: x.published if x.published else datetime.min,
                reverse=True
            )
        
        # Log categorization results
        for category, articles in categorized.items():
            logger.info(f"Category '{category}': {len(articles)} articles")
            
        return dict(categorized)
    
    def _matches_keywords(self, text: str, keywords: List[str]) -> bool:
        """
        Check if text matches any of the keywords.
        
        Args:
            text: Text to search (should be lowercase)
            keywords: List of keywords to search for
            
        Returns:
            True if any keyword is found in text
        """
        return any(keyword.lower() in text for keyword in keywords)


# Import datetime for sorting
from datetime import datetime
