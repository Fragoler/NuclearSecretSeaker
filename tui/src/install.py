from pathlib import Path

import os
import sys

DEFAULT_CFG = '''
dir: .git
dir: .idea
dir: .venv
dir: node_modules'''

HOOK_CONTENT = '''#!/usr/bin/env sh

output=$(nuclearss-seaker 2>/dev/null)

if [ -z "$output" ]; then
    exit 0
fi

if ! exec < /dev/tty 2>/dev/null; then
    echo "Error: there is no access to the terminal (/dev/tty is unavailable). The commit is blocked."
    exit 1
fi

tmpfile=$(mktemp)
echo "$output" > "$tmpfile"
nuclearss tui "$tmpfile"

exit $?
'''

def install(repo_path):
    repo_path = Path(repo_path).resolve()

    git_dir = repo_path / ".git"
    if not git_dir.exists():
        print(f"Error: '{repo_path}' is not a Git repository")
        sys.exit(1)

    hooks_dir = git_dir / "hooks"
    hook_file = hooks_dir / "pre-commit"

    # Проверяем, существует ли уже хук
    if hook_file.exists():
        print(f"Warning: pre-commit hook already exists at {hook_file}")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Installation cancelled.")
            sys.exit(0)

    try:
        hook_file.write_text(HOOK_CONTENT)
    except Exception as e:
        print(f"Error writing hook: {e}")
        sys.exit(1)

    os.chmod(hook_file, 0o755)

    config_path = repo_path / ".nuclearss"
    if not config_path.exists():
        config_path.write_text(DEFAULT_CFG)

    print(f"   Git hook installed successfully!")
    print(f"   Path: {hook_file}")
    print(f"   Now nuclearss runs on every 'git commit'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        install(sys.argv[1])
    else:
        install(".")
