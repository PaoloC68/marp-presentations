"""Plugin lifecycle hooks for marp-presentations."""
from __future__ import annotations
import subprocess
import shutil


def install():
    """Called by plugin installer after plugin is copied into place.
    Attempts to install marp-cli globally via npm for PDF/PPTX export.
    Falls back gracefully to npx on-demand if npm install fails.
    """
    if shutil.which("marp"):
        print("marp-cli already installed, skipping.")
        return

    print("Installing @marp-team/marp-cli globally via npm...")
    try:
        result = subprocess.run(
            ["npm", "install", "-g", "@marp-team/marp-cli"],
            capture_output=True, text=True, timeout=180
        )
        if result.returncode == 0:
            print("marp-cli installed successfully.")
        else:
            print(f"marp-cli global install failed (will use npx on demand): {result.stderr[:300]}")
    except Exception as e:
        print(f"Could not install marp-cli (will use npx on demand): {e}")
