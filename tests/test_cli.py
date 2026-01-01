"""
WHY: To verify the command-line interface for registry management.
WHAT: Tests for the 'list' command.
HOW: Mocks BithubComms and argparse; follows Guard -> Do -> Verify.
"""

import pytest
import json
import os
from unittest.mock import patch, MagicMock, mock_open
from bithub.bithub_registry import cmd_list

def test_registry_cli_list():
    """Do: Execute list command. Verify: Registry file is read and printed."""
    registry_data = json.dumps([{"username": "bot1", "name": "Bot One"}])
    with patch("os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=registry_data)), \
         patch("builtins.print") as mock_print:
        cmd_list(MagicMock(), None)
        mock_print.assert_any_call("- @bot1 (Bot One) [UNKNOWN]")
