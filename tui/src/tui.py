import json
import os
import sys


def tui(file_json=None):
    if file_json: # Read JSON input from file
        try:
            with open(file_json, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print("Invalid JSON file or file not found.")
            sys.exit(1)
    else: # Read JSON input from stdin
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("Invalid JSON input.")
            sys.exit(1)

    for item in data:
        file_path = item.get("file")
        description = item.get("description")
        level = item.get("level")

        if not file_path or not description or level is None:
            continue

        print(f"Potential secret detected in {file_path}:")
        print(f"  Description: {description}")
        print(f"  Severity Level: {level}")

        while True:
            action = input("Do you want to ignore this issue? [y/N]: ").strip().lower()
            if action == "y":
                add_to_ignore(file_path)
                break
            else:
                print(f"File path: {os.path.abspath(file_path)}")
                sys.exit(1)


def add_to_ignore(file_path):
    pass # Placeholder
