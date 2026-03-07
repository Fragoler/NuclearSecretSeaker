from tui import tui
from install import install

import sys
import argparse
import subprocess
import json

from ignore import ignore_path

DEFAULT_CFG_PATH= ".nuclearss"

def main():
    parser = argparse.ArgumentParser(description="Process JSON input.")

    parser.add_argument("command", nargs="?", choices=["report", "tui", "install", "ignore"], help="Command: report, tui, ignore <path>, or install <path>")
    parser.add_argument("path", nargs="?")
    
    parser.add_argument("-c", "--config", type=str, help=f"Specify config file (default: {DEFAULT_CFG_PATH})")
    
    args = parser.parse_args()

    config_file = args.config if args.config else DEFAULT_CFG_PATH

    if args.command == "ignore":
        if not args.path:
            print("Please specify a path to ignore.")
            sys.exit(1)
            
        ignore_path(args.path, config_file)
        sys.exit(0)

    if args.command == "install":
        install(args.path if args.path else ".")
        sys.exit(0)

    str_data = ""
    if args.command != "tui":
        result = subprocess.run(
            ["nuclearss-seaker", "-c", f"{config_file}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        str_data = result.stdout.strip()
        if not str_data:
            sys.exit(0)
    else: # TUI mode enables
        if args.path: 
            try:
                with open(args.path, "r") as f:
                    str_data = f.read()
            except FileNotFoundError:
                print("File not found.")
                sys.exit(1)
        else:
            str_data = sys.stdin.read()
            if not str_data:
                sys.exit(0)
    
    if args.command == "report":
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
        
    tui(data, config_file)

if __name__ == "__main__":
    main()
