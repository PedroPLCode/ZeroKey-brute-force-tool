import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from core.postgres_try_login import postgres_try_login
from settings import POSTGRES_DB_NAME


@pytest.mark.parametrize("case", ["success", "operational_error", "other_exception"])
def test_postgres_try_login(case):
    """
    Test postgres_try_login behavior for success, authentication failure and other errors.

    Scenarios:
    - success: psycopg2.connect() returns a connection object -> function returns password and closes connection.
    - operational_error: psycopg2.connect() raises psycopg2.OperationalError -> function returns None.
    - other_exception: psycopg2.connect() raises a generic Exception -> function returns None.

    The test patches `psycopg2.connect` in the module under test so no real network I/O occurs.
    """
    host = "127.0.0.1"
    username = "testuser"
    password = "secret"
    port = 5432
    timeout = 3
    dbname = POSTGRES_DB_NAME

    if case == "success":
        mock_conn = MagicMock()
        with patch("core.postgres_try_login.psycopg2.connect", return_value=mock_conn) as mock_connect:
            result = postgres_try_login(host, username, password, port=port, timeout=timeout)
            assert result == password
            mock_connect.assert_called_once_with(
                host=host,
                user=username,
                password=password,
                port=port,
                dbname=dbname,
                connect_timeout=timeout,
            )
            mock_conn.close.assert_called_once()

    elif case == "operational_error":
        with patch("core.postgres_try_login.psycopg2.connect", side_effect=psycopg2.OperationalError("auth failed")) as mock_connect:
            result = postgres_try_login(host, username, password, port=port, timeout=timeout)
            assert result is None
            mock_connect.assert_called_once()

    elif case == "other_exception":
        with patch("core.postgres_try_login.psycopg2.connect", side_effect=Exception("network")) as mock_connect:
            result = postgres_try_login(host, username, password, port=port, timeout=timeout)
            assert result is None
            mock_connect.assert_called_once()
