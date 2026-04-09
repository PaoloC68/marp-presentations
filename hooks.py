"""Plugin lifecycle hooks for marp-presentations."""
from __future__ import annotations
import subprocess
import shutil
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent


def install():
    """Called by plugin installer after plugin is copied into place.

    1. Installs Node.js dependencies (marp-core + CodeMirror devDeps).
    2. Builds the local CodeMirror bundle (webui/codemirror-bundle.js).
    3. Optionally installs marp-cli globally for PDF/PPTX export.
    """
    # ── Step 1: npm install (including devDependencies for the build step) ──
    print("Installing Node.js dependencies...")
    try:
        result = subprocess.run(
            ["npm", "install"],
            capture_output=True, text=True, timeout=180,
            cwd=str(PLUGIN_DIR)
        )
        if result.returncode == 0:
            print("Node.js dependencies installed.")
        else:
            print(f"npm install failed: {result.stderr[:300]}")
            return
    except Exception as e:
        print(f"npm install error: {e}")
        return

    # ── Step 2: Build CodeMirror bundle ──────────────────────────────────
    bundle_path = PLUGIN_DIR / "webui" / "codemirror-bundle.js"
    if bundle_path.exists():
        print("CodeMirror bundle already present, skipping build.")
    else:
        print("Building CodeMirror bundle...")
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                capture_output=True, text=True, timeout=60,
                cwd=str(PLUGIN_DIR)
            )
            if result.returncode == 0:
                print("CodeMirror bundle built successfully.")
            else:
                print(f"Bundle build failed: {result.stderr[:300]}")
        except Exception as e:
            print(f"Bundle build error: {e}")

    # ── Step 3: Optionally install marp-cli globally (for PDF/PPTX export) ─
    if shutil.which("marp"):
        print("marp-cli already installed, skipping.")
        return

    print("Installing @marp-team/marp-cli globally via npm (for PDF/PPTX export)...")
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
