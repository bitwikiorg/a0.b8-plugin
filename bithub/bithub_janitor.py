"""
Why: Handles bulk deletion and cleanup operations.
What: Extends BithubComms to provide safe, throttled deletion capabilities.
How: Implements a 'slow nuke' strategy to avoid rate limits and server load.
"""

import time
import sys
import logging
from typing import List, Dict, Any
from .bithub_comms import BithubComms

# logging setup
logger = logging.getLogger(__name__)

class BithubJanitor(BithubComms):
    """Specialized class for cleanup operations."""

    def nuke_category(self, category_id: int, delay: int = 2) -> None:
        """Deletes all topics in a category with a safety delay.

        Args:
            category_id (int): The ID of the category to clear.
            delay (int): Seconds to sleep between deletions. Defaults to 2.
        """
        logger.info(f"[Janitor] Starting nuke of Category {category_id}...")
        
        # Fetch topics (this might need pagination in a real scenario, 
        # but for now we assume one batch or implement simple looping if needed)
        # Using the existing _request method to get latest topics
        endpoint = f"/c/{category_id}.json"
        try:
            response = self._request("GET", endpoint)
            topic_list = response.get("topic_list", {}).get("topics", [])
            
            if not topic_list:
                logger.info("[Janitor] No topics found to delete.")
                return

            count = 0
            for topic in topic_list:
                t_id = topic['id']
                logger.info(f"[Janitor] Deleting Topic {t_id}...")
                try:
                    self.delete_topic(t_id)
                    count += 1
                except Exception as e:
                    logger.error(f"[Janitor] Failed to delete Topic {t_id}: {e}")
                
                # Enforce slow nuke constraint
                time.sleep(delay)
            
            logger.info(f"[Janitor] Nuke complete. Deleted {count} topics.")
            
        except Exception as e:
            logger.error(f"[Janitor] Failed to fetch category {category_id}: {e}")
