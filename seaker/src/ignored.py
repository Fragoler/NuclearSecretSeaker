from logger import log, LogLevel

import subprocess


def get_git_ignored_files(root_dir: str) -> list[str]:
    try:
        result = subprocess.run(
            ['git', 'ls-files', '-o', '-i', '--exclude-standard'],
            cwd=root_dir,
            capture_output=True,
            text=True,
            check=True
        )

        ignored_files = [_path.strip() for _path in result.stdout.strip().split('\n') if _path.strip()]

        return ignored_files

    except subprocess.CalledProcessError as e:
        log(f"Git exception: {e}", LogLevel.ERROR)
        log(f"stderr: {e.stderr}", LogLevel.ERROR)
        return []
    except FileNotFoundError:
        log("Git is not installed or not found in PATH.", LogLevel.ERROR)
        return []
