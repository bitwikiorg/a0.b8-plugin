"""
Why: Maintains a local directory of available agents and personas.
What: Syncs with a remote Discourse topic to parse bot metadata.
How: Parses Markdown tables from a source topic into a JSON registry.
"""

import os
import json
import argparse
import datetime
from typing import List, Dict, Any, Optional

from .bithub_comms import BithubComms
from .bithub_config import REGISTRY_FILE, REGISTRY_TOPIC_ID, REGISTRY_TOPIC_SLUG, REGISTRY_SOURCE_URL


def parse_markdown_table(markdown: str) -> List[Dict[str, Any]]:
    """Parses a markdown table to extract bot information.

    Args:
        markdown: The raw markdown content containing bot tables.

    Returns:
        A list of dictionaries, where each dictionary represents a bot
        and contains keys like 'type', 'id', 'name', 'username', etc.
    """
    bots = []
    lines = markdown.splitlines()
    current_section = None

    for line in lines:
        if "## 👥 Active Personas" in line:
            current_section = "persona"
        elif "## 🧠 Available LLMs" in line:
            current_section = "llm"
        elif line.strip().startswith("|") and "---" not in line and "Name" not in line and "Display Name" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if not parts:
                continue

            if current_section == "persona" and len(parts) >= 3:
                try:
                    p_id = int(parts[0])
                except ValueError:
                    p_id = None

                name = parts[1].replace("**", "")
                username = parts[2].replace("`", "").replace("@", "")
                desc = parts[-1] if len(parts) > 7 else ""

                bots.append({
                    "type": "persona",
                    "id": p_id,
                    "name": name,
                    "username": username,
                    "description": desc,
                    "provider": "BIThub"
                })

            elif current_section == "llm" and len(parts) >= 3:
                try:
                    l_id = int(parts[0])
                except ValueError:
                    l_id = None

                name = parts[1].replace("**", "")
                username = parts[2].replace("`", "").replace("@", "")
                provider = parts[3]

                bots.append({
                    "type": "llm",
                    "id": l_id,
                    "name": name,
                    "username": username,
                    "provider": provider
                })
    return bots


def cmd_refresh(args: argparse.Namespace, comms: BithubComms) -> None:
    """Refreshes the local registry from the remote source topic.

    Fetches the latest posts from the source topic, parses the markdown content,
    and updates the local JSON registry file.

    Args:
        args: The parsed command-line arguments.
        comms: An initialized BithubComms instance for API communication.
    """
    print(f"[System] Syncing Registry from Public Topic {REGISTRY_TOPIC_ID}...")

    # Use the correct endpoint format with slug to get topic data
    topic = comms.get_topic_posts(REGISTRY_TOPIC_ID, REGISTRY_TOPIC_SLUG)

    # Extract the post stream from the topic
    stream = topic.get('post_stream', {}).get('posts', [])
    if not stream:
        print("[Error] Topic has no posts.")
        return

    # Get the first post ID from the post stream
    first_post = stream[0]
    first_post_id = first_post.get('id')
    if not first_post_id:
        print("[Error] Could not get first post ID from topic data.")
        return

    print(f"First post ID: {first_post_id}")

    # Access the post directly to get its raw content
    post = comms.get_post(first_post_id)
    raw_content = post.get('raw', '')

    if not raw_content:
        print("[Error] Post content is empty.")
        return

    new_registry = parse_markdown_table(raw_content)

    if new_registry:
        with open(REGISTRY_FILE, "w") as f:
            json.dump(new_registry, f, indent=2)

        print(f"[Success] Registry updated. Found {len(new_registry)} bots.")
    else:
        print("[Error] Failed to parse bots from topic.")


def cmd_list(args: argparse.Namespace, comms: Optional[BithubComms]) -> None:
    """Lists the bots currently in the local registry.

    Args:
        args: The parsed command-line arguments.
        comms: The communication interface (unused in this command).
    """
    if not os.path.exists(REGISTRY_FILE):
        print("Registry not found. Run 'refresh'.")
        return

    with open(REGISTRY_FILE, 'r') as f:
        data = json.load(f)

    print(f"\n[Source] {REGISTRY_SOURCE_URL}")
    print(f"[Total] {len(data)} bots available.\n")

    print(f"{'ID':<5} | {'Username':<25} | {'Name':<35} | {'Type'}")
    print("-" * 80)
    for b in data:
        print(f"{str(b.get('id', 'N/A')):<5} | {b['username']:<25} | {b['name']:<35} | {b.get('type', 'unknown').upper()}")


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("list")
    subparsers.add_parser("refresh")
    args = parser.parse_args()

    if args.command == "refresh":
        comms = BithubComms()
        cmd_refresh(args, comms)
    elif args.command == "list":
        cmd_list(args, None)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()