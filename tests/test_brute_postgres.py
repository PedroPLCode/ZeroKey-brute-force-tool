import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from pathlib import Path
from core.brute_postgres import postgres_bruteforce


@pytest.fixture
def mock_open_passwords(tmp_path: Path):
    wordlist = tmp_path / "passwords.txt"
    wordlist.write_text("wrongpass\ncorrectpass\nanotherwrong\n")
    return str(wordlist)
    return str(wordlist)


@patch("psycopg2.connect")
def test_postgres_bruteforce_success(mock_connect: MagicMock, mock_open_passwords: str):
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    def side_effect(**kwargs: object) -> object:
        if kwargs.get("password") == "correctpass":
            return mock_conn
        else:
            raise psycopg2.OperationalError("Access denied")

    mock_connect.side_effect = side_effect

    result = postgres_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result == "correctpass"
    mock_conn.close.assert_called_once()


@patch("psycopg2.connect")
def test_postgres_bruteforce_fail(mock_connect: MagicMock, mock_open_passwords: str):
    mock_connect.side_effect = psycopg2.OperationalError("Access denied")

    result = postgres_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None


@patch("psycopg2.connect")
def test_postgres_bruteforce_other_exception(
    mock_connect: MagicMock, mock_open_passwords: str
):
    mock_connect.side_effect = Exception("Connection error")

    result = postgres_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None
