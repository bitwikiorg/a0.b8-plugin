"""
Why: Provides a unified CLI entry point for the Bithub system.
What: Orchestrates subcommands for agents, cores, chat, and registry.
How: Uses argparse to dispatch commands to specific handler functions.
"""

import argparse
import json
import sys

from dotenv import load_dotenv

from .bithub_comms import BithubComms
from .bithub_cores import BithubCores
from .bithub_config import DEFAULT_TIMEOUT
from .bithub_errors import BithubError, BithubAuthError, BithubNetworkError, BithubRateLimitError
from .bithub_logging import configure_logging
from .bithub_registry import cmd_list, cmd_refresh


def handle_agent(args: argparse.Namespace) -> None:
    """Handle the 'agent' subcommand: Send PM and wait for reply.

    Sends a private message to a specified bot and waits for a response.
    Prints the sanitized response content or error details to stdout.

    Args:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - bot_username (str): The target bot's username.
            - message (str): The message content to send.
            - timeout (int): Timeout in seconds for waiting for a reply.
    """
    try:
        comms = BithubComms()
        title = f"Task: {args.message[:30]}..."
        resp = comms.send_private_message([args.bot_username], title, args.message)

        topic_id = resp['topic_id']
        my_post_id = resp['id']

        reply = comms.wait_for_reply(topic_id, my_post_id, timeout=args.timeout)

        if reply:
            content = reply.get('cooked', '') or reply.get('raw', '')
            clean_text = comms.sanitize_html(content)
            print(clean_text)
        else:
            sys.exit(1)

    except BithubAuthError as e:
        print(json.dumps({"status": "error", "type": "AuthError", "message": str(e)}))
        sys.exit(1)
    except BithubRateLimitError as e:
        print(json.dumps({"status": "error", "type": "RateLimitError", "message": str(e)}))
        sys.exit(1)
    except BithubNetworkError as e:
        print(json.dumps({"status": "error", "type": "NetworkError", "message": str(e)}))
        sys.exit(1)
    except BithubError as e:
        print(json.dumps({"status": "error", "type": "BithubError", "message": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def handle_core(args: argparse.Namespace) -> None:
    """Handle the 'core' subcommand: Deploy workflows or watch topics.

    Supports deploying core workflows or watching existing topics for updates.

    Args:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - subcommand (str): 'deploy' or 'watch'.
            - title (str, optional): Title for deployment.
            - content (str, optional): Content for deployment.
            - category (int, optional): Category ID for deployment.
            - topic_id (int, optional): Topic ID to watch.
            - last_post_id (int, optional): Last known post ID for watching.
            - timeout (int, optional): Timeout in seconds.
    """
    try:
        cores = BithubCores()

        if args.subcommand == 'deploy':
            result = cores.deploy_only(
                title=args.title,
                content=args.content,
                category_id=args.category,
                tags=[]
            )
            print(json.dumps(result))

        elif args.subcommand == 'watch':
            last_post_id = getattr(args, 'last_post_id', 0)
            result = cores.watch_topic(
                topic_id=args.topic_id,
                last_post_id=last_post_id,
                timeout=args.timeout
            )

            if result:
                clean_text = cores.sanitize_html(result.get('cooked', '') or result.get('raw', ''))
                print(clean_text)
            else:
                sys.exit(1)

    except BithubAuthError as e:
        print(json.dumps({"status": "error", "type": "AuthError", "message": str(e)}))
        sys.exit(1)
    except BithubRateLimitError as e:
        print(json.dumps({"status": "error", "type": "RateLimitError", "message": str(e)}))
        sys.exit(1)
    except BithubNetworkError as e:
        print(json.dumps({"status": "error", "type": "NetworkError", "message": str(e)}))
        sys.exit(1)
    except BithubError as e:
        print(json.dumps({"status": "error", "type": "BithubError", "message": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def handle_chat(args: argparse.Namespace) -> None:
    """Handle the 'chat' subcommand: Realtime chat.

    Currently supports sending messages to a specific channel.

    Args:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - subcommand (str): 'send'.
            - channel_id (int): The target channel ID.
            - message (str): The message content to send.
    """
    try:
        comms = BithubComms()
        if args.subcommand == 'send':
            resp = comms.send_chat_message(args.channel_id, args.message)
            print(json.dumps({"status": "success", "response": resp}))

    except BithubAuthError as e:
        print(json.dumps({"status": "error", "type": "AuthError", "message": str(e)}))
        sys.exit(1)
    except BithubRateLimitError as e:
        print(json.dumps({"status": "error", "type": "RateLimitError", "message": str(e)}))
        sys.exit(1)
    except BithubNetworkError as e:
        print(json.dumps({"status": "error", "type": "NetworkError", "message": str(e)}))
        sys.exit(1)
    except BithubError as e:
        print(json.dumps({"status": "error", "type": "BithubError", "message": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def handle_registry(args: argparse.Namespace) -> None:
    """Handle the 'registry' subcommand.

    Manages the bot registry, allowing listing and refreshing of available bots.

    Args:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - subcommand (str): 'list' or 'refresh'.
    """
    try:
        comms = BithubComms()
        if args.subcommand == 'refresh':
            cmd_refresh(args, comms)
        elif args.subcommand == 'list':
            cmd_list(args, comms)

    except BithubAuthError as e:
        print(json.dumps({"status": "error", "type": "AuthError", "message": str(e)}))
        sys.exit(1)
    except BithubRateLimitError as e:
        print(json.dumps({"status": "error", "type": "RateLimitError", "message": str(e)}))
        sys.exit(1)
    except BithubNetworkError as e:
        print(json.dumps({"status": "error", "type": "NetworkError", "message": str(e)}))
        sys.exit(1)
    except BithubError as e:
        print(json.dumps({"status": "error", "type": "BithubError", "message": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def handle_notifications(args: argparse.Namespace) -> None:
    """Handle the 'notifications' subcommand.

    Checks for recent notifications.

    Args:
        args (argparse.Namespace): Parsed command-line arguments containing:
            - subcommand (str): 'check'.
            - limit (int): The maximum number of notifications to retrieve.
    """
    try:
        comms = BithubComms()
        if args.subcommand == 'check':
            resp = comms.get_notifications(limit=args.limit)
            if isinstance(resp, dict) and 'notifications' in resp:
                print(json.dumps(resp['notifications']))
            else:
                print(json.dumps(resp))

    except BithubAuthError as e:
        print(json.dumps({"status": "error", "type": "AuthError", "message": str(e)}))
        sys.exit(1)
    except BithubRateLimitError as e:
        print(json.dumps({"status": "error", "type": "RateLimitError", "message": str(e)}))
        sys.exit(1)
    except BithubNetworkError as e:
        print(json.dumps({"status": "error", "type": "NetworkError", "message": str(e)}))
        sys.exit(1)
    except BithubError as e:
        print(json.dumps({"status": "error", "type": "BithubError", "message": str(e)}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)



def handle_reply(args: argparse.Namespace) -> None:
    """Handle the 'reply' subcommand: Reply to an existing topic."""
    try:
        comms = BithubComms()
        resp = comms.reply_to_post(args.topic_id, args.message)
        my_post_id = resp['id']
        reply = comms.wait_for_reply(args.topic_id, my_post_id, timeout=args.timeout)
        if reply:
            content = reply.get('cooked', '') or reply.get('raw', '')
            print(comms.sanitize_html(content))
        else:
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


def main() -> None:
    """Main entry point for the Bithub CLI.

    Parses command-line arguments and dispatches control to the appropriate
    handler function based on the subcommand provided.
    """
    configure_logging()
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(description="Bithub Unified CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Agent Command
    p_agent = subparsers.add_parser("agent", help="Interact with a bot")
    p_agent.add_argument("bot_username", help="Target bot username (e.g., @discobot)")
    p_agent.add_argument("message", help="Message content")
    p_agent.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    p_agent.set_defaults(func=handle_agent)

    # Reply Command
    p_reply = subparsers.add_parser("reply", help="Reply to an existing topic")
    p_reply.add_argument("topic_id", type=int, help="Target topic ID")
    p_reply.add_argument("message", help="Message content")
    p_reply.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    p_reply.set_defaults(func=handle_reply)


    # Core Command
    p_core = subparsers.add_parser("core", help="Deploy workflows")
    p_core_sub = p_core.add_subparsers(dest="subcommand", required=True)

    # Core Deploy
    p_core_deploy = p_core_sub.add_parser("deploy", help="Deploy a core workflow")
    p_core_deploy.add_argument("title", help="Topic title")
    p_core_deploy.add_argument("content", help="Topic content")
    p_core_deploy.add_argument("--category", type=int, required=True, help="Category ID")
    p_core_deploy.set_defaults(func=handle_core)

    # Core Watch
    p_core_watch = p_core_sub.add_parser("watch", help="Watch a topic for results")
    p_core_watch.add_argument("topic_id", type=int, help="Topic ID to watch")
    p_core_watch.add_argument("--last_post_id", type=int, default=0, help="ID of the last known post")
    p_core_watch.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    p_core_watch.set_defaults(func=handle_core)

    # Chat Command
    p_chat = subparsers.add_parser("chat", help="Realtime chat operations")
    p_chat_sub = p_chat.add_subparsers(dest="subcommand", required=True)
    p_chat_send = p_chat_sub.add_parser("send", help="Send a message to a channel")
    p_chat_send.add_argument("channel_id", type=int, help="Channel ID")
    p_chat_send.add_argument("message", help="Message content")
    p_chat_send.set_defaults(func=handle_chat)
    # Registry Command
    p_reg = subparsers.add_parser("registry", help="Manage bot registry")
    p_reg_sub = p_reg.add_subparsers(dest="subcommand", required=True)
    p_reg_sub.add_parser("refresh", help="Refresh registry from source")
    p_reg_sub.add_parser("list", help="List available bots")
    p_reg.set_defaults(func=handle_registry)

    # Notifications Command
    p_notif = subparsers.add_parser("notifications", help="Manage notifications")
    p_notif_sub = p_notif.add_subparsers(dest="subcommand", required=True)
    p_notif_check = p_notif_sub.add_parser("check", help="Check for notifications")
    p_notif_check.add_argument("--limit", type=int, default=30, help="Limit number of notifications")
    p_notif.set_defaults(func=handle_notifications)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
