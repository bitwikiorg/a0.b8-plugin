"""
Title: setup_env.py Script
Description: Script for setup_env.
"""


import os
import sys

def load_env():
    env_file = ".env"
    if not os.path.exists(env_file):
        print("[Init] No .env file found. Please run 'python3 bithub_auth.py' to setup.")
        return False

    print("[Init] Loading environment from .env...")
    with open(env_file, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val
    return True

if __name__ == "__main__":
    if load_env():
        print("[Init] Environment loaded. Bithub instruments ready.")
    else:
        sys.exit(1)
