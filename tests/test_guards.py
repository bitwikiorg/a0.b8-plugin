
import pytest
import os
from bithub.bithub_comms import BithubComms
from bithub.bithub_errors import BithubError

@pytest.fixture
def comms():
    os.environ['BITHUB_USER_API_KEY'] = 'test_key'
    return BithubComms()

def test_character_limit(comms):
    long_content = 'a' * 32001
    with pytest.raises(BithubError, match='Content exceeds character limit'):
        comms._validate_content(long_content)

def test_placeholder_section_sign(comms):
    content = 'Hello §§include(/path/to/file)'
    with pytest.raises(BithubError, match='Content contains unresolved framework placeholders'):
        comms._validate_content(content)

def test_placeholder_curly_braces(comms):
    content = 'Hello {{variable}}'
    with pytest.raises(BithubError, match='Content contains unresolved framework placeholders'):
        comms._validate_content(content)

def test_valid_content(comms):
    content = 'This is a valid message.'
    comms._validate_content(content) # Should not raise
