from ignore import ignore_text, ignore_path

import os


def get_color(level):
    intensity = level / 255.0

    if intensity < 0.33:
        r, g, b = 0, int(255 * (1 - intensity * 3)), 0
    elif intensity < 0.66:
        r, g, b = int(255 * ((intensity - 0.33) * 3)), int(255 * (1 - (intensity - 0.33) * 3)), 0
    else:
        r, g, b = 255, 0, int(255 * (1 - (intensity - 0.66) * 3))

    return f"\033[38;2;{int(r)};{int(g)};{int(b)}m"

def tui(data, config_file):
    for item in data:
        file_path = item.get("file")
        description = item.get("description")
        snippet = item.get("snippet")
        secret = item.get("secret")
        level = item.get("level")

        if not file_path or not description or level is None:
            continue

        color = get_color(level)
        reset = "\033[0m"
        colored_secret = f"{color}\"{secret}\"{reset}"

        print(f"\n{'='*60}")
        print(f"Potential secret detected! In {file_path}:")
        print(f"  File: {file_path}") 
        print(f"  Type: {description}")
        print(f"  Text: \n{'-'*20}\n{snippet}\n{'-'*20}")
        while True:
            action = input(f"\nDo you want to ignore \"{colored_secret}\" issue? [y/N/f/?]: ").strip().lower()
            if action == "y":
                ignore_text(secret, config_file)
                break
            elif action == "f":
                ignore_path(file_path, config_file)
                break
            elif action == "?":
                print("\nOptions:")
                print("  y - Ignore this specific secret")
                print("  f - Ignore all file")
                print("  ? - Show this help message")
                print("  N or [Enter] - Do not ignore and interrupt the process")
            else:
                return 0

    return 0


def add_to_ignore(file_path):
    pass # Placeholder
