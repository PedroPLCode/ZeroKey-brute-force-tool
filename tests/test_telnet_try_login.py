import pytest
from unittest.mock import patch, MagicMock
from core.telnet_try_login import telnet_try_login


@pytest.mark.parametrize("scenario", ["success", "failure", "unknown", "connection_error"])
def test_telnet_try_login(scenario, capsys):
    """
    Unit tests for the telnet_try_login() function.

    This test ensures the telnet_try_login function behaves correctly under different
    simulated Telnet connection scenarios without making any real network calls.

    Test Scenarios:
        1. success:
            - The response includes a known success indicator.
            - Function should return the tested password.
            - Should print a success message.

        2. failure:
            - The response includes a known failure indicator.
            - Function should return None.
            - Should print a failure message.

        3. unknown:
            - The response does not match any known success/failure indicators.
            - Function should return None.
            - Should print an 'Unknown response' message.

        4. connection_error:
            - open() raises an Exception (connection failure).
            - Function should return None.
            - Should print a connection error message.
    """

    host = "127.0.0.1"
    username = "root"
    password = "toor"

    mock_telnet = MagicMock()
    mock_telnet.read_until.return_value = b"login: "
    mock_telnet.read_very_eager.return_value = b""

    if scenario == "success":
        mock_telnet.read_very_eager.return_value = b"Welcome to system shell"
    elif scenario == "failure":
        mock_telnet.read_very_eager.return_value = b"Login incorrect"
    elif scenario == "unknown":
        mock_telnet.read_very_eager.return_value = b"Unrecognized prompt..."

    with patch("core.telnet_try_login.telnetlib.Telnet", return_value=mock_telnet), \
         patch("core.telnet_try_login.TELNET_SUCCESS_INDICATORS", ["welcome", "shell"]), \
         patch("core.telnet_try_login.TELNET_FAILURE_INDICATORS", ["incorrect", "failed"]), \
         patch("core.telnet_try_login.TELNET_SLEEP_DELAY", 0):

        if scenario == "connection_error":
            mock_telnet.open.side_effect = Exception("Connection refused")

        result = telnet_try_login(host, username, password)

        if scenario == "success":
            assert result == password
        else:
            assert result is None

        captured = capsys.readouterr().out.lower()

        if scenario == "success":
            assert "" in captured
        elif scenario == "failure":
            assert "failed" in captured
        elif scenario == "unknown":
            assert "unknown response" in captured
        elif scenario == "connection_error":
            assert "could not connect" in captured

        mock_telnet.close.assert_called()
