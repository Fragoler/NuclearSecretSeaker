from ignored import get_git_ignored_files
from logger import LogLevel, log
from config import parse_config
from patterns import load_patterns_from_json
from scanner import find_regex

from pathlib import Path

import sys
import json

DEFAULT_CONFIG_PATH = ".nuclearss"
DEFAULT_ROOT_DIR = "."


def print_help():
    help_text = f"""
        Usage: program [options]

        Options:
          -h, --help               See this message
          -i DIR, --input DIR      Pick root directory (default: {DEFAULT_ROOT_DIR})
          -c FILE, --config FILE   Specify config file (default: {DEFAULT_CONFIG_PATH})
          -x DIR, --ignore DIR     Ignore directory
          -x FILE, --ignore FILE   Ignore file
          -x FILE1 -x FILE2 -x DIR The way to ignore multiple dirs/files
    """
    log(help_text, LogLevel.QUIET)


def main():
    argc = len(sys.argv)
    root_dir = "."
    config_path = DEFAULT_CONFIG_PATH
    ignore_list = []
    if argc == 1:
        pass
    else:
        i = 1
        while i < argc:
            if sys.argv[i] in ['-h', '--help']:
                print_help()
                return
            elif sys.argv[i] in ['-i', '--input']:
                if i + 1 < argc:
                    root_dir = sys.argv[i + 1]
                    i += 2
                else:
                    log("DIR expected after -i (--input) option)", LogLevel.ERROR)
                    return
            elif sys.argv[i] in ['-x', '--ignore']:
                if i + 1 < argc:
                    ignore_list.append(sys.argv[i + 1])
                    i += 2
                else:
                    log("DIR or FILE expected after -x (--ignore) option", LogLevel.ERROR)
                    return
            elif sys.argv[i] in ['-c', '--config']:
                if i + 1 < argc:
                    config_path = sys.argv[i + 1]
                    i += 2
                else:
                    log("FILE expected after -c (--config) option", LogLevel.ERROR)
            else:
                log(f"Unknown option: {sys.argv[i]}", LogLevel.ERROR)
                return

    suppressed_dirs, suppressed_files, suppressed_matches = parse_config(config_path)
    ignored_files = get_git_ignored_files(root_dir)

    # merge ignore_list into dirs/files as provided by -x
    for item in ignore_list:
        if Path(item).is_dir():
            suppressed_dirs.append(item)
        else:
            suppressed_files.append(item)

    dict_pattern = load_patterns_from_json()

    results = find_regex(root_dir, dict_pattern, suppressed_dirs, suppressed_files, suppressed_matches, ignored_files)
    log(json.dumps(results, indent=4, ensure_ascii=False), LogLevel.QUIET)


if __name__ == '__main__':
    main()
