"""
Title: fetch_topology.py Script
Description: Script for fetch_topology.
"""


import sys
import os
import json
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bithub.bithub_comms import BithubComms

def fetch_topology():
    load_dotenv()
    comms = BithubComms()

    print("--- CATEGORIES ---")
    try:
        resp = comms._request("GET", "/categories.json")
        categories = resp.get('category_list', {}).get('categories', [])
        for cat in categories:
            print(f"{cat['id']:<5} | {cat['name']}")
    except Exception as e:
        print(f"Error fetching categories: {e}")

    print("
--- CHAT CHANNELS ---")
    try:
        resp = comms.get_chat_channels()
        channels = resp.get('public_channels', [])
        for c in channels:
            print(f"{c['id']:<5} | {c['title']}")
    except Exception as e:
        print(f"Error fetching channels: {e}")

if __name__ == "__main__":
    fetch_topology()
