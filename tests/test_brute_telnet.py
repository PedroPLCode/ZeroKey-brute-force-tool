import pytest
from pathlib import Path
from core.brute_telnet import telnet_bruteforce


class FakeTelnetBase:
    """Base mock class emulating telnetlib.Telnet behavior used in tests.

    This class is designed to simulate the Telnet interface for unit tests
    without requiring a live Telnet server. It provides minimal methods
    that the `telnet_bruteforce` function interacts with.

    Args:
        responses (bytes, optional): Data returned by `read_very_eager()`.
        open_raises (bool, optional): If True, `open()` raises an exception to simulate connection errors.
        read_until_prompts (dict[bytes, bytes], optional): A mapping of prompts to return values
            for `read_until()` calls.
    """

    def __init__(self, responses=None, open_raises=False, read_until_prompts=None):
        self._responses = responses or b""
        self._closed = False
        self.open_raises = open_raises
        self.read_until_prompts = read_until_prompts or {}
        self.written = b""

    def open(self, host, port, timeout=None):
        """Simulate opening a Telnet connection, optionally raising an exception."""
        if self.open_raises:
            raise Exception("connection error")

    def read_until(self, prompt: bytes, timeout=None):
        """Return the pre-defined response for a given prompt."""
        return self.read_until_prompts.get(prompt, b"")

    def write(self, data: bytes):
        """Store written bytes (simulating sending data over the connection)."""
        self.written += data

    def read_very_eager(self):
        """Return the pre-defined response bytes from the server."""
        return self._responses

    def close(self):
        """Mark the connection as closed."""
        self._closed = True


def make_wordlist(tmp_path: Path, lines):
    """Helper function to create a temporary wordlist file for testing.

    Args:
        tmp_path (Path): The pytest temporary path fixture.
        lines (list[str]): List of passwords to write into the wordlist.

    Returns:
        str: The absolute path to the created wordlist file.
    """
    p = tmp_path / "wordlist.txt"
    p.write_text("\n".join(lines), encoding="utf-8")
    return str(p)


def test_success_on_first_password(monkeypatch, tmp_path, capsys):
    """Test that the first password in the wordlist succeeds immediately.

    This test ensures that the function correctly detects a successful
    login attempt when the very first password triggers a success indicator.
    """
    wl = make_wordlist(tmp_path, ["password1", "password2"])
    fake = FakeTelnetBase(responses=b"Welcome\n$ ")
    monkeypatch.setattr("telnetlib.Telnet", lambda: fake)
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_SUCCESS_INDICATORS", ["$", "#", ">"], raising=False
    )
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_FAILURE_INDICATORS",
        ["login incorrect", "invalid"],
        raising=False,
    )

    found = telnet_bruteforce("127.0.0.1", "user", wl, port=23, timeout=1, delay=0)
    assert found == "password1"

    captured = capsys.readouterr()
    assert "Telnet login succeeded" in captured.out


def test_success_on_later_password(monkeypatch, tmp_path, capsys):
    """Test that success is detected on a later password after one or more failures.

    This test simulates multiple Telnet attempts where earlier passwords
    fail and a later one triggers a success indicator.
    """
    wl = make_wordlist(tmp_path, ["bad1", "rightpass", "bad2"])
    responses_sequence = [b"Login incorrect\n", b"Welcome\n$ "]
    created = {"i": 0}

    def telnet_factory():
        idx = created["i"]
        resp = responses_sequence[min(idx, len(responses_sequence) - 1)]
        created["i"] += 1
        return FakeTelnetBase(responses=resp)

    monkeypatch.setattr("telnetlib.Telnet", telnet_factory)
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_SUCCESS_INDICATORS", ["$", "#", ">"], raising=False
    )
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_FAILURE_INDICATORS",
        ["login incorrect", "invalid"],
        raising=False,
    )

    found = telnet_bruteforce("127.0.0.1", "user", wl, port=23, timeout=1, delay=0)
    assert found == "rightpass"
    captured = capsys.readouterr()
    assert "Telnet login succeeded" in captured.out


def test_connection_error_skips_and_continues(monkeypatch, tmp_path, capsys):
    """Test that connection errors are handled gracefully and subsequent attempts continue.

    This test simulates the first Telnet connection raising an exception,
    verifying that the function skips it and continues with the next password.
    """
    wl = make_wordlist(tmp_path, ["pass1", "pass2"])
    created = {"i": 0}

    class TelnetFactory:
        def __call__(self):
            idx = created["i"]
            created["i"] += 1
            if idx == 0:
                return FakeTelnetBase(open_raises=True)
            return FakeTelnetBase(responses=b"Welcome\n$ ")

    monkeypatch.setattr("telnetlib.Telnet", TelnetFactory())
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_SUCCESS_INDICATORS", ["$"], raising=False
    )
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_FAILURE_INDICATORS",
        ["login incorrect"],
        raising=False,
    )

    found = telnet_bruteforce("127.0.0.1", "user", wl, port=23, timeout=1, delay=0)
    assert found == "pass2"


def test_no_password_found_returns_none(monkeypatch, tmp_path, capsys):
    """Test that the function returns None if no password succeeds.

    This test checks that when all responses indicate failure,
    the function correctly returns None after exhausting the wordlist.
    """
    wl = make_wordlist(tmp_path, ["a", "b", "c"])

    def telnet_factory():
        return FakeTelnetBase(responses=b"Login incorrect\n")

    monkeypatch.setattr("telnetlib.Telnet", telnet_factory)
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_SUCCESS_INDICATORS", ["$"], raising=False
    )
    monkeypatch.setattr(
        "core.brute_telnet.TELNET_FAILURE_INDICATORS",
        ["login incorrect"],
        raising=False,
    )

    found = telnet_bruteforce("127.0.0.1", "user", wl, port=23, timeout=1, delay=0)
    assert found is None
    captured = capsys.readouterr()
    assert "Telnet login failed" in captured.out or "Unknown response" in captured.out


def test_file_not_found_raises(tmp_path):
    """Test that FileNotFoundError is raised when the wordlist file does not exist."""
    with pytest.raises(FileNotFoundError):
        telnet_bruteforce("127.0.0.1", "user", str(tmp_path / "no_such_file.txt"))
