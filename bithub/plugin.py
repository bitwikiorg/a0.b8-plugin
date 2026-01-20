"""
Title: Bithub Plugin Client
Description: High-level client for the Bithub plugin system.
"""


import os
import json
import logging
from typing import List, Dict, Any, Optional

from .bithub_cores import BithubCores
from .bithub_registry import parse_markdown_table
from .bithub_config import REGISTRY_FILE, REGISTRY_TOPIC_ID
from .bithub_errors import BithubError

logger = logging.getLogger(__name__)

class BithubClient:
    """High-level client for the Bithub plugin system.

    Provides simplified access to messaging, agent discovery, and core workflow deployment.
    """

    def __init__(self):
        """Initializes the BithubClient."""
        try:
            # BithubCores inherits from BithubComms, so it handles auth and basic comms too.
            self._cores = BithubCores()
        except Exception as e:
            logger.error(f"Failed to initialize Bithub backend: {e}")
            raise

    def send_message(self, bot: str, text: str) -> Dict[str, Any]:
        """Sends a private message to a specific bot or user.

        Args:
            bot (str): The username of the recipient (e.g., 'my_bot').
            text (str): The message content.

        Returns:
            Dict[str, Any]: The API response or an error dict.
        """
        try:
            # Ensure username has no @ for the API call if the API expects raw username,
            # but BithubComms.send_private_message takes a list of strings.
            recipient = bot.lstrip('@')

            response = self._cores.send_private_message(
                recipients=[recipient],
                title="Message from BithubClient",
                raw=text
            )
            return response
        except Exception as e:
            logger.error(f"Failed to send message to {bot}: {e}")
            return {"error": str(e), "status": "failed"}

    def list_agents(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Lists available agents from the registry.

        Args:
            force_refresh (bool): If True, forces a download of the latest registry from the hub.

        Returns:
            List[Dict[str, Any]]: A list of agent dictionaries.
        """
        if force_refresh or not os.path.exists(REGISTRY_FILE):
            self._refresh_registry()

        try:
            with open(REGISTRY_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return self._refresh_registry()

    def get_cores(self) -> BithubCores:
        """Returns the underlying BithubCores instance for advanced workflow operations.

        Returns:
            BithubCores: The initialized cores client.
        """
        return self._cores

    def _refresh_registry(self) -> List[Dict[str, Any]]:
        """Internal method to refresh the local registry cache."""
        try:
            logger.info(f"Refreshing registry from topic {REGISTRY_TOPIC_ID}...")
            topic = self._cores.get_topic_posts(REGISTRY_TOPIC_ID)
            stream = topic.get('post_stream', {}).get('posts', [])

            if not stream:
                logger.warning("Registry topic has no posts.")
                return []

            first_post_id = stream[0]
            post = self._cores.get_post(first_post_id)
            raw_content = post.get('raw', '')

            agents = parse_markdown_table(raw_content)

            # Ensure directory exists
            os.makedirs(os.path.dirname(REGISTRY_FILE) or '.', exist_ok=True)

            with open(REGISTRY_FILE, 'w') as f:
                json.dump(agents, f, indent=2)

            return agents
        except Exception as e:
            logger.error(f"Failed to refresh registry: {e}")
            return []
