import pytest
from unittest.mock import patch, MagicMock
from core.scanner import detect_services

sample_ports = {
    21: "ftp",
    22: "ssh",
    3306: "mysql",
}


@pytest.fixture(autouse=True)
def patch_ports_to_scan(monkeypatch: pytest.MonkeyPatch):
    """Patch the PORTS_TO_SCAN variable for testing.

    Args:
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch fixture.
    """
    monkeypatch.setattr("core.scanner.PORTS_TO_SCAN", sample_ports)


def test_detect_services_all_open():
    """
    Test that detect_services returns all services if all ports are open.
    """
    def mock_create_connection(address: tuple[str, int], timeout: int = 2):
        mock_socket = MagicMock()
        return mock_socket

    with patch("socket.create_connection", side_effect=mock_create_connection):
        result = detect_services("127.0.0.1")
        assert set(result) == set(sample_ports.values())


def test_detect_services_some_open():
    """
    Test that detect_services returns only the services on open ports.
    """
    def mock_create_connection(address: tuple[str, int], timeout: int = 2):
        port = address[1]
        if port in (22, 3306):
            return MagicMock()
        else:
            raise OSError("Connection refused")

    with patch("socket.create_connection", side_effect=mock_create_connection):
        result = detect_services("127.0.0.1")
        assert set(result) == {"ssh", "mysql"}


def test_detect_services_none_open():
    """
    Test that detect_services returns empty list if no ports open.
    """
    def mock_create_connection(address: tuple[str, int], timeout: int = 2):
        raise OSError("Connection refused")

    with patch("socket.create_connection", side_effect=mock_create_connection):
        result = detect_services("127.0.0.1")
        assert result == []
