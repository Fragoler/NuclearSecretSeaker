from tabnanny import check

from tui import tui
from install import install
from ignore import ignore_path
from pathlib import Path

import sys
import argparse
import subprocess
import json


DEFAULT_CFG_PATH= ".nuclearss"

def main():
    parser = argparse.ArgumentParser(
        description="NuclearSS: The Utility that protects the git repository from leaks of tokens, passwords, secrets, and other confidential information.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nuclearss check /path    # Run default check /path directory
  nuclearss report /path   # Generate PDF report for path
  nuclearss tui data.json  # Launch TUI with JSON file
  nuclearss install /path  # Install git hooks for selected repository
  nuclearss install        # Install git hooks for current repository
  nuclearss ignore /path   # Ignore all secrets in the specified path"""
    )

    parser.add_argument("-c", "--config", default=f"{DEFAULT_CFG_PATH}",
                        help="Config file path (default: %(default)s in target directory)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=False)

    _check = subparsers.add_parser("check",
                          help="Run security scan on target path using nuclearss-seaker")
    _check.add_argument("path", nargs="?", default=".",
                        help="Target path to scan (default: current directory)")

    report = subparsers.add_parser("report",
                                   help="Generate PDF report from scan results")
    report.add_argument("path", nargs="?", default=".",
                        help="Target path to scan (default: current directory)")

    tui_parser = subparsers.add_parser("tui",
                                       help="Launch interactive TUI interface")
    tui_parser.add_argument("path", nargs="?",
                            help="JSON file path or read from stdin if omitted")

    install_parser = subparsers.add_parser("install",
                                           help="Install default config to path")
    install_parser.add_argument("path", nargs="?", default=".",
                                help="Installation path (default: current directory)")

    ignore_parser = subparsers.add_parser("ignore",
                                          help="Add path exclusion to config")
    ignore_parser.add_argument("path", nargs=1,
                               help="Path to ignore (e.g., 'node_modules/')")
    
    args = parser.parse_args()

    if not args.command:
        args.command = "check"
        args = parser.parse_args([args.command])
    
    path = args.path if args.path else "."
    config_file = args.config if args.config else str(Path(path) / DEFAULT_CFG_PATH)
    command = args.command if args.command else "check"

    if command == "ignore":
        if not args.path:
            print("Please specify a path to ignore.")
            sys.exit(1)
        
        for p in args.path:
            ignore_path(p, config_file)
        sys.exit(0)

    if command == "install":
        install(path)
        sys.exit(0)

    # Get json data from nuclearss-seaker
    str_data = ""
    if command in ["check", "report"]:
        result = subprocess.run(
            ["nuclearss-seaker", "-c", f"{config_file}", "-d", f"{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        str_data = result.stdout.strip()

    elif command == 'tui': 
        if args.path: 
            try:
                with open(args.path, "r") as f:
                    str_data = f.read()
            except FileNotFoundError:
                print("File not found.")
                sys.exit(1)
        else:
            str_data = sys.stdin.read()

    # End process if no data provided
    if not str_data:
        sys.exit(0)
    
    if command == "report":
        result = subprocess.run(
            ["nuclearss-pdf"],
            input=str_data,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            print("nuclearss-pdf failed:", result.stderr, file=sys.stderr)
        sys.exit(result.returncode)
    

    try:
        data = json.loads(str_data)
    except json.JSONDecodeError:
        print("Invalid JSON input.")
        sys.exit(1)
        
    code = tui(data, config_file)
    sys.exit(code)

if __name__ == "__main__":
    main()
