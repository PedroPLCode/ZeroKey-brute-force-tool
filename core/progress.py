import os
import tempfile
from config import STATE_PATH


def sanitize(s: str) -> str:
    """Sanitize string to be safe for filenames (replace path separators and spaces)."""
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in s)


def make_progress_path(wordlist_path: str, host: str, username: str, proto: str) -> str:
    """
    Create a progress file path unique for (wordlist, host, username, proto).
    Example: /path/to/wordlist.txt.127_0_0_1.root.ssh.progress
    """
    base = os.path.basename(wordlist_path)
    filename = f"{proto}_{host}_{username}_{base}.progress"
    return os.path.join(STATE_PATH, filename)


def atomic_write(path: str, data: str) -> None:
    """Atomically write data to path."""
    dirn = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dirn)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise


def read_progress(progress_path: str) -> int:
    """Read saved line index from progress file. Returns 0 if missing/invalid."""
    if not os.path.exists(progress_path):
        return 0
    try:
        with open(progress_path, "r", encoding="utf-8") as pf:
            content = pf.read().strip()
            return int(content) if content else 0
    except Exception:
        return 0


def write_progress(progress_path: str, line_index: int) -> None:
    """Write line index atomically to progress file."""
    atomic_write(progress_path, str(int(line_index)))


def remove_progress(progress_path: str) -> None:
    """Remove progress file if exists."""
    try:
        if os.path.exists(progress_path):
            os.remove(progress_path)
    except Exception:
        pass
    