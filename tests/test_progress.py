import os
import tempfile
import pytest
from core.progress import (
    sanitize,
    make_progress_path,
    atomic_write,
    read_progress,
    write_progress,
    remove_progress,
)

@pytest.fixture
def temp_state_path(monkeypatch):
    """
    Fixture that creates a temporary STATE_PATH directory for testing.
    Automatically cleans up after the test.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr("core.progress.STATE_PATH", tmpdir)
        yield tmpdir


def test_sanitize():
    """
    Test that sanitize() correctly replaces unsafe characters in filenames.
    """
    original = "root@127.0.0.1:password list.txt"
    result = sanitize(original)
    assert "@" not in result
    assert ":" not in result
    assert " " not in result
    assert result.endswith(".txt")
    assert all(c.isalnum() or c in "-_." for c in result)


def test_make_progress_path(temp_state_path):
    """
    Test that make_progress_path() generates the correct file path inside STATE_PATH.
    """
    path = make_progress_path("/data/wordlist.txt", "127.0.0.1", "root", "ssh")
    assert path.startswith(temp_state_path)
    assert "ssh_127.0.0.1_root_wordlist.txt.progress" in path


def test_atomic_write_and_read_progress(temp_state_path):
    """
    Test that atomic_write() safely writes data and read_progress() reads it correctly.
    """
    test_file = os.path.join(temp_state_path, "progress.test")
    atomic_write(test_file, "42")

    with open(test_file, "r", encoding="utf-8") as f:
        assert f.read() == "42"

    assert read_progress(test_file) == 42


def test_read_progress_invalid_file(temp_state_path):
    """
    Test that read_progress() returns 0 for missing or invalid files.
    """
    invalid_path = os.path.join(temp_state_path, "missing.progress")

    assert read_progress(invalid_path) == 0

    corrupted_file = os.path.join(temp_state_path, "corrupted.progress")
    with open(corrupted_file, "w", encoding="utf-8") as f:
        f.write("not_a_number")

    assert read_progress(corrupted_file) == 0


def test_write_progress_and_remove(temp_state_path):
    """
    Test that write_progress() writes correctly and remove_progress() deletes the file.
    """
    path = os.path.join(temp_state_path, "test_write.progress")

    write_progress(path, 100)
    assert os.path.exists(path)
    assert read_progress(path) == 100

    remove_progress(path)
    assert not os.path.exists(path)


def test_atomic_write_cleanup_on_error(temp_state_path, monkeypatch):
    """
    Test that atomic_write() cleans up temporary files if an exception occurs.
    """
    temp_file = os.path.join(temp_state_path, "cleanup.progress")

    def fail_replace(src, dst):
        raise OSError("Simulated write failure")

    monkeypatch.setattr("os.replace", fail_replace)

    with pytest.raises(OSError):
        atomic_write(temp_file, "data")

    leftovers = [f for f in os.listdir(temp_state_path) if f.endswith(".tmp")]
    assert not leftovers
