import os

def ignore_path(path, config_path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Invalid path: {path}")

    if os.path.isfile(path):
        entry = f"file: {path}\n"
    elif os.path.isdir(path):
        entry = f"dir: {path}\n"
    else:
        raise ValueError(f"Unknown path type: {path}")

    with open(config_path, "a", encoding="utf-8") as cfg:
        cfg.write(entry)


def ignore_text(text, config_path):
    entry = f"text: {text}\n"
    with open(config_path, "a", encoding="utf-8") as cfg:
        cfg.write(entry)
