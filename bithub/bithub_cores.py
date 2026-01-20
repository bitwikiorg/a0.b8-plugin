"""
WHY: To instantiate and monitor complex agentic workflows (Core Synapses).
WHAT: Extends BithubComms to handle genesis events and completion harvesting.
HOW: Follows Guard -> Do -> Verify; uses cores_registry.json for category validation.
"""

import json
import time
from typing import List, Optional, Dict, Any
from .bithub_comms import BithubComms
from .bithub_errors import BithubError
from .bithub_config import CORES_REGISTRY_FILE

class BithubCores(BithubComms):
    def _validate_category(self, category_id: int):
        # Guard: Validate category against registry
        try:
            with open(CORES_REGISTRY_FILE, 'r') as f:
                registry = json.load(f)
                if not any(c['id'] == category_id for c in registry):
                    raise BithubError(f"Invalid category_id: {category_id}. Not found in cores_registry.json.")
        except FileNotFoundError:
            pass

    def deploy_core(self, title: str, content: str, category_id: int) -> Dict[str, Any]:
        # Guard
        self._validate_category(category_id)

        # Do
        payload = {"title": title, "raw": content, "category": category_id}
        resp = self._request("POST", "/posts.json", json_data=payload)

        # Verify
        return {"topic_id": resp['topic_id'], "post_id": resp['id']}

    def watch_topic(self, topic_id: int, last_post_id: int, timeout: int = 60) -> Optional[Dict[str, Any]]:
        # Guard: Polling loop
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            # Do
            topic_data = self.get_topic(topic_id)
            stream = topic_data.get("post_stream", {}).get("stream", [])

            # Verify
            if stream and stream[-1] > last_post_id:
                return self.get_post(stream[-1])
            time.sleep(5)
        return None
