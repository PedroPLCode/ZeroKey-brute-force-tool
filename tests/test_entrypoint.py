import pytest
import sys
from unittest.mock import patch
from typing import Generator, Any
from entrypoint import entrypoint


@pytest.fixture
def mock_services_and_brute() -> Generator[dict[str, Any], None, None]:
    """Mock the service detection and brute-force functions.

    Yields:
        Generator[dict[str, Any], None, None]: Mocked functions and their return values.
    """
    with patch("core.brute_ssh.ssh_bruteforce") as mock_ssh, patch(
        "core.brute_ftp.ftp_bruteforce"
    ) as mock_ftp, patch("core.brute_mysql.mysql_bruteforce") as mock_mysql, patch(
        "core.brute_postgres.postgres_bruteforce"
    ) as mock_pg, patch(
        "entrypoint.detect_services"
    ) as mock_detect, patch(
        "entrypoint.save_to_json"
    ) as mock_save, patch(
        "entrypoint.log_result"
    ) as mock_log, patch(
        "entrypoint.BRUTEFORCE_FUNCS",
        {
            "ssh": (mock_ssh, 22, 3, 0.5),
            "ftp": (mock_ftp, 21, 3, 0.5),
            "telnet": (mock_ftp, 21, 3, 0.5),
            "mysql": (mock_mysql, 3306, 3, 0.5),
            "postgres": (mock_pg, 5432, 3, 0.5),
        },
    ) as mock_funcs:

        mock_ssh.return_value = "sshpass"
        mock_ftp.return_value = "ftppass"
        mock_mysql.return_value = "mysqlpass"
        mock_pg.return_value = "pgpass"

        mock_detect.return_value = ["ssh"]

        yield {
            "detect": mock_detect,
            "ssh": mock_ssh,
            "ftp": mock_ftp,
            "mysql": mock_mysql,
            "pg": mock_pg,
            "save": mock_save,
            "log": mock_log,
            "funcs": mock_funcs,
        }


def run_entrypoint_with_args(args_list: list[str]) -> None:
    """Run the entrypoint with the given command-line arguments.

    Args:
        args_list (list[str]): List of command-line arguments.
    """
    test_args: list[str] = ["entrypoint.py"] + args_list
    with patch.object(sys, "argv", test_args):
        entrypoint()


def test_entrypoint_unknown_service_skips(mock_services_and_brute: dict[str, Any]):
    """Test the entrypoint with an unknown service.

    Args:
        mock_services_and_brute (dict[str, Any]): Mocked functions and their return values.
    """
    mock_services_and_brute["detect"].return_value = ["unknown"]

    run_entrypoint_with_args(
        ["127.0.0.1", "user", "passwords.txt", "--protocol", "auto"]
    )

    mock_services_and_brute["save"].assert_called_once()


def test_entrypoint_no_services_detected(mock_services_and_brute: dict[str, Any]):
    """Test the entrypoint when no services are detected.

    Args:
        mock_services_and_brute (dict[str, Any]): Mocked functions and their return values.
    """
    mock_services_and_brute["detect"].return_value = []

    run_entrypoint_with_args(
        ["127.0.0.1", "user", "passwords.txt", "--protocol", "auto"]
    )

    mock_services_and_brute["ssh"].assert_not_called()
    mock_services_and_brute["save"].assert_not_called()
