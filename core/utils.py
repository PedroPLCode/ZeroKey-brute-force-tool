import os
import json
from datetime import datetime
from typing import Any, Dict


def log_result(data: Dict[str, Any], log_path: str = "logs/bruteforce.log") -> None:
    """
    Append a log entry with timestamp and brute force attempt result details.

    Args:
        data (Dict[str, Any]): Dictionary containing keys 'host', 'username', 'protocol',
                               'success', and 'password'.
        log_path (str): Path to the log file. Defaults to 'logs/bruteforce.log'.
    """
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = (
        f"{timestamp} HOST: {data['host']} USER: {data['username']} "
        f"PROTO: {data['protocol']} SUCCESS: {data['success']} PASSWORD: {data['password']}\n"
    )
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as log:
        log.write(line)


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

def clear_line():
    """
    Clear the current line in the console.
    """
    print("\033[K", end="\r")