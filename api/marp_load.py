from __future__ import annotations
from pathlib import Path
from helpers.api import ApiHandler, Input, Output, Request, Response

PRESENTATIONS_DIR = Path("/a0/usr/workdir/presentations")
PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)


class MarpLoad(ApiHandler):
    """POST /api/plugins/marp_presentations/marp_load
    Body: { "filename": "my-deck.md" }
    Returns: { "ok": true, "filename": "...", "content": "..." }
    """

    async def process(self, input: Input, request: Request) -> Output:
        filename: str = (input.get("filename") or "").strip()
        if not filename:
            return Response("'filename' is required", 400)

        name = Path(filename).name
        if not name.endswith(".md"):
            name += ".md"

        path = PRESENTATIONS_DIR / name
        if not path.exists():
            return Response(f"File not found: {name}", 404)

        content = path.read_text(encoding="utf-8")
        return {"ok": True, "filename": name, "content": content}
