import socket
from typing import List, Dict
from settings import PORTS_TO_SCAN


def detect_services(host: str) -> List[str]:
    """
    Detect open services on the given host by attempting TCP connections.

    Args:
        host (str): The IP address or hostname of the target.

    Returns:
        List[str]: A list of service names detected on open ports.
    """
    services: List[str] = []
    ports: Dict[int, str] = PORTS_TO_SCAN

    for port, service_name in ports.items():
        try:
            with socket.create_connection((host, port), timeout=2):
                services.append(service_name)
        except Exception as e:
            print(
                f"Error during service detection: {e} on port {port} for service {service_name}. Continuing..."
            )
            continue

    return services
