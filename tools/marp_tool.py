"""Marp Presentations tool — lets the agent generate, save, list, open and export presentations."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from helpers.tool import Tool, Response

PRESENTATIONS_DIR = Path("/a0/usr/workdir/presentations")
PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)


class MarpTool(Tool):
    """Tool for creating and managing Marp slide presentations.

    Actions:
      save   - save markdown content to a .md file
      load   - load markdown content from a file
      list   - list all saved presentations
      open   - open the viewer modal in the UI (returns open instruction)
      export - export a presentation to html/pdf/pptx
    """

    async def execute(self, action: str = "list", filename: str = "",
                      content: str = "", format: str = "html", **kwargs) -> Response:

        action = action.lower().strip()

        if action == "save":
            return self._save(filename, content)
        elif action == "load":
            return self._load(filename)
        elif action == "list":
            return self._list()
        elif action == "open":
            return self._open(filename)
        elif action == "export":
            return await self._export(filename, format)
        else:
            return Response(
                message=f"Unknown action '{action}'. Use: save, load, list, open, export",
                break_loop=False
            )

    # ------------------------------------------------------------------ #
    #  Private helpers                                                      #
    # ------------------------------------------------------------------ #

    def _safe_path(self, filename: str) -> Path:
        """Return a safe path inside PRESENTATIONS_DIR."""
        name = Path(filename).name  # strip any directory traversal
        if not name.endswith(".md"):
            name = name + ".md"
        return PRESENTATIONS_DIR / name

    def _save(self, filename: str, content: str) -> Response:
        if not filename:
            return Response(message="'filename' is required for save action.", break_loop=False)
        if not content:
            return Response(message="'content' is required for save action.", break_loop=False)
        path = self._safe_path(filename)
        path.write_text(content, encoding="utf-8")
        return Response(
            message=f"Presentation saved to {path}. Use action='open' with filename='{path.name}' to view it in the popup viewer.",
            break_loop=False
        )

    def _load(self, filename: str) -> Response:
        if not filename:
            return Response(message="'filename' is required for load action.", break_loop=False)
        path = self._safe_path(filename)
        if not path.exists():
            return Response(message=f"File not found: {path}", break_loop=False)
        content = path.read_text(encoding="utf-8")
        return Response(message=f"Content of {path.name}:\n\n{content}", break_loop=False)

    def _list(self) -> Response:
        files = sorted(PRESENTATIONS_DIR.glob("*.md"))
        if not files:
            return Response(
                message="No presentations found in /a0/usr/workdir/presentations/. Use action='save' to create one.",
                break_loop=False
            )
        listing = "\n".join(f"- {f.name} ({f.stat().st_size} bytes)" for f in files)
        return Response(message=f"Saved presentations:\n{listing}", break_loop=False)

    def _open(self, filename: str) -> Response:
        if not filename:
            return Response(
                message="Please specify a filename to open. Use action='list' to see available presentations.",
                break_loop=False
            )
        path = self._safe_path(filename)
        if not path.exists():
            return Response(message=f"File not found: {path.name}. Use action='save' to create it first.", break_loop=False)
        # Return a special marker that the UI extension can pick up
        return Response(
            message=f"Opening presentation '{path.name}' in the viewer. The slide popup should appear in the UI.",
            break_loop=False
        )

    async def _export(self, filename: str, fmt: str) -> Response:
        if not filename:
            return Response(message="'filename' is required for export action.", break_loop=False)
        path = self._safe_path(filename)
        if not path.exists():
            return Response(message=f"File not found: {path.name}", break_loop=False)

        fmt = fmt.lower().strip()
        if fmt not in ("html", "pdf", "pptx"):
            return Response(message=f"Unsupported format '{fmt}'. Choose from: html, pdf, pptx", break_loop=False)

        out_name = path.stem + "." + fmt
        out_path = PRESENTATIONS_DIR / out_name

        marp_bin = shutil.which("marp") or "npx"
        if marp_bin == "npx":
            cmd = ["npx", "--yes", "@marp-team/marp-cli", str(path), f"--{fmt}", "-o", str(out_path)]
        else:
            cmd = [marp_bin, str(path), f"--{fmt}", "-o", str(out_path)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return Response(
                    message=f"Exported successfully to {out_path}",
                    break_loop=False
                )
            else:
                err = result.stderr[:500] or result.stdout[:500]
                return Response(message=f"Export failed: {err}", break_loop=False)
        except subprocess.TimeoutExpired:
            return Response(message="Export timed out after 120 seconds.", break_loop=False)
        except Exception as e:
            return Response(message=f"Export error: {e}", break_loop=False)
