from ftplib import FTP, error_perm
from typing import Optional
from .utils import clear_line


def ftp_try_login(
    host: str, 
    username: str, 
    password_to_check: str, 
    port: int = 21, 
    timeout: int = 3, 
) -> Optional[str]:
    """
    Attempt FTP connection using a single password.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        password_to_check (str): Password to check.
        port (int): FTP port. Defaults to 21.
        timeout (int, optional): Connection timeout in seconds. Defaults to 5.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    try:
        ftp = FTP()
        ftp.connect(host, port, timeout=timeout)
        ftp.login(user=username, passwd=password_to_check)
        ftp.quit()
        return password_to_check
    except error_perm:
        clear_line()
        print(f"[-] FTP login failed for {username}:{password_to_check}", end="\r")
        pass
    except Exception as e:
        clear_line()
        print(
            f"Connection error or other FTP issues: {e}. Continuing...",
            end="\r",
        )
        pass
    return None
