import sys
from enum import Enum

class LogLevel(Enum):
    VERBOSE = 1
    ERROR = 2
    QUIET = 3

CURRENT_LOG_LEVEL = LogLevel.QUIET


def set_log_level(level: LogLevel) -> None:
    global CURRENT_LOG_LEVEL
    CURRENT_LOG_LEVEL = level


def log(msg: str, level: LogLevel) -> None:
    if level.value < CURRENT_LOG_LEVEL.value:
        return
    if level is LogLevel.VERBOSE:
        print(msg)
    elif level is LogLevel.ERROR:
        print(msg, file=sys.stderr)
    else:
        print(msg)
