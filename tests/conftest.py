"""
Title: conftest.py Test
Description: Test suite for conftest.
"""

import pytest
import os
from unittest.mock import MagicMock, patch
from bithub.bithub_comms import BithubComms
from bithub.bithub_cores import BithubCores
from bithub.bithub_errors import BithubError

@pytest.fixture
def mock_comms():
    return MagicMock(spec=BithubComms)

@pytest.fixture
def mock_cores():
    return MagicMock(spec=BithubCores)
