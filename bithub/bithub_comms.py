\"\"\"
WHY: To provide a robust, rate-limited transport layer (Telepathy) for the Agent Zero node.
WHAT: Manages Flash (Realtime) and Deep (Memory) Synapse protocols via the Bithub API.
HOW: Implements a centralized request handler with exponential backoff and neurotransmitter regulation (RateLimiting).
\"\"\"

import random
import os
import requests
import time
import re
import json
import logging
from typing import Optional, List, Dict, Any

from .bithub_errors import BithubError, BithubAuthError, BithubNetworkError, BithubRateLimitError

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, calls_per_minute: int = 60, jitter: float = 0.1):
        self.interval = 60.0 / calls_per_minute
        self.last_call = 0
        self.jitter = jitter

    def wait(self) -> None:
        elapsed = time.time() - self.last_call
        wait_time = self.interval - elapsed
        if wait_time > 0:
            noise = random.uniform(0, self.jitter * self.interval)
            time.sleep(wait_time + noise)
        self.last_call = time.time()

class BithubComms:
    # Hard Invariants
    MAX_CONTENT_LENGTH = 32000
    DEFAULT_RETRIES = 4

    def __init__(self):
        # Guard: Environment Validation
        self.base_url = os.environ.get("BITHUB_URL", "https://hub.bitwiki.org").rstrip("/")
        self.user_api_key = os.environ.get("BITHUB_USER_API_KEY")

        if not self.user_api_key:
            raise BithubAuthError("CRITICAL: BITHUB_USER_API_KEY is missing. Synaptic bridge cannot initialize.")

        if not self.base_url.startswith('http'):
            raise BithubError(f"CRITICAL: Invalid BITHUB_URL format: {self.base_url}")

        # Do: Initialize state
        self.global_limiter = RateLimiter(calls_per_minute=100)
        self.write_limiter = RateLimiter(calls_per_minute=50)
        self.headers = {
            "Content-Type": "application/json",
            "User-Api-Key": self.user_api_key,
            "User-Agent": "AgentZero-Swarm/2.3"
        }

    def _validate_genesis_purity(self, raw: str, category_id: int):
        if category_id >= 54 and re.search(r'@[a-zA-Z0-9_]+', raw):
            raise BithubError("Genesis Purity Violation: @username tags are forbidden in Core categories (ID 54+).")

    def _validate_content(self, content: str) -> None:
        if len(content) > self.MAX_CONTENT_LENGTH: raise BithubError("Content too long")
        if re.search(r'§§|\\{\\{', content): raise BithubError("Unresolved placeholders")

    def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None, retries: int = DEFAULT_RETRIES) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        self.global_limiter.wait()
        if method in ["POST", "PUT", "DELETE"]:
            self.write_limiter.wait()

        backoff = 1
        for attempt in range(retries):
            try:
                response = requests.request(method, url, headers=self.headers, params=params, json=json_data)

                if response.ok: return response.json()
                if response.status_code in [401, 403]: raise BithubAuthError(f"HTTP {response.status_code}: {response.text}")
                if response.status_code == 429:
                    if attempt == retries - 1: raise BithubRateLimitError("Rate limit exceeded")
                    wait_time = int(response.headers.get("Retry-After", backoff))
                    time.sleep(wait_time)
                    backoff *= 2
                    continue
                raise BithubError(f"HTTP {response.status_code}: {response.text}")
            except requests.exceptions.RequestException as e:
                if attempt == retries - 1: raise BithubNetworkError(f"Network error: {e}")
                time.sleep(backoff)
                backoff *= 2
        raise BithubNetworkError("Max retries exceeded")

    def get_topic_posts(self, topic_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/t/{topic_id}.json")

    def get_post(self, post_id: int) -> Dict[str, Any]:
        return self._request("GET", f"/posts/{post_id}.json")

    def send_private_message(self, recipients: List[str], title: str, raw: str) -> Dict[str, Any]:
        self._validate_genesis_purity(raw, 0)
        self._validate_content(raw)
        payload = {"title": title, "raw": raw, "archetype": "private_message", "target_recipients": ",".join(recipients)}
        return self._request("POST", "/posts.json", json_data=payload)

    def reply_to_post(self, topic_id: int, raw: str, reply_to_post_number: Optional[int] = None) -> Dict[str, Any]:
        topic_data = self.get_topic_posts(topic_id)
        posts_count = len(topic_data.get("post_stream", {}).get("posts", []))
        if posts_count < 5 and re.search(r'@[a-zA-Z0-9_]+', raw):
            raise BithubError("Post-Completion Rule: @username tags are blocked until the topic has at least 5 posts.")
        self._validate_content(raw)
        payload = {"topic_id": topic_id, "raw": raw}
        if reply_to_post_number: payload["reply_to_post_number"] = reply_to_post_number
        return self._request("POST", "/posts.json", json_data=payload)

    def get_chat_channels(self) -> Dict[str, Any]:
        return self._request("GET", "/chat/api/me/channels.json")

    def send_chat_message(self, channel_id: int, message: str) -> Dict[str, Any]:
        payload = {"message": message}
        return self._request("POST", f"/chat/{channel_id}.json", json_data=payload)

    def create_dm_channel(self, usernames: List[str]) -> Dict[str, Any]:
        params = {"usernames": ",".join(usernames)}
        return self._request("GET", "/chat/direct_messages.json", params=params)

    def delete_topic(self, topic_id: int) -> Dict[str, Any]:
        return self._request("DELETE", f"/t/{topic_id}.json")

    def delete_post(self, post_id: int) -> Dict[str, Any]:
        return self._request("DELETE", f"/posts/{post_id}.json")
