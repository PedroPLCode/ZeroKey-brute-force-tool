import sys
import os
from unittest.mock import MagicMock
from entrypoint import entrypoint


def run_entrypoint_with_args(args_list):
    """
    Helper to run entrypoint() with a temporary argv list.
    IMPORTANT: Put positional args before option flags so argparse assigns
    positionals correctly (host, [usernames...], [wordlist], then options).
    """
    test_argv = ["entrypoint.py"] + args_list
    old_argv = sys.argv
    sys.argv = test_argv
    try:
        entrypoint()
    finally:
        sys.argv = old_argv


def make_wordlist(tmp_path, lines):
    """Create a simple wordlist file and return its path."""
    p = tmp_path / "wl.txt"
    p.write_text("\n".join(lines), encoding="utf-8")
    return str(p)


def test_entrypoint_skips_if_success_exists(monkeypatch, tmp_path, capsys):
    """
    If a success marker exists for a given host/user/protocol, entrypoint should
    skip brute-forcing that combination (login func should not be invoked).
    """
    host = "127.0.0.1"
    user = "alice"
    wl = make_wordlist(tmp_path, ["x"])

    monkeypatch.setattr("entrypoint.detect_services", lambda h: ["ftp"])
    mock_login = MagicMock(return_value=None)
    monkeypatch.setattr("entrypoint.LOGIN_FUNCS", {"ftp": (mock_login, 21, 0.01, 1)}, raising=False)

    monkeypatch.setattr("entrypoint.read_progress", lambda p: 0)
    monkeypatch.setattr("entrypoint.make_progress_path", lambda w, h, u, pr: os.path.join(str(tmp_path), f"{pr}.progress"))
    monkeypatch.setattr("entrypoint.make_success_path", lambda w, h, u, pr: os.path.join(str(tmp_path), f"{pr}.success"))

    monkeypatch.setattr("entrypoint.success_exists", lambda p: True)

    run_entrypoint_with_args([host, user, wl, "--protocol", "auto"])

    mock_login.assert_not_called()

    captured = capsys.readouterr()
    assert "[SKIP]" in captured.out or "already cracked" in captured.out
