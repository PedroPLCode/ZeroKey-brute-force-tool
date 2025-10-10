import os
import json
from datetime import datetime
from typing import Any, Dict, List


def load_usernames_from_file(path: str) -> List[str]:
    """
    Load usernames from a file, ignoring comments and empty lines.

    Args:
        path (str): Path to the file containing usernames.

    Returns:
        List[str]: List of usernames.
    """
    users: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                users.append(line)
    except Exception as e:
        print(f"[ERROR] Unable to read user file '{path}': {e}")
    return users


def log_result(data: Dict[str, Any], log_path: str = "logs/bruteforce.log") -> None:
    """
    Append a log entry with timestamp and brute force attempt result details.

    Args:
        data (Dict[str, Any]): Dictionary containing keys 'host', 'username', 'protocol',
                               'success', and 'password'.
        log_path (str): Path to the log file. Defaults to 'logs/bruteforce.log'.
    """
    timestamp = get_current_timestamp()
    line = f"[{timestamp}] HOST: {data['host']} PROTO: {data['protocol']} SUCCESS: {data['success']} USER: {data['username']} PASSWORD: {data['password']}\n"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as log:
        log.write(line)
    print(f"[✓] Log entry added to {log_path}")


def save_to_json(data: Dict[str, Any], path: str = "results/results.json") -> None:
    """
    Save a dictionary to a JSON file, creating directories as needed.

    Args:
        data (Dict[str, Any]): Data to be saved as JSON.
        path (str): Destination JSON file path. Defaults to 'results/results.json'.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[✓] Results saved to {path}")


def get_current_timestamp() -> str:
    """
    Get the current timestamp in the format [YYYY-MM-DD HH:MM:SS].

    Returns:
        str: Current timestamp.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clear_line():
    """
    Clear the current line in the console.
    """
    print("\033[K", end="\r")


def create_results_filename(host: str) -> str:
    """
    Create a results filename based on the host.

    Args:
        host (str): Target host.
        proto (str): Protocol used.

    Returns:
        str: Generated filename.
    """
    safe_host = host.replace('.', '_')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"brute_force_results_{timestamp}_{safe_host}.json"
