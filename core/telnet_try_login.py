import time
import telnetlib
from typing import Optional
from .utils import clear_line
from settings import (
    TELNET_FAILURE_INDICATORS,
    TELNET_SUCCESS_INDICATORS,
    TELNET_SLEEP_DELAY
)


def telnet_try_login(
    host: str,
    username: str,
    password_to_check: str,
    port: int = 23,
    timeout: int = 5,
) -> Optional[str]:
    """
    Attempt Telnet connection using a single password.

    Args:
        host (str): Target hostname or IP address.
        username (str): Username to authenticate.
        password_to_check (str): Password to check.
        port (int, optional): Telnet port. Defaults to 23.
        timeout (int, optional): Connection timeout in seconds. Defaults to 5.

    Returns:
        Optional[str]: The password if authentication succeeds; otherwise None.
    """
    tn = telnetlib.Telnet()
    try:
        tn.open(host, port, timeout=timeout)
    except Exception as e:
        clear_line()
        print(f"[-] Could not connect to {host}:{port} — {e}", end="\r")
        tn.close()
        time.sleep(TELNET_SLEEP_DELAY)
        return None

    try:
        try:
            prompt = tn.read_until(b"login: ", timeout=2)
        except Exception:
            prompt = b""

        if b"login" in prompt.lower() or b"username" in prompt.lower():
            tn.write(username.encode("utf-8") + b"\n")
            tn.read_until(b"Password: ", timeout=2)
            tn.write(password_to_check.encode("utf-8") + b"\n")
        else:
            tn.write(username.encode("utf-8") + b"\n")
            time.sleep(TELNET_SLEEP_DELAY)
            tn.write(password_to_check.encode("utf-8") + b"\n")

        time.sleep(TELNET_SLEEP_DELAY)
        try:
            response = tn.read_very_eager()
        except Exception:
            response = b""

        text = response.decode(errors="ignore").lower()

        if any(ind in text for ind in TELNET_SUCCESS_INDICATORS):
            tn.close()
            return password_to_check

        if any(ind in text for ind in TELNET_FAILURE_INDICATORS):
            clear_line()
            print(
                f"[-] Telnet login failed for {username}:{password_to_check}", end="\r"
            )
        else:
            clear_line()
            snippet = text.replace("\n", " ")[:200]
            print(
                f"[-] Unknown response for {username}:{password_to_check} -> {snippet!r}",
                end="\r",
            )

    except Exception as e:
        clear_line()
        print(f"[!] Telnet error for {username}:{password_to_check}: {e}", end="\r")
    finally:
        try:
            tn.close()
        except Exception:
            pass

    return None
