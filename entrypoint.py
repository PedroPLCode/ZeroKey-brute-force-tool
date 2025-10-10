import argparse
from typing import Optional, Dict, List
from core.scanner import detect_services
from core.utils import (
    log_result, 
    save_to_json, 
    create_results_filename, 
    get_current_timestamp
)
from settings import (
    DEFAULT_PASSWORDS_FILE,
    LOGS_PATH,
    LOG_FILE,
    RESULT_PATH,
    DEFAULT_USERNAME,
    BRUTEFORCE_FUNCS,
)


def entrypoint() -> None:
    """
    CLI entrypoint for a simple brute-force tool with auto service detection.
    Supports SSH, FTP, MySQL, and PostgreSQL protocols.
    Results are logged and can be saved in JSON format.
    """
    try:
        parser = argparse.ArgumentParser(
            description="Simple brute force tool for SSH/FTP/MySQL/Postgres with auto service detection"
        )
        parser.add_argument("host", help="Target host IP address")
        parser.add_argument(
            "username", help="Username to authenticate with", default=DEFAULT_USERNAME
        )
        parser.add_argument(
            "wordlist",
            help="Path to password wordlist file",
            default=DEFAULT_PASSWORDS_FILE,
        )
        parser.add_argument(
            "--protocol",
            choices=["ssh", "ftp", "mysql", "postgres", "auto"],
            default="auto",
            help="Protocol to brute-force (default: auto)",
        )
        parser.add_argument(
            "--port", type=int, help="Custom port for the selected service"
        )
        parser.add_argument("--output", help="Path to save JSON output", default=None)
        args = parser.parse_args()

        print(f"[INFO] Starting brute-force attack on {args.host} as {args.username}")

        if args.protocol == "auto":
            detected: List[str] = detect_services(args.host)
            print(f"[INFO] Detected services: {detected}")
            if not detected:
                print("[WARN] No services detected on the target host. Exiting.")
                return
        else:
            detected = [args.protocol]

        result: Dict[str, Optional[str] | bool] = {
            "timestamp": get_current_timestamp(),
            "host": args.host,
            "protocol": None,
            "success": False,
            "username": args.username,
            "password": None,
        }

        for proto in detected:
            password: Optional[str] = None

            if proto in BRUTEFORCE_FUNCS:
                func, default_port, timeout = BRUTEFORCE_FUNCS[proto]
                port = args.port or default_port
                password = func(
                    args.host, args.username, args.wordlist, port=port, timeout=timeout
                )
            else:
                print(f"[WARN] Unknown protocol: {proto}, skipping.")
                continue

            if password:
                result.update(
                    {"protocol": proto, "success": True, "username": args.username, "password": password}
                )
                log_path = LOGS_PATH + LOG_FILE
                log_result(result, log_path=log_path)
                print(f"[SUCCESS] {proto.upper()} - Username: {args.username}, Password: {password}")

        results_filename = create_results_filename(args.host, proto, args.username)
        result_path = RESULT_PATH + results_filename
        save_to_json(result, path=args.output or result_path)
        print("[INFO] Brute-force attack completed.")
    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    entrypoint()
    