from core.brute_ssh import ssh_bruteforce
from core.brute_ftp import ftp_bruteforce
from core.brute_mysql import mysql_bruteforce
from core.brute_postgres import postgres_bruteforce
from typing import Dict, Optional, Callable, Tuple

PORTS_TO_SCAN: dict[int, str] = {21: "ftp", 22: "ssh", 3306: "mysql", 5432: "postgres"}

BRUTEFORCE_FUNCS: Dict[str, Tuple[Callable[..., Optional[str]], int, int]] = {
    "ssh": (ssh_bruteforce, 22, 3),
    "ftp": (ftp_bruteforce, 21, 3),
    "mysql": (mysql_bruteforce, 3306, 3),
    "postgres": (postgres_bruteforce, 5432, 3),
}

DEFAULT_USERNAME = "root"
DEFAULT_PASSWORDS_FILE = "passwords.txt"

RESULT_PATH = "results/"
RESULT_FILE = "results.json"

LOGS_PATH = "logs/"
LOG_FILE = "brute_force.log"
