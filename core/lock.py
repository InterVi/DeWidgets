"""Provide lock file."""
import os
from core.paths import LOCK_FILE


def is_locked() -> bool:
    """Check is locked (file and PID available).

    :return: bool, True if locked
    """
    if os.path.isfile(LOCK_FILE):  # check lock
        with open(LOCK_FILE) as lock:
            try:
                os.kill(int(lock.read()), 0)
            except OSError:
                pass
            else:
                return True
    return False


def create_lock():
    """Create lock file (write PID)."""
    with open(LOCK_FILE, 'w') as lock:
        lock.write(str(os.getpid()))


def remove_lock():
    """Remove lock file."""
    if os.path.isfile(LOCK_FILE):
        os.remove(LOCK_FILE)
