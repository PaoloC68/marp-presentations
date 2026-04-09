from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from helpers.api import ApiHandler, Input, Output, Request, Response

PRESENTATIONS_DIR = Path("/a0/usr/workdir/presentations")
PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_FORMATS = ("html", "pdf", "pptx")


class MarpExport(ApiHandler):
    """POST /api/plugins/marp_presentations/marp_export
    Body: { "filename": "my-deck.md", "format": "pdf" }
    Returns: { "ok": true, "output": "/path/to/file.pdf" }
    """

    async def process(self, input: Input, request: Request) -> Output:
        filename: str = (input.get("filename") or "").strip()
        fmt: str = (input.get("format") or "html").strip().lower()

        if not filename:
            return Response("'filename' is required", 400)
        if fmt not in SUPPORTED_FORMATS:
            return Response(f"Unsupported format '{fmt}'. Choose from: {', '.join(SUPPORTED_FORMATS)}", 400)

        name = Path(filename).name
        if not name.endswith(".md"):
            name += ".md"

        src = PRESENTATIONS_DIR / name
        if not src.exists():
            return Response(f"File not found: {name}", 404)

        out_name = src.stem + "." + fmt
        out_path = PRESENTATIONS_DIR / out_name

        marp_bin = shutil.which("marp")
        if marp_bin:
            cmd = [marp_bin, str(src), f"--{fmt}", "-o", str(out_path)]
        else:
            cmd = ["npx", "--yes", "@marp-team/marp-cli", str(src), f"--{fmt}", "-o", str(out_path)]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return {"ok": True, "output": str(out_path), "filename": out_name}
            err = (result.stderr or result.stdout or "Unknown error")[:600]
            return Response(f"Export failed: {err}", 500)
        except subprocess.TimeoutExpired:
            return Response("Export timed out (120s). PDF/PPTX require Chromium — first run may take longer.", 500)
        except Exception as e:
            return Response(f"Export error: {e}", 500)
