import socket

def detect_services(host):
    services = []
    ports = {
        21: "ftp",
        22: "ssh"
    }

    for port, name in ports.items():
        try:
            sock = socket.create_connection((host, port), timeout=2)
            services.append(name)
            sock.close()
        except:
            continue

    return services
