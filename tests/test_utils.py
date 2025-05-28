import json
import pytest
from pathlib import Path
from core.utils import log_result, save_to_json


def test_log_result_creates_log_file_and_writes(tmp_path: Path):
    log_path = tmp_path / "logdir" / "bruteforce.log"
    data: dict[str, object] = {
        "host": "127.0.0.1",
        "username": "user",
        "protocol": "ssh",
        "success": True,
        "password": "secret",
    }

    log_result(data, str(log_path))

    assert log_path.exists()
    content = log_path.read_text()
    assert "HOST: 127.0.0.1" in content
    assert "USER: user" in content
    assert "PROTO: ssh" in content
    assert "SUCCESS: True" in content
    assert "PASSWORD: secret" in content
    assert content.startswith("[")


def test_save_to_json_creates_file_and_saves_data(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
):
    data = {"key": "value"}
    json_path = tmp_path / "results" / "data.json"

    save_to_json(data, str(json_path))

    assert json_path.exists()
    with open(json_path) as f:
        loaded = json.load(f)
    assert loaded == data

    captured = capsys.readouterr()
    assert "[✓] Results saved to" in captured.out


@pytest.mark.parametrize("path", ["results/test.json", "logs/test.log"])
def test_directories_created_for_log_and_json(tmp_path: Path, path: str):
    full_path = tmp_path / path
    data: dict[str, object] = {
        "host": "host",
        "username": "user",
        "protocol": "proto",
        "success": False,
        "password": None,
    }

    if full_path.suffix == ".log":
        log_result(data, str(full_path))
        assert full_path.exists()
    else:
        save_to_json(data, str(full_path))
        assert full_path.exists()
