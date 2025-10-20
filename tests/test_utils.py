import re
from datetime import datetime
from core import utils


def test_load_usernames_from_file_ignores_comments_and_blank_lines(tmp_path):
    """
    Test that load_usernames_from_file reads usernames, ignores comment lines
    (starting with '#') and empty lines, and returns the expected list.
    """
    content = """
    # this is a comment
    alice

    # another comment
    bob
    # indented comment
    charlie
    """
    fp = tmp_path / "users.txt"
    fp.write_text(content, encoding="utf-8")

    users = utils.load_usernames_from_file(str(fp))
    assert users == ["alice", "bob", "charlie"]


def test_load_usernames_from_file_missing_file_returns_empty_list(tmp_path, capsys):
    """
    If the file cannot be read, the function should return an empty list
    and print an error message (caught by capturing stdout).
    """
    missing = tmp_path / "no_such_file.txt"
    users = utils.load_usernames_from_file(str(missing))
    assert users == []

    captured = capsys.readouterr()
    assert "Unable to read user file" in captured.out or "Unable to read user file" in captured.err


def test_get_current_timestamp_format():
    """
    get_current_timestamp should return a string in the format YYYY-MM-DD HH:MM:SS
    that can be parsed by datetime.strptime with the same format.
    """
    ts = utils.get_current_timestamp()
    assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", ts)
    parsed = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    assert isinstance(parsed, datetime)


def test_log_result_writes_file_and_prints_ok(tmp_path, monkeypatch, capsys):
    """
    log_result should append a single-line entry to the specified log file and
    print an '[OK] Log entry added' message. We monkeypatch get_current_timestamp
    to a fixed value so the log line is deterministic.
    """
    fake_ts = "2000-01-02 03:04:05"
    monkeypatch.setattr(utils, "get_current_timestamp", lambda: fake_ts)

    data = {
        "host": "10.0.0.1",
        "protocol": "ssh",
        "success": True,
        "username": "root",
        "password": "pw123",
    }

    log_dir = tmp_path / "logs"
    log_file = log_dir / "bruteforce.log"
    assert not log_dir.exists()

    utils.log_result(data, log_path=str(log_file))

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert fake_ts in content
    assert "10.0.0.1:ssh" in content
    assert "success:True" in content
    assert "root:pw123" in content

    captured = capsys.readouterr()
    assert "[OK] Log entry added" in captured.out


def test_clear_line_prints_escape_sequence(capsys):
    """
    clear_line should print the terminal escape sequence to clear the line
    (\\033[K) and return the cursor to start (\\r). We verify stdout contains
    the escape code followed by carriage return.
    """
    utils.clear_line()
    captured = capsys.readouterr()
    assert "\033[K" in captured.out
    assert captured.out.endswith("\r") or captured.out.endswith("\r\n")
