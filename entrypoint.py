import argparse
from typing import Optional, Dict, List
from core.scanner import detect_services
from core.utils import (
    load_usernames_from_file,
    log_result,
    save_to_json,
    create_results_filename,
    get_current_timestamp
)
from settings import (
    LOGS_PATH,
    LOG_FILE,
    RESULT_PATH,
    DEFAULT_USERNAMES,
    DEFAULT_PASSWORDS_FILE,
    BRUTEFORCE_FUNCS,
)


def entrypoint() -> None:
    """
    Main entry point for the brute-force tool. Parses command-line arguments, detects services,
    and attempts brute-force attacks on the specified host using provided or default usernames
    and password lists. Results are logged and saved in JSON format.
    """
    try:
        parser = argparse.ArgumentParser(
            description="Brute-force tool for various services (SSH, FTP, MySQL, PostgreSQL)."
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
            choices=["ssh", "ftp", "mysql", "postgres", "auto"],
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

                if proto in BRUTEFORCE_FUNCS:
                    func, default_port, timeout = BRUTEFORCE_FUNCS[proto]
                    port = args.port or default_port
                    wordlist_path = args.wordlist or DEFAULT_PASSWORDS_FILE
                    try:
                        password = func(
                            args.host, user, wordlist_path, port=port, timeout=timeout
                        )
                    except Exception as e:
                        print(f"[ERROR] Error during brute-force attempt ({proto}) for {user}: {e}")
                        password = None
                else:
                    print(f"[WARN] Unknown protocol: {proto}, skipping.")
                    password = None

                if password:
                    result = result_template.copy()
                    result.update({"success": True, "password": password})
                    log_path = LOGS_PATH + LOG_FILE
                    try:
                        log_result(result, log_path=log_path)
                    except Exception as e:
                        print(f"[WARN] Failed to log result: {e}")
                    print(f"[SUCCESS] {proto.upper()} {user}:{password}")
                    all_results.append(result)
                else:
                    result = result_template.copy()
                    all_results.append(result)
                    print(f"[INFO] {proto.upper()} - no valid password found for {user}")

        results_filename = create_results_filename(args.host)
        result_path = RESULT_PATH + results_filename
        save_to_json(all_results, path=args.output or result_path)
        print(f"[INFO] Brute-force attack completed.")

    except (KeyboardInterrupt, Exception) as e:
        if isinstance(e, KeyboardInterrupt):
            print("\n[INFO] Exiting due to user interruption.")
        else:
            print(f"[ERROR] An unexpected error occurred: {e}")
        result_path = RESULT_PATH + "partial_results.json"
        if 'all_results' in locals() and all_results:
            save_to_json(all_results, path=result_path)
        exit(1)


if __name__ == "__main__":
    entrypoint()
