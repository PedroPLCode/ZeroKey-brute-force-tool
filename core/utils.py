from datetime import datetime

def log_result(data, log_path="logs/bruteforce.log"):
    with open(log_path, "a") as log:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        line = f"{timestamp} HOST: {data['host']} USER: {data['username']} PROTO: {data['protocol']} SUCCESS: {data['success']} PASSWORD: {data['password']}\n"
        log.write(line)
