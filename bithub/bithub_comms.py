"""
Why: Manages the Synapse Layer (Transport) for the Neural Net Link.
What: Handles Flash (Realtime) and Deep (Memory) Synapse protocols.
How: Wraps signals with a RateLimiter (Neurotransmitter Regulation) and retry logic.
"""

import random
import os
import sys
import requests
import time
import html
import re
import json
import logging
from typing import Optional, List, Dict, Any

from .bithub_errors import BithubError, BithubAuthError, BithubNetworkError, BithubRateLimitError

# logging setup
logger = logging.getLogger(__name__)

class RateLimiter:
    """Implements a simple rate limiter with jitter to manage API request frequency.

    Attributes:
        interval (float): The minimum time interval between calls in seconds.
        last_call (float): The timestamp of the last successful call.
        jitter (float): The jitter factor to randomize wait times.
    """

    def __init__(self, calls_per_minute: int = 60, jitter: float = 0.1):
        """Initializes the RateLimiter.

        Args:
            calls_per_minute (int): The number of allowed calls per minute. Defaults to 60.
            jitter (float): The randomness factor for wait times. Defaults to 0.1.
        """
        self.interval = 60.0 / calls_per_minute
        self.last_call = 0
        self.jitter = jitter

    def wait(self) -> None:
        """Blocks execution until the rate limit allows a new call.

        Calculates the required wait time based on the last call timestamp and the
        configured interval. Adds random jitter to the wait time.
        """
        elapsed = time.time() - self.last_call
        wait_time = self.interval - elapsed
        if wait_time > 0:
            noise = random.uniform(0, self.jitter * self.interval)
            time.sleep(wait_time + noise)
        self.last_call = time.time()

