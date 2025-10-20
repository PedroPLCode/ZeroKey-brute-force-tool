import paramiko
from typing import Optional
from core.utils import clear_line


def ssh_try_login(
    host: str,
    username: str,
    password_to_check: str,
    port: int = 22,
    timeout: int = 3,
) -> Optional[str]:
    """
    Attempt SSH connection using a single password.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        password_to_check (str): Password to check.
        port (int): SSH port. Defaults to 22.
        timeout (int, optional): Connection timeout in seconds. Defaults to 5.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password_to_check,
            timeout=timeout,
        )
        return password_to_check
    except paramiko.AuthenticationException:
        clear_line()
        print(f"[-] SSH login failed for {username}:{password_to_check}", end="\r")
        pass
    except Exception as e:
        clear_line()
        print(
            f"Connection error or other SSH issues: {e}. Continuing...",
            end="\r",
        )
        pass
    finally:
        client.close()

    return None
