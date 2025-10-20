import pymysql
from typing import Optional
from .utils import clear_line


def mysql_try_login(
    host: str,
    username: str,
    password_to_check: str,
    port: int = 3306,
    timeout: int = 3
) -> Optional[str]:
    """
    Attempt MySQL connection using a single password.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        password_to_check (str): Password to check.
        port (int): MySQL port. Defaults to 3306.
        timeout (int, optional): Connection timeout in seconds. Defaults to 5.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    try:
        conn = pymysql.connect(
            host=host,
            user=username,
            password=password_to_check,
            port=port,
            connect_timeout=timeout,
        )
        conn.close()
        return password_to_check
    except pymysql.err.OperationalError:
        clear_line()
        print(f"[-] MySQL login failed for {username}:{password_to_check}", end="\r")
        pass
    except Exception as e:
        clear_line()
        print(
            f"Connection error or other MYSQL issues: {e}. Continuing...",
            end="\r",
        )
        pass
    return None
