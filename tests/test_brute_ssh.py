import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from core.brute_ssh import ssh_bruteforce
import paramiko


@pytest.fixture
def mock_open_passwords(tmp_path: Path):
    """Mock the opening of the passwords file.

    Keyword arguments:
    tmp_path -- The temporary directory path for the test.
    Return: The path to the mock passwords file.
    """
    
    wordlist = tmp_path / "passwords.txt"
    wordlist.write_text("wrongpass\ncorrectpass\nanotherwrong\n")
    return str(wordlist)


@patch("paramiko.SSHClient")
def test_ssh_bruteforce_success(
    mock_ssh_client_class: MagicMock, mock_open_passwords: str
):
    """Test the SSH brute-force function for successful authentication.

    Args:
        mock_ssh_client_class (MagicMock): Mocked SSH client class.
        mock_open_passwords (str): Path to the mock passwords file.

    Raises:
        paramiko.AuthenticationException: If authentication fails.
        paramiko.SSHException: For other SSH-related exceptions.

    Returns:
        _type_: The password if found, else None.
    """
    mock_client_instance = MagicMock()
    mock_ssh_client_class.return_value = mock_client_instance

    def connect_side_effect(**kwargs: object) -> None:
        if kwargs.get("password") == "correctpass":
            return None
        else:
            raise paramiko.AuthenticationException()

    mock_client_instance.connect.side_effect = connect_side_effect
    mock_client_instance.set_missing_host_key_policy.return_value = None
    mock_client_instance.close.return_value = None

    result = ssh_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result == "correctpass"


@patch("paramiko.SSHClient")
def test_ssh_bruteforce_fail(
    mock_ssh_client_class: MagicMock, mock_open_passwords: str
):
    """Test the SSH brute-force function for failed authentication.

    Args:
        mock_ssh_client_class (MagicMock): Mocked SSH client class.
        mock_open_passwords (str): Path to the mock passwords file.
    """
    mock_client_instance = MagicMock()
    mock_ssh_client_class.return_value = mock_client_instance

    mock_client_instance.connect.side_effect = paramiko.AuthenticationException()
    mock_client_instance.set_missing_host_key_policy.return_value = None
    mock_client_instance.close.return_value = None

    result = ssh_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None


@patch("paramiko.SSHClient")
def test_ssh_bruteforce_other_ssh_exception(
    mock_ssh_client_class: MagicMock, mock_open_passwords: str
):
    """Test the SSH brute-force function for other SSH-related exceptions.

    Args:
        mock_ssh_client_class (MagicMock): Mocked SSH client class.
        mock_open_passwords (str): Path to the mock passwords file.
    """
    mock_client_instance = MagicMock()
    mock_ssh_client_class.return_value = mock_client_instance

    mock_client_instance.connect.side_effect = paramiko.SSHException()
    mock_client_instance.set_missing_host_key_policy.return_value = None
    mock_client_instance.close.return_value = None

    result = ssh_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None
