import pytest
from unittest.mock import Mock, patch
from notebookbot.authentication.authentication_setup import (
    try_authenticate,
    get_existing_keys,
    get_api_key_choice,
)
from notebookbot.authentication.authentication_manager import AuthenticationManager

@pytest.fixture
def mock_auth_manager():
    auth_manager = Mock(spec=AuthenticationManager)
    auth_manager.is_authenticated = False
    auth_manager.api_interface = Mock()
    auth_manager.api_interface.encryption_manager = Mock()
    return auth_manager

def test_try_authenticate_success(mock_auth_manager):
    """Test successful authentication within first try."""
    def auth_success():
        mock_auth_manager.is_authenticated = True
    
    mock_auth_manager.setup_or_authenticate = Mock(side_effect=auth_success)
    
    result = try_authenticate(mock_auth_manager)
    
    assert result is True
    mock_auth_manager.setup_or_authenticate.assert_called_once()

def test_try_authenticate_after_failures(mock_auth_manager):
    """Test authentication failing after three attempts."""
    # Always return False for is_authenticated
    mock_auth_manager.setup_or_authenticate = Mock()
    mock_auth_manager.is_authenticated = False
    
    result = try_authenticate(mock_auth_manager)
    
    assert result is False
    assert mock_auth_manager.setup_or_authenticate.call_count == 3

def test_get_existing_keys_with_keys(mock_auth_manager):
    """Test getting existing keys when some exist."""
    expected_keys = {"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}
    mock_auth_manager.api_interface.encryption_manager.list_keys.return_value = expected_keys
    
    result = get_existing_keys(mock_auth_manager)
    
    assert result == expected_keys
    mock_auth_manager.api_interface.encryption_manager.list_keys.assert_called_once()

def test_get_existing_keys_no_keys(mock_auth_manager):
    """Test getting existing keys when none exist."""
    mock_auth_manager.api_interface.encryption_manager.list_keys.return_value = set()
    
    result = get_existing_keys(mock_auth_manager)
    
    assert result == set()
    mock_auth_manager.api_interface.encryption_manager.list_keys.assert_called_once()

@pytest.mark.parametrize("choice,remaining,expected", [
    ("1", {"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}, "OPENAI_API_KEY"),
    ("2", {"OPENAI_API_KEY", "ANTHROPIC_API_KEY"}, "ANTHROPIC_API_KEY"),
    ("openai", {"OPENAI_API_KEY"}, "OPENAI_API_KEY"),
    ("anthropic", {"ANTHROPIC_API_KEY"}, "ANTHROPIC_API_KEY"),
    ("no", {"OPENAI_API_KEY"}, None),
])
def test_get_api_key_choice(choice, remaining, expected):
    """Test various API key choice inputs."""
    with patch('builtins.input', return_value=choice):
        result = get_api_key_choice(remaining)
        assert result == expected

if __name__ == "__main__":
    pytest.main()
