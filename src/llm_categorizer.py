"""
LLM-based article categorizer using OpenRouter or GitHub Models API.
"""
from typing import List, Dict
from collections import defaultdict
import logging
import os
import json

from categorizer import ArticleCategorizer
from utils import load_config, get_config_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMCategorizer:
    """Categorizes articles using LLM via OpenRouter or GitHub Models API."""
    
    def __init__(self, config: Dict):
        """
        Initialize the LLM categorizer.
        
        Args:
            config: Configuration dictionary with LLM settings and categories
        """
        self.config = config
        self.llm_config = config.get('llm', {})
        self.provider = self.llm_config.get('provider', 'openrouter')
        self.model = self.llm_config.get('model', 'openai/gpt-4o-mini')
        self.batch_size = self.llm_config.get('batch_size', 10)
        self.max_tokens = self.llm_config.get('max_tokens', 500)
        self.temperature = self.llm_config.get('temperature', 0.3)
        self.fallback_to_keywords = self.llm_config.get('fallback_to_keywords', True)
        
        self.categories = config.get('categories', [])
        
        # Load keyword categories from categories.yaml for fallback
        keyword_config = load_config(get_config_path('categories.yaml'))
        self.keyword_categories = keyword_config.get('categories', {})
        
        # Initialize keyword categorizer for fallback
        self.keyword_categorizer = ArticleCategorizer(self.keyword_categories)
        
        # Initialize API client
        self.client = None
        self._init_client()
        
    def _init_client(self):
        """Initialize LLM client based on provider."""
        try:
            import openai
            
            # Get provider-specific configuration
            api_config = self.llm_config.get('api_config', {}).get(self.provider, {})
            if not api_config:
                logger.warning(f"No API config found for provider: {self.provider}. Will use keyword fallback.")
                return
            
            base_url = api_config.get('base_url')
            env_var = api_config.get('env_var')
            
            # Get API key from environment
            api_key = os.getenv(env_var)
            if not api_key:
                logger.warning(f"{env_var} not found. Will use keyword fallback.")
                return
            
            # Initialize client
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            logger.info(f"{self.provider.capitalize()} client initialized successfully")
            
        except ImportError:
            logger.warning("openai package not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"Error initializing {self.provider} client: {str(e)}")
    
    def categorize_articles(self, articles: List) -> Dict[str, List]:
        """
        Categorize articles using LLM or fallback to keywords.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Dictionary mapping category names to lists of articles
        """
        if not articles:
            return {}
        
        # Try LLM categorization first
        if self.client:
            try:
                return self._categorize_with_llm(articles)
            except Exception as e:
                logger.error(f"LLM categorization failed: {str(e)}")
                if self.fallback_to_keywords:
                    logger.info("Falling back to keyword-based categorization")
                else:
                    raise
        
        # Fallback to keyword-based categorization using ArticleCategorizer
        return self.keyword_categorizer.categorize_articles(articles)
    
    def _categorize_with_llm(self, articles: List) -> Dict[str, List]:
        """
        Categorize articles using LLM in batches.
        
        Args:
            articles: List of Article objects
            
        Returns:
            Dictionary mapping category names to lists of articles
        """
        categorized = defaultdict(list)
        
        # Process articles in batches
        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1} ({len(batch)} articles)")
            
            try:
                batch_results = self._categorize_batch(batch)
                
                # Add results to categorized dict
                for article, category in zip(batch, batch_results):
                    if category:
                        categorized[category].append(article)
                        
            except Exception as e:
                logger.error(f"Error processing batch: {str(e)}")
                # Try individual articles in this batch with keyword fallback
                for article in batch:
                    category = self._categorize_single_with_keywords(article)
                    if category:
                        categorized[category].append(article)
        
        # Sort articles within each category by date
        from datetime import datetime
        for category in categorized:
            categorized[category].sort(
                key=lambda x: x.published if x.published else datetime.min,
                reverse=True
            )
        
        # Log results
        for category, arts in categorized.items():
            logger.info(f"Category '{category}': {len(arts)} articles")
        
        return dict(categorized)
    
    def _categorize_batch(self, articles: List) -> List[str]:
        """
        Categorize a batch of articles using LLM.
        
        Args:
            articles: List of Article objects
            
        Returns:
            List of category names (one per article)
        """
        # Create category list for prompt
        category_list = "\n".join([
            f"{i+1}. {cat['name']}: {cat['description']}"
            for i, cat in enumerate(self.categories)
        ])
        
        # Create articles summary for prompt
        articles_text = ""
        for i, article in enumerate(articles):
            articles_text += f"\nArticle {i+1}:\n"
            articles_text += f"Title: {article.title}\n"
            articles_text += f"Source: {article.source}\n"
            articles_text += f"Summary: {article.summary[:200]}...\n"
        
        # Create prompt
        prompt = f"""Categorize the following technical blog articles into ONE of these categories:

{category_list}

Articles to categorize:
{articles_text}

Return ONLY a JSON array with the category name for each article, in order.
Example format: ["Category Name 1", "Category Name 2", ...]

If an article doesn't clearly fit any category, use "Software Engineering & Systems".
"""
        
        # Call API based on provider
        return self._call_llm_api(prompt, len(articles))
    
    def _call_llm_api(self, prompt: str, expected_count: int) -> List[str]:
        """Call LLM API (OpenRouter or GitHub Models)."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a technical article categorization assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        result = response.choices[0].message.content
        # Parse JSON response
        try:
            # Clean markdown code blocks if present (some models wrap JSON in ```json```)
            cleaned_result = result.strip()
            if cleaned_result.startswith('```'):
                # Remove markdown code block markers
                lines = cleaned_result.split('\n')
                # Remove first line (```json or ```)
                lines = lines[1:]
                # Remove last line if it's just ```
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]
                cleaned_result = '\n'.join(lines).strip()
            
            data = json.loads(cleaned_result)
            # Handle different possible response formats
            if isinstance(data, list):
                categories = data
            elif 'categories' in data:
                categories = data['categories']
            elif 'results' in data:
                categories = data['results']
            else:
                # Take the first list found in the dict
                categories = next(v for v in data.values() if isinstance(v, list))
            
            # Validate we got the right number of results
            if len(categories) != expected_count:
                logger.warning(f"Expected {expected_count} categories, got {len(categories)}")
                # Pad or truncate
                categories = (categories + ["Software Engineering & Systems"] * expected_count)[:expected_count]
            
            return categories
        except (json.JSONDecodeError, StopIteration) as e:
            logger.error(f"Failed to parse LLM response: {result}")
            raise
    
    def _categorize_single_with_keywords(self, article) -> str:
        """Get category for single article using keywords."""
        text = f"{article.title} {article.summary}".lower()
        
        for category_name, category_info in self.keyword_categories.items():
            keywords = category_info.get('keywords', [])
            if any(keyword.lower() in text for keyword in keywords):
                return category_name
        
        return "Software Engineering & Systems"