class BithubComms:
    """Handles communication with the Bithub (Discourse) API.

    Manages authentication, rate limiting, and request execution for various
    Discourse endpoints including posts, topics, and chat.

    Attributes:
        base_url (str): The base URL of the Bithub instance.
        user_api_key (str): The API key for authentication.
        global_limiter (RateLimiter): Rate limiter for all requests.
        write_limiter (RateLimiter): Rate limiter specifically for write operations.
        headers (Dict[str, str]): Standard HTTP headers for requests.
    """

    def __init__(self):
        """Initializes the BithubComms client.

        Raises:
            BithubAuthError: If the "BITHUB_USER_API_KEY" environment variable is missing.
        """
        self.base_url = os.environ.get("BITHUB_URL", "https://hub.bitwiki.org").rstrip("/")
        self.user_api_key = os.environ.get("BITHUB_USER_API_KEY")

        if not self.user_api_key:
            raise BithubAuthError("[Security] BITHUB_USER_API_KEY is required. Anonymous access disabled.")

        self.global_limiter = RateLimiter(calls_per_minute=100)
        self.write_limiter = RateLimiter(calls_per_minute=50)

        self.headers = {
            "Content-Type": "application/json",
            "User-Api-Key": self.user_api_key,
            "User-Agent": "AgentZero-Swarm/2.3"
        }

    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, retries: int = 4) -> Dict[str, Any]:
        """Executes an HTTP request to the Bithub API with retries and rate limiting.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST").
            endpoint (str): The API endpoint path (e.g., "/posts.json").
            params (Optional[Dict[str, Any]]): URL query parameters. Defaults to None.
            json_data (Optional[Dict[str, Any]]): JSON body payload. Defaults to None.
            retries (int): The number of retry attempts for failed requests. Defaults to 4.

        Returns:
            Dict[str, Any]: The JSON response from the API.

        Raises:
            BithubAuthError: If authentication fails (401/403).
            BithubRateLimitError: If rate limits are exceeded and retries are exhausted (429).
            BithubNetworkError: If network issues persist or max retries are exceeded.
            BithubError: For other non-2xx HTTP responses.
        """
        url = f"{self.base_url}{endpoint}"

        self.global_limiter.wait()
        if method in ["POST", "PUT", "DELETE"]:
            self.write_limiter.wait()

        backoff = 1
        for attempt in range(retries):
            try:
                response = requests.request(
                    method, url, headers=self.headers, params=params, json=json_data
                )

                if response.ok:
                    return response.json()

                if response.status_code in [401, 403]:
                    raise BithubAuthError(f"HTTP {response.status_code}: {response.text}")

                if response.status_code == 429:
                    if attempt == retries - 1:
                        raise BithubRateLimitError(f"Rate limit exceeded after {retries} retries")
                    
                    wait_time = int(response.headers.get("Retry-After", backoff))
                    logger.warning(f"[System] Rate limit (429). Cooling {wait_time}s...")
                    time.sleep(wait_time)
                    backoff *= 2
                    continue

                if response.status_code >= 500:
                    logger.warning(f"[System] Server error ({response.status_code}). Retrying in {backoff}s...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                # Other non-2xx errors (e.g., 400, 404)
                raise BithubError(f"HTTP {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise BithubNetworkError(f"Network error after {retries} retries: {e}") from e
                
                logger.warning(f"[Network] Error: {e}. Retrying...")
                time.sleep(backoff)
                backoff *= 2

        raise BithubNetworkError("Max retries exceeded")

    def _enforce_audience_format(self, content: str, audience: str) -> str:
        """Validates content format based on target audience.

        Args:
            content (str): The raw content to validate.
            audience (str): The target audience ('human' or 'ai').

        Returns:
            str: The validated (and potentially extracted) content.

        Raises:
            BithubError: If validation fails for the specified audience.
        """
        if audience == 'human':
            return content
        
        if audience == 'ai':
            # Try parsing as pure JSON first
            try:
                json.loads(content)
                return content
            except json.JSONDecodeError:
                pass
            
            # Try extracting from markdown code block
            match = re.search(r"```json\s*({.*?})\s*```", content, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError:
                    pass
            
            raise BithubError("Content validation failed: AI audience requires valid JSON.")
        
        return content

    def create_topic(self, title: str, raw: str, category_id: Optional[int] = None, tags: Optional[List[str]] = None, target_audience: str = 'human', sync: bool = False, timeout: int = 45, poll_interval: int = 2) -> Optional[Dict[str, Any]]:
        """Creates a new topic.

        Args:
            title (str): The title of the topic.
            raw (str): The content of the first post.
            category_id (Optional[int]): The category ID. Defaults to None.
            tags (Optional[List[str]]): A list of tags. Defaults to None.
            target_audience (str): Target audience ('human' or 'ai'). Defaults to 'human'.
            sync (bool): If True, wait for a reply. Defaults to False.
            timeout (int): Max wait time in seconds. Defaults to 45.
            poll_interval (int): Seconds between polls. Defaults to 2.

        Returns:
            Dict[str, Any]: The API response (created topic or reply post).
        """
        raw = self._enforce_audience_format(raw, target_audience)

        payload = {
            "title": title,
            "raw": raw
        }
        if category_id:
            payload["category"] = category_id
        if tags:
            payload["tags"] = tags

        response = self._request("POST", "/posts.json", json_data=payload)

        if not sync:
            return response

        topic_id = response.get("topic_id")
        post_id = response.get("id")

        if not topic_id or not post_id:
            return response

        return self.wait_for_reply(topic_id, post_id, timeout, poll_interval)

    def send_private_message(self, recipients: List[str], title: str, raw: str, meta_data: Optional[Dict[str, Any]] = None, target_audience: str = 'human', sync: bool = False, timeout: int = 45, poll_interval: int = 2) -> Optional[Dict[str, Any]]:
        """Sends a private message to one or more users.

        Args:
            recipients (List[str]): A list of usernames to receive the message.
            title (str): The subject line of the message.
            raw (str): The body content of the message.
            meta_data (Optional[Dict[str, Any]]): Additional metadata to attach to the post. Defaults to None.
            target_audience (str): Target audience ('human' or 'ai'). Defaults to 'human'.
            sync (bool): If True, wait for a reply. Defaults to False.
            timeout (int): Max wait time in seconds. Defaults to 45.
            poll_interval (int): Seconds between polls. Defaults to 2.

        Returns:
            Dict[str, Any]: The API response (created post or reply post).

        Raises:
            ValueError: If the recipients list is invalid.
        """
        if not recipients or not all(isinstance(r, str) for r in recipients):
            raise ValueError("Invalid recipients list")
        
        raw = self._enforce_audience_format(raw, target_audience)
        
        payload = {
            "title": title,
            "raw": raw,
            "archetype": "private_message",
            "target_recipients": ",".join(recipients)
        }
        if meta_data:
            for k, v in meta_data.items():
                payload[f"meta_data[{k}]"] = v

        response = self._request("POST", "/posts.json", json_data=payload)

        if not sync:
            return response

        topic_id = response.get("topic_id")
        post_id = response.get("id")

        if not topic_id or not post_id:
            return response

        return self.wait_for_reply(topic_id, post_id, timeout, poll_interval)

    def reply_to_post(self, topic_id: int, raw: str, reply_to_post_number: Optional[int] = None, target_audience: str = 'human', sync: bool = False, timeout: int = 45, poll_interval: int = 2) -> Optional[Dict[str, Any]]:
        """Replies to an existing topic or specific post.

        Args:
            topic_id (int): The ID of the topic to reply to.
            raw (str): The content of the reply.
            reply_to_post_number (Optional[int]): The specific post number to reply to. Defaults to None.
            target_audience (str): Target audience ('human' or 'ai'). Defaults to 'human'.
            sync (bool): If True, wait for a reply. Defaults to False.
            timeout (int): Max wait time in seconds. Defaults to 45.
            poll_interval (int): Seconds between polls. Defaults to 2.

        Returns:
            Dict[str, Any]: The API response containing the new post details (or reply if sync).
        """
        raw = self._enforce_audience_format(raw, target_audience)

        payload = {"topic_id": topic_id, "raw": raw}
        if reply_to_post_number:
            payload["reply_to_post_number"] = reply_to_post_number
        response = self._request("POST", "/posts.json", json_data=payload)

        if not sync:
            return response

        topic_id = response.get("topic_id")
        post_id = response.get("id")

        if not topic_id or not post_id:
            return response

        return self.wait_for_reply(topic_id, post_id, timeout, poll_interval)

    def get_topic_posts(self, topic_id: int) -> Dict[str, Any]:
        """Retrieves all posts for a specific topic.

        Args:
            topic_id (int): The ID of the topic.

        Returns:
            Dict[str, Any]: The topic data including the post stream.
        """
        return self._request("GET", f"/t/{topic_id}.json")

    def update_post(self, post_id: int, raw: str) -> Dict[str, Any]:
        """Updates an existing post.

        Args:
            post_id (int): The ID of the post to update.
            raw (str): The new content for the post.

        Returns:
            Dict[str, Any]: The API response.
        """
        payload = {"post": {"raw": raw}}
        return self._request("PUT", f"/posts/{post_id}.json", json_data=payload)

    def get_post(self, post_id: int) -> Dict[str, Any]:
        """Retrieves a single post by its ID.

        Args:
            post_id (int): The ID of the post.

        Returns:
            Dict[str, Any]: The post data.
        """
        return self._request("GET", f"/posts/{post_id}.json")

    def get_notifications(self, limit: int = 30) -> Dict[str, Any]:
        """Retrieves the user"s notifications.

        Args:
            limit (int): The maximum number of notifications to return. Defaults to 30.

        Returns:
            Dict[str, Any]: A list of notifications.
        """
        return self._request("GET", f"/notifications.json?limit={limit}")

    def wait_for_reply(self, topic_id: int, last_post_id: int, timeout: int = 45, poll_interval: int = 2) -> Optional[Dict[str, Any]]:
        """Polls a topic for a new reply after a specific post ID.

        Args:
            topic_id (int): The ID of the topic to monitor.
            last_post_id (int): The ID of the last known post.
            timeout (int): The maximum time to wait in seconds. Defaults to 45.
            poll_interval (int): Seconds between polls. Defaults to 2.

        Returns:
            Optional[Dict[str, Any]]: The new post object if found, otherwise None.
        """
        start_time = time.time()
        logger.debug(f"[System] Polling Topic {topic_id} for reply > {last_post_id}...")
        while (time.time() - start_time) < timeout:
            topic_data = self.get_topic_posts(topic_id)
            stream = topic_data.get("post_stream", {}).get("stream", [])
            if stream and stream[-1] > last_post_id:
                new_post_id = stream[-1]
                post = self.get_post(new_post_id)
                if post.get("cooked") or post.get("raw"):
                    return post
                else:
                    logger.debug("[System] Reply detected but empty. Waiting for stream...")
                    time.sleep(2)
                    continue
            time.sleep(poll_interval)
        return None

    def delete_post(self, post_id: int) -> Dict[str, Any]:
        """Deletes a specific post.

        Args:
            post_id (int): The ID of the post to delete.

        Returns:
            Dict[str, Any]: The API response.
        """
        return self._request("DELETE", f"/posts/{post_id}.json")

    def delete_topic(self, topic_id: int) -> Dict[str, Any]:
        """Deletes a specific topic.

        Args:
            topic_id (int): The ID of the topic to delete.

        Returns:
            Dict[str, Any]: The API response.
        """
        return self._request("DELETE", f"/t/{topic_id}.json")

    def delete_user(self, user_id: int, delete_posts: bool = False) -> Dict[str, Any]:
        """Deletes a user.

        WARNING: This action is irreversible.

        Args:
            user_id (int): The ID of the user to delete.
            delete_posts (bool): If True, delete all posts by the user. Defaults to False.

        Returns:
            Dict[str, Any]: The API response.
        """
        payload = {"delete_posts": delete_posts, "block_email": False, "block_urls": False, "block_ip": False}
        return self._request("DELETE", f"/admin/users/{user_id}.json", json_data=payload)

    # --- Chat API Methods ---
    def get_chat_channels(self) -> Dict[str, Any]:
        """Retrieves a list of chat channels available to the user.

        Returns:
            Dict[str, Any]: The list of chat channels.
        """
        return self._request("GET", "/chat/api/me/channels.json")

    def get_chat_messages(self, channel_id: int, page_size: int = 20) -> Dict[str, Any]:
        """Retrieves messages from a specific chat channel.

        Args:
            channel_id (int): The ID of the chat channel.
            page_size (int): The number of messages to retrieve. Defaults to 20.

        Returns:
            Dict[str, Any]: The list of chat messages.
        """
        return self._request("GET", f"/chat/api/channels/{channel_id}/messages.json?page_size={page_size}")

    def create_dm_channel(self, usernames: List[str]) -> Dict[str, Any]:
        """Retrieves (or creates) a direct message channel with the specified users.

        Args:
            usernames (List[str]): A list of usernames to include in the DM.

        Returns:
            Dict[str, Any]: The channel details (e.g. {'channel': {'id': ...}}).
        """
        # Updated to use GET /chat/direct_messages.json which retrieves the existing DM channel
        params = {"usernames": ",".join(usernames)}
        return self._request("GET", "/chat/direct_messages.json", params=params)

    def send_chat_message(self, channel_id: int, message: str) -> Dict[str, Any]:
        """Sends a message to a chat channel.

        Args:
            channel_id (int): The ID of the chat channel.
            message (str): The content of the message.

        Returns:
            Dict[str, Any]: The API response.
        """
        payload = {"message": message}
        return self._request("POST", f"/chat/{channel_id}.json", json_data=payload)

    def sanitize_html(self, raw_html: str) -> str:
        """Sanitizes HTML content by removing scripts, styles, and tags.

        Args:
            raw_html (str): The raw HTML string to sanitize.

        Returns:
            str: The plain text content with HTML tags removed.
        """
        if not raw_html: return ""
        text = html.unescape(raw_html)
        text = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE)
        clean = re.sub(r"<[^>]+>", "", text)
        return clean.strip()
