import os
import tempfile
import pytest
from core import success as success_mod


@pytest.fixture
def tmp_state_dir(monkeypatch):
    """
    Create a temporary directory and monkeypatch success.STATE_PATH to point to it.

    This ensures all success files are created inside a temp directory and are
    removed automatically by the fixture at test end.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(success_mod, "STATE_PATH", tmpdir)
        yield tmpdir


def test_make_success_path_contains_components(tmp_state_dir):
    """
    Ensure make_success_path produces a path inside STATE_PATH that includes
    protocol, host, user and original wordlist base name.
    """
    wordlist = "/data/wordlists/common.txt"
    host = "127.0.0.1"
    user = "root"
    proto = "ssh"

    path = success_mod.make_success_path(wordlist, host, user, proto)

    assert path.startswith(tmp_state_dir)
    assert path.endswith(".success")
    assert proto in os.path.basename(path)
    assert host in os.path.basename(path)
    assert user in os.path.basename(path)
    assert "common.txt" in os.path.basename(path)


def test_write_success_creates_file_and_writes_password(tmp_state_dir):
    """
    write_success should create parent dirs as needed and write the password
    into the file at the given success path.
    """
    wordlist = "/data/wordlists/common.txt"
    host = "10.0.0.5"
    user = "admin"
    proto = "ftp"

    path = success_mod.make_success_path(wordlist, host, user, proto)
    password = "s3cr3t!"

    assert not os.path.exists(path)

    success_mod.write_success(path, password)
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == password


def test_success_exists_reflects_file_presence(tmp_state_dir):
    """
    success_exists should return True when the success file exists and False otherwise.
    """
    wordlist = "wl.txt"
    host = "localhost"
    user = "user"
    proto = "mysql"

    path = success_mod.make_success_path(wordlist, host, user, proto)

    assert not success_mod.success_exists(path)

    success_mod.write_success(path, "pw")
    assert success_mod.success_exists(path)


def test_write_success_overwrites_existing_file(tmp_state_dir):
    """
    write_success should overwrite existing success file with the new password.
    """
    wordlist = "wl2.txt"
    host = "host"
    user = "u"
    proto = "telnet"
    path = success_mod.make_success_path(wordlist, host, user, proto)

    success_mod.write_success(path, "first")
    assert success_mod.success_exists(path)
    with open(path, "r", encoding="utf-8") as f:
        assert f.read() == "first"

    success_mod.write_success(path, "second")
    with open(path, "r", encoding="utf-8") as f:
        assert f.read() == "second"
