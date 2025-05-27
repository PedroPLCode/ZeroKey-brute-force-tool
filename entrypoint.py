import argparse
from typing import Optional, Dict, List
from core.scanner import detect_services
from core.brute_ssh import ssh_bruteforce
from core.brute_ftp import ftp_bruteforce
from core.brute_mysql import mysql_bruteforce
from core.brute_postgres import postgres_bruteforce
from core.utils import log_result, save_to_json


def entrypoint() -> None:
    """
    CLI entrypoint for a simple brute-force tool with auto service detection.
    Supports SSH, FTP, MySQL, and PostgreSQL protocols.
    """
    parser = argparse.ArgumentParser(
        description="Simple brute force tool for SSH/FTP/MySQL/Postgres with auto service detection"
    )
    parser.add_argument("host", help="Target host IP address")
    parser.add_argument("username", help="Username to authenticate with")
    parser.add_argument("wordlist", help="Path to password wordlist file")
    parser.add_argument(
        "--protocol",
        choices=["ssh", "ftp", "mysql", "postgres", "auto"],
        default="auto",
        help="Protocol to brute-force (default: auto)"
    )
    parser.add_argument("--port", type=int, help="Custom port for the selected service")
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
        "host": args.host,
        "username": args.username,
        "protocol": None,
        "success": False,
        "password": None
    }

    for proto in detected:
        password: Optional[str] = None

        if proto == "ssh":
            password = ssh_bruteforce(args.host, args.username, args.wordlist, port=args.port)
        elif proto == "ftp":
            password = ftp_bruteforce(args.host, args.username, args.wordlist, port=args.port)
        elif proto == "mysql":
            password = mysql_bruteforce(args.host, args.username, args.wordlist, port=args.port or 3306)
        elif proto == "postgres":
            password = postgres_bruteforce(args.host, args.username, args.wordlist, port=args.port or 5432)
        else:
            print(f"[WARN] Unknown protocol: {proto}, skipping.")
            continue

        if password:
            result.update({
                "protocol": proto,
                "success": True,
                "password": password
            })
            log_result(result)
            break

    save_to_json(result, path=args.output or "results/results.json")
    print("[INFO] Scan completed.")
