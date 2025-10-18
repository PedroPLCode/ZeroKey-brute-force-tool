"""
Settings for the brute-force tool.
DEFAULT_USERNAMES provides a list of common usernames to try during brute-force attacks.
TELNET_FAILURE_INDICATORS strings to find failure telnett login attempt.
TELNET_SUCCESS_INDICATORS strings to confirm successful telnet login attempt.
TELNET_SLEEP_DELAY Sleep delay to wait for telnet response in seconds.
"""

DEFAULT_USERNAMES = ["root", "admin", "postgres"]
TELNET_FAILURE_INDICATORS = [
    "login incorrect",
    "incorrect",
    "authentication failed",
    "access denied",
    "invalid",
    "failed",
    "connection closed"
]
TELNET_SUCCESS_INDICATORS = ["$", "#", ">", "last login", "welcome", "shell"]
TELNET_SLEEP_DELAY = 1
