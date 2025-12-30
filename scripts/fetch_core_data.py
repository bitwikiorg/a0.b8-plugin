"""
Title: fetch_core_data.py Script
Description: Script for fetch_core_data.
"""


import sys
import os
import json
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bithub.bithub_comms import BithubComms

def fetch_core_data():
    load_dotenv()
    comms = BithubComms()

    print("--- CATEGORIES (Recursive) ---")
    try:
        resp = comms._request("GET", "/categories.json?include_subcategories=true")
        categories = resp.get('category_list', {}).get('categories', [])

        def print_cat(cat, level=0):
            indent = "  " * level
            print(f"{cat['id']:<5} | {indent}{cat['name']} ({cat['slug']})")
            for sub in cat.get('subcategory_list', []):
                print_cat(sub, level + 1)

        for cat in categories:
            print_cat(cat)

    except Exception as e:
        print(f"Error fetching categories: {e}")

    print("
--- BOTS (Registry) ---")
    # Assuming registry file exists or fetching from topic if needed
    # For now, just listing what we know or fetching from API if possible (Discourse doesn't list 'bots' easily without admin)
    # We'll stick to categories for now as that was the critical error.

if __name__ == "__main__":
    fetch_core_data()
