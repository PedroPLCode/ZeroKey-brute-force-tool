import pytest
from unittest.mock import patch, MagicMock
from ftplib import error_perm
from core.brute_ftp import ftp_bruteforce

@pytest.fixture
def mock_open_passwords(tmp_path):
    passwords = ["wrongpass", "correctpass", "anotherwrong"]
    wordlist = tmp_path / "passwords.txt"
    wordlist.write_text("\n".join(passwords))
    return str(wordlist)

@patch("core.brute_ftp.FTP")
def test_ftp_bruteforce_success(mock_ftp_class, mock_open_passwords):
    mock_ftp_instance = MagicMock()
    mock_ftp_class.return_value = mock_ftp_instance

    def login_side_effect(user, passwd):
        if passwd == "correctpass":
            return "230 Login successful."
        else:
            raise error_perm("530 Login incorrect.")

    mock_ftp_instance.connect.return_value = None
    mock_ftp_instance.login.side_effect = login_side_effect
    mock_ftp_instance.quit.return_value = None

    result = ftp_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result == "correctpass"

@patch("ftplib.FTP")
def test_ftp_bruteforce_fail(mock_ftp_class, mock_open_passwords):
    mock_ftp_instance = MagicMock()
    mock_ftp_class.return_value = mock_ftp_instance

    mock_ftp_instance.login.side_effect = error_perm("530 Login incorrect.")
    mock_ftp_instance.connect.return_value = None
    mock_ftp_instance.quit.return_value = None

    result = ftp_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None

@patch("ftplib.FTP")
def test_ftp_bruteforce_other_exception(mock_ftp_class, mock_open_passwords):
    mock_ftp_instance = MagicMock()
    mock_ftp_class.return_value = mock_ftp_instance

    mock_ftp_instance.login.side_effect = Exception("Connection error")
    mock_ftp_instance.connect.return_value = None
    mock_ftp_instance.quit.return_value = None

    result = ftp_bruteforce("127.0.0.1", "user", mock_open_passwords)
    assert result is None