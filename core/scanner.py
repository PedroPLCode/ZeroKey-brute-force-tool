dodaj annotacje typów, ang docsting i wszystko ang

import socket
from settings import PORTS_TO_SCAN

def detect_services(host):
    services = []
    ports = PORTS_TO_SCAN

    for port, name in ports.items():
        try:
            sock = socket.create_connection((host, port), timeout=2)
            services.append(name)
            sock.close()
        except:
            continue

    return services
