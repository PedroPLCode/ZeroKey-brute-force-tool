dodaj annotacje typów, ang docsting i wszystko ang

import os
import json
from datetime import datetime

def log_result(data, log_path="logs/bruteforce.log"):
    with open(log_path, "a") as log:
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        line = f"{timestamp} HOST: {data['host']} USER: {data['username']} PROTO: {data['protocol']} SUCCESS: {data['success']} PASSWORD: {data['password']}\n"
        log.write(line)


def save_to_json(data, path="results/results.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[✓] Wyniki zapisane do {path}")