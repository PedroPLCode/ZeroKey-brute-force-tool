import psycopg2
from psycopg2 import OperationalError
from typing import Optional
from .utils import clear_line
from settings import POSTGRES_DB_NAME


def postgres_try_login(
    host: str,
    username: str,
    password_to_check: str,
    port: int = 5432,
    timeout: int = 3,
) -> Optional[str]:
    """
    Attempt PostgreSQL connection using a single password.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        password_to_check (str): Password to check.
        port (int, optional): PostgreSQL port. Defaults to 5432.
        dbname (str, optional): Database name to connect to. Defaults to "postgres".
        timeout (int, optional): Connection timeout in seconds. Defaults to 5.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    try:
        conn = psycopg2.connect(
            host=host,
            user=username,
            password=password_to_check,
            port=port,
            dbname=POSTGRES_DB_NAME,
            connect_timeout=timeout,
        )
        conn.close()
        return password_to_check
    except OperationalError:
        clear_line()
        print(
            f"[-] PostgreSQL login failed for {username}:{password_to_check}", end="\r"
        )
        pass
    except Exception as e:
        clear_line()
        print(
            f"Connection error or other POSTGRES issues: {e}. Continuing...",
            end="\r",
        )
        pass
    return None
