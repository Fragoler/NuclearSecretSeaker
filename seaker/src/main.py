from ignored import get_git_ignored_files
from logger import LogLevel, log
from config import parse_config
from patterns import load_patterns_from_json
from scanner import find_regex

from pathlib import Path

import argparse
import json

DEFAULT_CONFIG_PATH = ".nuclearss"
DEFAULT_ROOT_DIR = "."


def main():
    parser = argparse.ArgumentParser(prog="nuclearss-seaker", description="Search for secrets using configured patterns")
    parser.add_argument('-d', '--dir', dest='dir', default=DEFAULT_ROOT_DIR,
                        help=f"Pick root directory (default: {DEFAULT_ROOT_DIR})")
    parser.add_argument('-c', '--config', dest='config', default=DEFAULT_CONFIG_PATH,
                        help=f"Specify config file (default: {DEFAULT_CONFIG_PATH})")
    parser.add_argument('-x', '--ignore', dest='ignore', action='append', default=[],
                        help='Ignore file or directory; may be specified multiple times')

    args = parser.parse_args()
    root_dir = args.dir
    config_path = args.config
    ignore_list = args.ignore or []

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
