import pytest
from unittest.mock import patch, MagicMock
from core.ftp_try_login import ftp_try_login


@pytest.mark.parametrize("login_success", [True, False])
def test_ftp_try_login(monkeypatch, login_success):
    """
    Test ftp_try_login behavior for successful and failed FTP authentications.

    This test uses mocking to avoid any real network I/O.

    Scenarios:
    - Success: ftp.login() does not raise -> function returns the tested password.
    - Failure: ftp.login() raises ftplib.error_perm -> function returns None.

    The FTP class is patched so connect() and login() calls are intercepted
    and their invocation is asserted.
    """
    mock_ftp_instance = MagicMock()

    if not login_success:
        from ftplib import error_perm
        mock_ftp_instance.login.side_effect = error_perm("530 Login incorrect.")

    with patch("core.ftp_try_login.FTP", return_value=mock_ftp_instance):
        if login_success:
            result = ftp_try_login("127.0.0.1", "user", "pass")
            assert result == "pass"
            mock_ftp_instance.connect.assert_called_once()
            mock_ftp_instance.login.assert_called_once_with(user="user", passwd="pass")
            mock_ftp_instance.quit.assert_called_once()
        else:
            result = ftp_try_login("127.0.0.1", "user", "wrongpass")
            assert result is None
            mock_ftp_instance.connect.assert_called_once()
            mock_ftp_instance.login.assert_called_once()
            mock_ftp_instance.quit.assert_not_called()
