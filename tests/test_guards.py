"""
WHY: To verify that the 'Immune System' and 'Genesis Purity' rules are strictly enforced.
WHAT: Tests for @username blocking, character limits, and placeholder detection.
HOW: Mocks BithubComms; follows Guard -> Do -> Verify to ensure rules trigger correctly.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from bithub.bithub_comms import BithubComms
from bithub.bithub_errors import BithubError

@pytest.fixture
def comms():
    with patch.dict('os.environ', {"BITHUB_USER_API_KEY": "test_key"}):
        return BithubComms()

def test_genesis_purity_guard(comms):
    """Guard: Block @tags in Core categories (ID >= 54). Verify: Exception raised."""
    with pytest.raises(BithubError, match="Genesis Purity Violation"):
        comms._validate_genesis_purity("Hello @agent", 55)

def test_post_completion_guard(comms):
    """Guard: Block @tags if topic has < 5 posts. Verify: Exception raised."""
    with patch.object(comms, 'get_topic_posts', return_value={"post_stream": {"posts": [{}, {}]}}):
        with pytest.raises(BithubError, match="Post-Completion Rule"):
            comms.reply_to_post(topic_id=123, raw="Check this @user")

def test_character_limit(comms):
    """Guard: Content > 32000 chars. Verify: BithubError."""
    with pytest.raises(BithubError, match="Content too long"):
        comms._validate_content("A" * 32001)

def test_placeholder_curly_braces(comms):
    """Guard: Unresolved {{ }}. Verify: BithubError."""
    with pytest.raises(BithubError, match="Unresolved placeholders"):
        comms._validate_content("Hello {{name}}")

def test_placeholder_section_sign(comms):
    """Guard: Unresolved §§. Verify: BithubError."""
    with pytest.raises(BithubError, match="Unresolved placeholders"):
        comms._validate_content("Hello §§secret")

def test_registry_validation(comms):
    """Guard: Invalid category_id. Verify: BithubError."""
    from bithub.bithub_cores import BithubCores
    cores = BithubCores()
    with patch("builtins.open", patch("builtins.open", create=True)) as mock_file:
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps([{"id": 55}])
        with pytest.raises(BithubError, match="Invalid category_id: 99"):
            cores._validate_category(99)
