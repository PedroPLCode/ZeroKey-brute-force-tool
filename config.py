from core.ssh_try_login import ssh_try_login
from core.ftp_try_login import ftp_try_login
from core.telnet_try_login import telnet_try_login
from core.mysql_try_login import mysql_try_login
from core.postgres_try_login import postgres_try_login
from typing import Dict, Optional, Callable, Tuple

"""
Configuration settings for the brute-force tool.
PORTS_TO_SCAN is a dictionary mapping common service ports to their respective service names.
SCAN_DELAY sets a delay between port scans to avoid overwhelming the target.
LOGIN_FUNCS maps service names to their corresponding login functions along with
default port, delay between attempts and connection timeout.
DATA_DIR specifies the directory where username and password files are stored.
DEFAULT_USERNAMES_FILE and DEFAULT_PASSWORDS_FILE define the paths to these files.
DEFAULT_PASSWORDS_FILE defines the path to the default passwords file.
STATE_PATH specifies where to store progress state files.
RESULT_PATH and LOGS_PATH define where to store results and logs respectively.
RESULT_LOG_FILE specifies the log file name.
"""

PORTS_TO_SCAN: dict[int, str] = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    3306: "mysql",
    5432: "postgres",
}
SCAN_DELAY = 0.5

# Service name to (login function, default port, delay between attempts, connection timeout)
LOGIN_FUNCS: Dict[str, Tuple[Callable[..., Optional[str]], int, float, float]] = {
    "ssh": (ssh_try_login, 22, 0.5, 5.0),
    "ftp": (ftp_try_login, 21, 0.5, 5.0),
    "telnet": (telnet_try_login, 23, 3.0, 5.0),
    "mysql": (mysql_try_login, 3306, 0.5, 5.0),
    "postgres": (postgres_try_login, 5432, 0.5, 5.0),
}

DATA_DIR = "data/"
DEFAULT_USERNAMES_FILE = DATA_DIR + "usernames.txt"
DEFAULT_PASSWORDS_FILE = DATA_DIR + "passwords.txt"

STATE_PATH = f"{DATA_DIR}state/"

RESULT_PATH = "results/"
RESULT_LOG_FILE = "brute_force.log"
