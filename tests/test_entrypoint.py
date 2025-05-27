import pytest
import sys
from unittest.mock import patch, MagicMock
from entrypoint import entrypoint


@pytest.fixture
def mock_services_and_brute():
    with patch("entrypoint.detect_services") as mock_detect, \
         patch("entrypoint.save_to_json") as mock_save, \
         patch("entrypoint.log_result") as mock_log, \
         patch("entrypoint.BRUTEFORCE_FUNCS") as mock_funcs:

        mock_ssh = MagicMock(return_value="testpass")
        mock_ftp = MagicMock()
        mock_mysql = MagicMock()
        mock_pg = MagicMock()

        mock_detect.return_value = ["ssh"]

        mock_funcs.__getitem__.side_effect = lambda proto: {
            "ssh": (mock_ssh, 22),
            "ftp": (mock_ftp, 21),
            "mysql": (mock_mysql, 3306),
            "postgres": (mock_pg, 5432),
        }[proto]

        yield {
            "detect": mock_detect,
            "ssh": mock_ssh,
            "ftp": mock_ftp,
            "mysql": mock_mysql,
            "pg": mock_pg,
            "save": mock_save,
            "log": mock_log,
        }


def run_entrypoint_with_args(args_list):
    test_args = ["entrypoint.py"] + args_list
    with patch.object(sys, "argv", test_args):
        entrypoint()


def test_entrypoint_auto_detect_success(mock_services_and_brute):
    run_entrypoint_with_args(
        ["127.0.0.1", "root", "passwords.txt", "--protocol", "auto"]
    )

    mock = mock_services_and_brute
    mock["detect"].assert_called_once_with("127.0.0.1")
    mock["ssh"].assert_called_once()
    mock["log"].assert_called_once()
    mock["save"].assert_called_once()


def test_entrypoint_mysql_success(mock_services_and_brute):
    mock_services_and_brute["mysql"].return_value = "mysqlpass"

    run_entrypoint_with_args(
        ["127.0.0.1", "admin", "passwords.txt", "--protocol", "mysql"]
    )

    mock_services_and_brute["mysql"].assert_called_once()
    mock_services_and_brute["log"].assert_called_once()
    mock_services_and_brute["save"].assert_called_once()


def test_entrypoint_unknown_service_skips(mock_services_and_brute):
    mock_services_and_brute["detect"].return_value = ["unknown"]

    run_entrypoint_with_args(
        ["127.0.0.1", "user", "passwords.txt", "--protocol", "auto"]
    )

    mock_services_and_brute["save"].assert_called_once()


def test_entrypoint_no_services_detected(mock_services_and_brute):
    mock_services_and_brute["detect"].return_value = []

    run_entrypoint_with_args(
        ["127.0.0.1", "user", "passwords.txt", "--protocol", "auto"]
    )

    mock_services_and_brute["ssh"].assert_not_called()
    mock_services_and_brute["save"].assert_not_called()
