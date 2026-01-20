print("DEBUG: Script started")
"""
Title: fetch_core_data.py Script
Description: CLI script to sync Core definitions from BIThub.
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bithub.bithub_cores import BithubCores
# BithubComms import is not strictly needed if we just use BithubCores

def fetch_core_data():
    load_dotenv()
    
    # Initialize Cores manager
    # BithubCores inherits from BithubComms, so we just instantiate it directly
    cores = BithubCores()
    
    print("--- SYNCING CORES ---")
    try:
        results = cores.sync_cores()
        print(f"Successfully synced {len(results)} cores.")
        for core in results:
            print(f"- [{core['id']}] {core['name']} ({core['slug']})")
            
    except Exception as e:
        print(f"Error syncing cores: {e}")

if __name__ == "__main__":
    fetch_core_data()
