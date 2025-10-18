# ZeroKey-bruteforce-tool
A simple command-line brute force tool for SSH, FTP, Telnet, MySQL, and PostgreSQL services with automatic service detection.

### Features
- Automatic detection of running services on the target host (SSH, FTP, Telnet, MySQL, PostgreSQL)
- Brute force attack using a username and password wordlist
- Support for specifying protocol and port manually
- Logs successful login attempts to a file
- Saves results in JSON format
- Easy to extend with additional protocols

### Requirements
- Python 3.7+
- Dependencies listed in `requirements.txt`

### Installation
```bash
git clone https://github.com/PedroPLCode/ZeroKey-brute-force-tool.git
cd ZeroKey-brute-force-tool
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Usage
```bash
# adjust config.py and settings.py if needed.
python entrypoint.py <host> <username> <wordlist> [--protocol {ssh,ftp,telnet,mysql,postgres,auto}] [--port PORT] [--output OUTPUT]

Arguments
<host> — Target host IP or domain
<username> — Username to attempt login with
<wordlist> — Path to a password wordlist file

Optional arguments
--protocol — Protocol to use: ssh, ftp, telnet, mysql, postgres, or auto (default: auto)
--port — Port number of the service (defaults based on protocol if not specified)
--output — Path to save JSON results (default: results/results.json)

Example
python __main__.py 192.168.1.100 admin passwords.txt --protocol ssh --port 22 --output output.json
```

### How it works
If --protocol auto is set, the tool scans common service ports to detect running services.
For each detected or specified service, it tries passwords from the wordlist.
On successful login, it logs the details and stops further attempts.
Results are saved to a JSON file and appended to a log file.

### Testing
Tests use pytest. To run tests:
```bash
pytest tests/
```

### Use responsibly and only against systems you own or have explicit permission to test.
This tool is intended solely for ethical testing purposes. Unauthorized use against systems you do not own or do not have explicit permission to test is illegal and unethical. Always ensure you have proper authorization before conducting any brute force or penetration testing activities. Misuse of this software can lead to serious legal consequences. Use it responsibly, respecting privacy and security policies.

### License
This project is licensed under GNU General Public License Version 3, 29 June 2007