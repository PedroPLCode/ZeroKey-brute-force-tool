import pytest
from unittest.mock import patch, MagicMock
import pymysql
from core.mysql_try_login import mysql_try_login


@pytest.mark.parametrize("case", ["success", "operational_error", "other_exception"])
def test_mysql_try_login(case):
    """
    Test mysql_try_login for three scenarios using mocking:

    - success: pymysql.connect() returns a connection -> function returns the password and closes the connection.
    - operational_error: pymysql.connect() raises pymysql.err.OperationalError -> function returns None.
    - other_exception: pymysql.connect() raises a generic Exception -> function returns None.

    The test patches `pymysql.connect` in the module under test so no real DB connection
    is attempted. It also asserts that connect() and close() are called when appropriate.
    """
    host = "127.0.0.1"
    username = "user"
    password = "secret"
    port = 3306
    timeout = 3

    if case == "success":
        mock_conn = MagicMock()
        with patch("core.mysql_try_login.pymysql.connect", return_value=mock_conn) as mock_connect:
            result = mysql_try_login(host, username, password, port=port, timeout=timeout)
            assert result == password
            mock_connect.assert_called_once_with(
                host=host,
                user=username,
                password=password,
                port=port,
                connect_timeout=timeout,
            )
            mock_conn.close.assert_called_once()

    elif case == "operational_error":
        with patch("core.mysql_try_login.pymysql.connect", side_effect=pymysql.err.OperationalError("error")) as mock_connect:
            result = mysql_try_login(host, username, password, port=port, timeout=timeout)
            assert result is None
            mock_connect.assert_called_once()

    elif case == "other_exception":
        with patch("core.mysql_try_login.pymysql.connect", side_effect=Exception("network")) as mock_connect:
            result = mysql_try_login(host, username, password, port=port, timeout=timeout)
            assert result is None
            mock_connect.assert_called_once()
