import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import pymysql
from core.brute_mysql import mysql_bruteforce


@pytest.fixture
def mock_open_passwords(tmp_path: Path):
    """Mock the opening of the passwords file.

    Args:
        tmp_path (Path): The temporary directory path for the test.

    Returns:
        str: The path to the mock passwords file.
    """
    wordlist = tmp_path / "passwords.txt"
    wordlist.write_text("wrongpass\ncorrectpass\nanotherwrong\n")
    return str(wordlist)


@patch("pymysql.connect")
def test_mysql_bruteforce_success(mock_connect: MagicMock, mock_open_passwords: str):
    """
    Test the MySQL brute-force function for successful authentication.
    Args:
        mock_connect (MagicMock): Mocked MySQL connection.
        mock_open_passwords (str): Path to the mock passwords file.
    Returns:
        str: The password if found, else None.
    """
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    def side_effect(**kwargs: object) -> object:
        if kwargs.get("password") == "correctpass":
            return mock_conn
        else:
            raise pymysql.err.OperationalError("Access denied")

    mock_connect.side_effect = side_effect

    result = mysql_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result == "correctpass"
    mock_conn.close.assert_called_once()


@patch("pymysql.connect")
def test_mysql_bruteforce_fail(mock_connect: MagicMock, mock_open_passwords: str):
    """Test the MySQL brute-force function for failed authentication.

    Args:
        mock_connect (MagicMock): Mocked MySQL connection.
        mock_open_passwords (str): Path to the mock passwords file.
    """
    mock_connect.side_effect = pymysql.err.OperationalError("Access denied")

    result = mysql_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None


@patch("pymysql.connect")
def test_mysql_bruteforce_other_exception(
    mock_connect: MagicMock, mock_open_passwords: str
):
    """Test the MySQL brute-force function for other exceptions.

    Args:
        mock_connect (MagicMock): Mocked MySQL connection.
        mock_open_passwords (str): Path to the mock passwords file.
    """
    mock_connect.side_effect = Exception("Connection error")

    result = mysql_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None
