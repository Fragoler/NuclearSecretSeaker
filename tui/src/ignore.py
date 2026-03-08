from pathlib import Path

import os


def ignore_path(path, config_path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Invalid path: {path}")

    if os.path.isfile(path):
        entry = f"\nfile: {str(Path(path).resolve())}"
    elif os.path.isdir(path):
        entry = f"\ndir: {str(Path(path).resolve())}"
    else:
        raise ValueError(f"Unknown path type: {path}")

    with open(config_path, "a", encoding="utf-8") as cfg:
        cfg.write(entry)

def ignore_file(path, config_path, force=False):
    if not os.path.exists(path) and not force:
        raise FileNotFoundError(f"Invalid path: {path}")

    entry = f"\nfile: {str(Path(path).resolve())}"

    with open(config_path, "a", encoding="utf-8") as cfg:
        cfg.write(entry)


def ignore_text(text, config_path):
    entry = f"text: {text}\n"
    with open(config_path, "a", encoding="utf-8") as cfg:
        cfg.write(entry)
