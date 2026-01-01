"""
WHY: To maintain a local directory of swarm identities (Neurons).
WHAT: Syncs with a remote Bithub topic to parse agent metadata into a JSON registry.
HOW: Parses Markdown tables; follows Guard -> Do -> Verify for file I/O and API calls.
"""

import os
import json
import argparse
from typing import List, Dict, Any, Optional
from .bithub_comms import BithubComms
from .bithub_config import REGISTRY_FILE

def parse_markdown_table(markdown: str) -> List[Dict[str, Any]]:
    bots = []
    lines = markdown.splitlines()
    current_section = None

    for line in lines:
        if "## 👥 Active Personas" in line: current_section = "persona"
        elif "## 🧠 Available LLMs" in line: current_section = "llm"
        elif line.strip().startswith("|") and "---" not in line and "Name" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3:
                bots.append({
                    "type": current_section or "unknown",
                    "username": parts[2].replace("`", "").replace("@", ""),
                    "name": parts[1].replace("**", "")
                })
    return bots

def refresh_registry(comms: BithubComms) -> int:
    # Guard: Fetch source topic
    topic_id = 30145
    topic = comms.get_topic_posts(topic_id)
    posts = topic.get('post_stream', {}).get('posts', [])
    if not posts: return 0

    # Do: Parse content
    post = comms.get_post(posts[0]['id'])
    new_registry = parse_markdown_table(post.get('raw', ''))

    # Verify: Save to file
    if new_registry:
        with open(REGISTRY_FILE, 'w') as f:
            json.dump(new_registry, f, indent=2)
    return len(new_registry)

def cmd_list(args: argparse.Namespace, comms: Optional[BithubComms]) -> None:
    """Do: List local registry. Verify: File exists and content is printed."""
    registry_file = REGISTRY_FILE
    if not os.path.exists(registry_file):
        print("Registry not found. Run refresh.")
        return

    with open(registry_file, 'r') as f:
        data = json.load(f)

    print(f"[Total] {len(data)} bots available.")
    for b in data:
        print(f"- @{b['username']} ({b['name']}) [{b.get('type', 'unknown').upper()}]")
