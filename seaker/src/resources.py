import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller.

    Behavior:
    - If running in a PyInstaller bundle (sys._MEIPASS present), prefer the
      file inside the bundle (by basename), otherwise fall back to the
      provided absolute path or current working directory.
    - If not frozen, return the absolute path for absolute inputs or join
      cwd with the relative path.
    """
    base_path = getattr(sys, '_MEIPASS', None)

    if base_path:
        if os.path.isabs(relative_path):
            return os.path.join(base_path, os.path.basename(relative_path))
        return os.path.join(base_path, relative_path)
    
    if os.path.isabs(relative_path):
        return relative_path
    return os.path.join(os.path.abspath('.'), relative_path)
