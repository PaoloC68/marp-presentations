from __future__ import annotations
from pathlib import Path
from helpers.api import ApiHandler, Input, Output, Request, Response

PRESENTATIONS_DIR = Path("/a0/usr/workdir/presentations")
PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)


class MarpList(ApiHandler):
    """POST /api/plugins/marp_presentations/marp_list
    Returns: { "ok": true, "files": [{"name": ..., "size": ..., "modified": ...}] }
    """

    async def process(self, input: Input, request: Request) -> Output:
        files = sorted(PRESENTATIONS_DIR.glob("*.md"))
        result = []
        for f in files:
            stat = f.stat()
            result.append({
                "name": f.name,
                "size": stat.st_size,
                "modified": int(stat.st_mtime),
            })
        return {"ok": True, "files": result}
