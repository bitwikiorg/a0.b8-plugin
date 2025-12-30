"""
Why: Facilitates interactive, low-latency communication.
What: Provides a terminal-based chat interface for channels.
How: Implements a poll-print-input loop for realtime interaction.
"""

import sys
from typing import Any, Dict, List, Union

from .bithub_comms import BithubComms


def list_channels(comms: BithubComms) -> List[Dict[str, Any]]:
    """Fetches and lists available chat channels.

    Args:
        comms: An initialized BithubComms instance.

    Returns:
        A list of dictionaries representing the available channels.
    """
    print("[System] Fetching channels...")
    resp = comms.get_chat_channels()
    channels = resp.get("public_channels", []) + resp.get("direct_message_channels", [])

    print(f"\n{'ID':<5} | {'Name/Title':<30}")
    print("-" * 40)
    for c in channels:
        c_id = c.get("id")
        title = c.get("title") or c.get("name") or "Unknown"
        # Handle DM users list if title is missing
        if not title and "users" in c:
            title = ", ".join([u["username"] for u in c["users"]])
        print(f"{c_id:<5} | {title:<30}")
    return channels


def realtime_session(channel_id: Union[str, int]) -> None:
    """Starts a realtime chat session for a specific channel.

    Args:
        channel_id: The ID of the channel to join.
    """
    try:
        comms = BithubComms()
    except Exception as e:
        print(f"[Fatal] {e}")
        return

    print(f"[System] Joining Chat Channel {channel_id}...")
    print("[Instructions] Type message and hit ENTER. Type /exit to quit.")

    last_msg_id = 0

    # Initial fetch
    msgs = comms.get_chat_messages(channel_id)
    for m in reversed(msgs.get("messages", [])):
        user = m.get("user", {}).get("username", "Unknown")
        txt = m.get("message", "")
        print(f"[{user}] {txt}")
        last_msg_id = m.get("id", last_msg_id)

    while True:
        try:
            user_input = input("\n(You) > ")
            if user_input.strip() == "/exit":
                break
            if user_input.strip():
                comms.send_chat_message(channel_id, user_input)

            # Poll for new
            updates = comms.get_chat_messages(channel_id)
            for m in reversed(updates.get("messages", [])):
                if m.get("id") > last_msg_id:
                    user = m.get("user", {}).get("username", "Unknown")
                    txt = m.get("message", "")
                    print(f"\n[{user}] {txt}")
                    last_msg_id = m.get("id")

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python bithub_chat_realtime.py <channel_id> OR 'list'")
        sys.exit(1)

    if sys.argv[1] == "list":
        list_channels(BithubComms())
    else:
        realtime_session(sys.argv[1])
