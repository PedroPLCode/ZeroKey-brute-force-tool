import os
import argparse
import json
from datetime import datetime
from core.scanner import detect_services
from core.brute_ssh import ssh_bruteforce
from core.brute_ftp import ftp_bruteforce
from core.brute_mysql import mysql_bruteforce
from core.brute_postgres import postgres_bruteforce

from core.utils import log_result

def save_to_json(data, path="results/results.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[✓] Wyniki zapisane do {path}")

def main():
    parser = argparse.ArgumentParser(description="Prosty brute force na SSH/FTP z autodetekcją usług")
    parser.add_argument("host", help="Adres IP hosta")
    parser.add_argument("username", help="Nazwa użytkownika do logowania")
    parser.add_argument("wordlist", help="Ścieżka do pliku z hasłami")
    parser.add_argument("--protocol", choices=["ssh", "ftp", "auto"], default="auto", help="Protokół do użycia")
    args = parser.parse_args()

    print(f"[INFO] Rozpoczynam brute force na {args.host} jako {args.username}")

    detected = []
    if args.protocol == "auto":
        detected = detect_services(args.host)
        print(f"[INFO] Wykryto usługi: {detected}")
    else:
        detected = [args.protocol]

    result = {"host": args.host, "username": args.username, "protocol": None, "success": False, "password": None}

    for proto in detected:
        if proto == "ssh":
            pwd = ssh_bruteforce(args.host, args.username, args.wordlist)
        elif proto == "ftp":
            pwd = ftp_bruteforce(args.host, args.username, args.wordlist)
        elif proto == "mysql":
            pwd = mysql_bruteforce(args.host, args.username, args.wordlist)

        else:
            continue

        if pwd:
            result.update({"protocol": proto, "success": True, "password": pwd})
            log_result(result)
            break

    save_to_json(result)
    print("[INFO] Zakończono skanowanie.")

if __name__ == "__main__":
    main()
