from core.brute_ssh import ssh_bruteforce
from core.brute_ftp import ftp_bruteforce
from core.brute_telnet import telnet_bruteforce
from core.brute_mysql import mysql_bruteforce
from core.brute_postgres import postgres_bruteforce
from typing import Dict, Optional, Callable, Tuple

"""
Configuration settings for the brute-force tool.
PORTS_TO_SCAN is a dictionary mapping common service ports to their respective service names.
SCAN_DELAY sets a delay between port scans to avoid overwhelming the target.
BRUTEFORCE_FUNCS maps service names to their corresponding brute-force functions along with
default port, max attempts and delay between attempts.
DATA_DIR specifies the directory where username and password files are stored.
DEFAULT_USERNAMES_FILE and DEFAULT_PASSWORDS_FILE define the paths to these files.
DEFAULT_PASSWORDS_FILE defines the path to the default passwords file.
RESULT_PATH and LOGS_PATH define where to store results and logs respectively.
LOG_PATH specifies the log file name.
LOG_FILE specifies the log file name.
"""

PORTS_TO_SCAN: dict[int, str] = {
    21: "ftp",
    22: "ssh",
    23: "telnet",
    3306: "mysql",
    5432: "postgres",
}
SCAN_DELAY = 0.5

# Service name to (bruteforce function, default port, max attempts, delay between attempts)
BRUTEFORCE_FUNCS: Dict[str, Tuple[Callable[..., Optional[str]], int, int, float]] = {
    "ssh": (ssh_bruteforce, 22, 3, 0.3),
    "ftp": (ftp_bruteforce, 21, 3, 0.3),
    "telnet": (telnet_bruteforce, 23, 3, 0.3),
    "mysql": (mysql_bruteforce, 3306, 3, 0.3),
    "postgres": (postgres_bruteforce, 5432, 3, 0.3),
}

DATA_DIR = "data/"
DEFAULT_USERNAMES_FILE = DATA_DIR + "usernames.txt"
DEFAULT_PASSWORDS_FILE = DATA_DIR + "passwords.txt"

RESULT_PATH = "results/"

LOGS_PATH = "logs/"
LOG_FILE = "brute_force.log"
