import os
from config import STATE_PATH


def make_success_path(wordlist_path: str, host: str, user: str, proto: str) -> str:
    """
    Create a success file path to track completed brute-force sessions.
    """
    base = os.path.basename(wordlist_path)
    filename = f"{proto}_{host}_{user}_{base}.success"
    return os.path.join(STATE_PATH, filename)


def write_success(success_path: str, password: str) -> None:
    """
    Write the successful password to the success file.
    """
    os.makedirs(os.path.dirname(success_path), exist_ok=True)
    with open(success_path, "w") as f:
        f.write(password)


def success_exists(success_path: str) -> bool:
    """
    Check if a success file exists for this protocol/host/user.
    """
    return os.path.exists(success_path)
