from __future__ import annotations
from pathlib import Path
from helpers.api import ApiHandler, Input, Output, Request, Response

PRESENTATIONS_DIR = Path("/a0/usr/workdir/presentations")
PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)


class MarpSave(ApiHandler):
    """POST /api/plugins/marp_presentations/marp_save
    Body: { "filename": "my-deck.md", "content": "# Slide..." }
    Returns: { "ok": true, "path": "..." }
    """

    async def process(self, input: Input, request: Request) -> Output:
        filename: str = (input.get("filename") or "").strip()
        content: str = input.get("content") or ""

        if not filename:
            return Response("'filename' is required", 400)
        if not content:
            return Response("'content' is required", 400)

        name = Path(filename).name
        if not name.endswith(".md"):
            name += ".md"

        path = PRESENTATIONS_DIR / name
        path.write_text(content, encoding="utf-8")
        return {"ok": True, "path": str(path), "filename": name}
