"""
WHY: To provide a centralized, portable configuration layer for the a0.b8 plugin.
WHAT: Defines environment-driven variables and dynamic path resolution for resources.
HOW: Uses pathlib for cross-platform path handling; resolves resources relative to the plugin root.
"""

import os
from pathlib import Path

# Plugin Root Resolution
PLUGIN_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = PLUGIN_ROOT / "resources"

# API Configuration
BITHUB_URL = os.environ.get("BITHUB_URL", "https://hub.bitwiki.org").rstrip("/")
DEFAULT_TIMEOUT = int(os.environ.get("BITHUB_TIMEOUT", "60"))

# Resource Paths (Dynamic)
REGISTRY_FILE = RESOURCES_DIR / "bot_registry.json"
CORES_REGISTRY_FILE = RESOURCES_DIR / "cores_registry.json"
TOPOLOGY_FILE = RESOURCES_DIR / "topology.json"

# Swarm Constants
CORES_CATEGORY_ID = 54
REGISTRY_TOPIC_ID = 30145
