from __future__ import annotations
import json
import subprocess
from pathlib import Path
from helpers.api import ApiHandler, Input, Output, Request, Response

RENDER_SCRIPT = str(Path(__file__).parent.parent / "helpers" / "render.js")


class MarpRender(ApiHandler):
    """POST /api/plugins/marp-presentations/marp_render
    Body: { "markdown": "---\nmarp: true\n---\n# Slide..." }
    Returns: { "ok": true, "html": "...", "css": "...", "slideCount": N }
    """

    async def process(self, input: Input, request: Request) -> Output:
        markdown: str = input.get("markdown") or ""
        if not markdown:
            return Response("'markdown' is required", 400)

        try:
            result = subprocess.run(
                ["node", RENDER_SCRIPT],
                input=json.dumps({"markdown": markdown}),
                capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                err = result.stderr[:500] or result.stdout[:500]
                return Response(f"Render failed: {err}", 500)

            data = json.loads(result.stdout)
            if "error" in data:
                return Response(f"Render error: {data['error']}", 500)

            return {
                "ok": True,
                "html": data["html"],
                "css": data["css"],
                "slideCount": data["slideCount"],
            }
        except subprocess.TimeoutExpired:
            return Response("Render timed out (30s)", 500)
        except Exception as e:
            return Response(f"Render error: {e}", 500)
