import pytest
from unittest.mock import patch, MagicMock
import paramiko
from core.ssh_try_login import ssh_try_login


@pytest.mark.parametrize("case", ["success", "auth_error", "generic_error"])
def test_ssh_try_login(case):
    """
    Test ssh_try_login behavior for different connection outcomes.

    Scenarios:
    ----------
    1. success:
        - `paramiko.SSHClient.connect` succeeds.
        - Function returns the tested password string.
        - The SSH client is closed after use.

    2. auth_error:
        - `paramiko.SSHClient.connect` raises AuthenticationException.
        - Function returns None and prints failure message.
        - The SSH client is closed after exception.

    3. generic_error:
        - `paramiko.SSHClient.connect` raises another Exception.
        - Function returns None and still closes client.

    Notes:
        - All tests mock `paramiko.SSHClient` and its methods so that
          no real SSH connection or network traffic is performed.
        - `clear_line()` side effects are ignored (we only test logic).
    """
    host = "127.0.0.1"
    username = "root"
    password = "toor"
    port = 22
    timeout = 3

    mock_client = MagicMock()

    with patch("core.ssh_try_login.paramiko.SSHClient", return_value=mock_client):
        if case == "success":
            result = ssh_try_login(host, username, password, port=port, timeout=timeout)
            assert result == password
            mock_client.connect.assert_called_once_with(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
            )
            mock_client.close.assert_called_once()

        elif case == "auth_error":
            mock_client.connect.side_effect = paramiko.AuthenticationException("Auth failed")
            result = ssh_try_login(host, username, password, port=port, timeout=timeout)
            assert result is None
            mock_client.close.assert_called_once()

        elif case == "generic_error":
            mock_client.connect.side_effect = Exception("Network unreachable")
            result = ssh_try_login(host, username, password, port=port, timeout=timeout)
            assert result is None
            mock_client.close.assert_called_once()
