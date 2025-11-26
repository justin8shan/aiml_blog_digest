#!/usr/bin/env python3
"""
Main script to orchestrate the weekly blog digest generation and email sending.
"""
import argparse
import logging
from pathlib import Path

from scraper import BlogScraper
from categorizer import ArticleCategorizer
from email_digest import EmailDigest
from utils import load_config, get_config_path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main(days_back: int = 7, send_email: bool = True):
    """
    Main function to run the blog digest pipeline.
    
    Args:
        days_back: Number of days to look back for articles
        send_email: Whether to send email or just generate digest
    """
    try:
        logger.info("Starting blog digest generation...")
        
        # Load configurations
        logger.info("Loading configuration files...")
        blogs_config = load_config(get_config_path('blogs.yaml'))
        categories_config = load_config(get_config_path('categories.yaml'))
        email_config = load_config(get_config_path('email_config.yaml'))
        footer_config = load_config(get_config_path('footer_config.yaml'))
        
        # Step 1: Fetch articles from blogs
        logger.info(f"Fetching articles from the last {days_back} days...")
        scraper = BlogScraper(blogs_config['blogs'])
        articles = scraper.fetch_articles(days_back=days_back)
        
        if not articles:
            logger.warning("No articles found. Exiting.")
            return
        
        logger.info(f"Successfully fetched {len(articles)} articles")
        
        # Step 2: Categorize articles
        logger.info("Categorizing articles...")
        categorizer = ArticleCategorizer(categories_config['categories'])
        categorized_articles = categorizer.categorize_articles(articles)
        
        # Step 3: Generate and send email digest
        email_sender = EmailDigest(email_config, footer_config, blogs_config)
        
        if send_email:
            logger.info("Sending email digest...")
            success = email_sender.send_digest(categorized_articles)
            
            if success:
                logger.info("✓ Blog digest completed successfully!")
            else:
                logger.error("✗ Failed to send email digest")
                return False
        else:
            # Just generate and print digest for testing
            logger.info("Generating digest (email sending disabled)...")
            from datetime import datetime
            week_start = datetime.now().strftime("%B %d, %Y")
            text_digest = email_sender.generate_text_digest(
                categorized_articles, week_start
            )
            print("\n" + "=" * 80)
            print(text_digest)
            print("=" * 80 + "\n")
            logger.info("Digest generated successfully (not sent)")
        
        return True
        
    except Exception as e:
        logger.error(f"Error in main pipeline: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate and send weekly AI/ML blog digest"
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back for articles (default: 7)'
    )
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Generate digest without sending email (for testing)'
    )
    
    args = parser.parse_args()
    
    success = main(days_back=args.days, send_email=not args.no_email)
    exit(0 if success else 1)
