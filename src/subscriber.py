"""
Database utilities for Supabase subscriber management.
"""
import os
import logging
from typing import List, Optional
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Subscriber:
    """Manages subscriber data in Supabase."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.client: Optional[Client] = None
        
        if self.supabase_url and self.supabase_key:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {str(e)}")
        else:
            logger.warning("SUPABASE_URL or SUPABASE_KEY not found in environment")
    
    def get_active_subscribers(self) -> List[str]:
        """
        Fetch list of active subscriber email addresses.
        
        Returns:
            List of email addresses for active subscribers
        """
        if not self.client:
            logger.warning("Supabase client not initialized. Returning empty list.")
            return []
        
        try:
            response = self.client.table('subscribers')\
                .select('email')\
                .eq('is_active', True)\
                .execute()
            
            emails = [row['email'] for row in response.data]
            logger.info(f"Retrieved {len(emails)} active subscribers from database")
            return emails
            
        except Exception as e:
            logger.error(f"Failed to fetch subscribers from database: {str(e)}")
            return []
