from tui import tui
from install import install

import argparse

def main():
    parser = argparse.ArgumentParser(description="Process JSON input.")
    parser.add_argument("--file", type=str, help="Path to JSON file.")
    parser.add_argument("-t", action="store_true", help="Activate TUI mode.")
    parser.add_argument("-i", "--install", type=str, help="Path to directory for repository installation.")
    args = parser.parse_args()

    if args.install:
        install(args.install)
    elif args.t:
        tui(args.file)

if __name__ == "__main__":
    main()
