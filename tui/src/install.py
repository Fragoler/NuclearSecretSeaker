from pathlib import Path

import os
import sys

DEFAULT_CFG = '''dir: .idea'''

PRE_COMMIT_HOOK = '''#!/usr/bin/env sh

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

PRE_PUSH_HOOK = '''#!/usr/bin/env sh

output=$(nuclearss-seaker 2>/dev/null)

if [ -z "$output" ]; then
    exit 0
fi

if ! exec < /dev/tty 2>/dev/null; then
    echo "Error: there is no access to the terminal (/dev/tty is unavailable). The push is blocked."
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
    commit_hook_file = hooks_dir / "pre-commit"
    push_hook_file = hooks_dir / "pre-push"
    
    if commit_hook_file.exists() or push_hook_file.exists():
        print(f"Warning: hooks already exists")
        response = input("Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Installation cancelled.")
            sys.exit(0)

    try:
        commit_hook_file.write_text(PRE_COMMIT_HOOK)
        push_hook_file.write_text(PRE_PUSH_HOOK)
    except Exception as e:
        print(f"Error writing hook: {e}")
        sys.exit(1)

    os.chmod(commit_hook_file, 0o755)
    os.chmod(push_hook_file, 0o755)

    config_path = repo_path / ".nuclearss"
    if not config_path.exists():
        config_path.write_text(DEFAULT_CFG)

    print(f"   Gits hooks installed successfully!")
    print(f"   Now nuclearss runs on every 'git commit' and 'git push'.")
