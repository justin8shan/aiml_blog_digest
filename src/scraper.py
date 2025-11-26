"""
Blog scraper module for fetching articles from RSS feeds.
"""
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Article:
    """Represents a blog article."""
    
    def __init__(self, title: str, link: str, published: datetime, 
                 summary: str, source: str):
        self.title = title
        self.link = link
        self.published = published
        self.summary = summary
        self.source = source
        
    def to_dict(self) -> Dict:
        """Convert article to dictionary."""
        return {
            'title': self.title,
            'link': self.link,
            'published': self.published.isoformat() if self.published else None,
            'summary': self.summary,
            'source': self.source
        }
    
    def __repr__(self):
        return f"Article(title='{self.title}', source='{self.source}')"


class BlogScraper:
    """Scrapes articles from tech blog RSS feeds."""
    
    def __init__(self, blogs: List[Dict]):
        """
        Initialize the blog scraper.
        
        Args:
            blogs: List of blog configurations with name, url, and rss_feed
        """
        self.blogs = blogs
        
    def fetch_articles(self, days_back: int = 7) -> List[Article]:
        """
        Fetch articles from all configured blogs.
        
        Args:
            days_back: Number of days to look back for articles
            
        Returns:
            List of Article objects
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        all_articles = []
        
        for blog in self.blogs:
            logger.info(f"Fetching articles from {blog['name']}...")
            try:
                articles = self._fetch_blog_articles(blog, cutoff_date)
                all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {blog['name']}")
            except Exception as e:
                logger.error(f"Error fetching from {blog['name']}: {str(e)}")
                
        logger.info(f"Total articles fetched: {len(all_articles)}")
        return all_articles
    
    def _fetch_blog_articles(self, blog: Dict, cutoff_date: datetime) -> List[Article]:
        """
        Fetch articles from a single blog's RSS feed.
        
        Args:
            blog: Blog configuration dictionary
            cutoff_date: Only fetch articles published after this date
            
        Returns:
            List of Article objects
        """
        articles = []
        
        try:
            feed = feedparser.parse(blog['rss_feed'])
            
            for entry in feed.entries:
                # Parse publication date
                published = self._parse_date(entry)
                
                # Skip articles older than cutoff date
                if published and published < cutoff_date:
                    continue
                
                # Extract article information
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                summary = entry.get('summary', entry.get('description', ''))
                
                # Clean HTML tags from summary if present
                summary = self._clean_html(summary)
                
                article = Article(
                    title=title,
                    link=link,
                    published=published,
                    summary=summary,
                    source=blog['name']
                )
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error parsing feed for {blog['name']}: {str(e)}")
            
        return articles
    
    def _parse_date(self, entry) -> datetime:
        """Parse publication date from feed entry."""
        # Try different date fields
        for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
            if hasattr(entry, date_field):
                time_struct = getattr(entry, date_field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except:
                        pass
        
        # If no date found, use current time
        return datetime.now()
    
    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        # Remove HTML tags
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text[:300]  # Limit summary length
