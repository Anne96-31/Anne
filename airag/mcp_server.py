"""MCP server：讓 Claude Code / Claude Desktop 等 AI 工具直接查詢你的 AI 學習筆記。

MCP（Model Context Protocol）是一個標準介面：你把功能包成「tool」或「resource」，
任何支援 MCP 的 AI 客戶端都能看到工具說明、自己決定什麼時候呼叫。
- tool：模型主動呼叫的動作（搜尋、問答）→ 這裡提供 search_notes / ask_notes / list_digests / get_digest
- resource：可被讀取的資料（像檔案）→ 這裡提供 notes://latest 與 notes://{date}

設計原則：全部唯讀、所有輸入都驗證（日期格式、筆數上限），只能讀 digests/ 底下的 YYYY-MM-DD.md。

注意：這是 mcp SDK 2.x 的寫法。網路上舊教學的 `FastMCP` 在 2.x 已改名為 `MCPServer`。

啟動（stdio，給本機 AI 客戶端用）：python -m airag.mcp_server
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, Field
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

from . import answer as rag
from .corpus import DATE_FILE_RE, digest_files
from .index import PRIORITIES, load_index

DEFAULT_DIGEST_DIR = Path(__file__).resolve().parent.parent / "digests"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_K = 20
READ_ONLY = ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True,
                            open_world_hint=False)

INSTRUCTIONS = """這個 server 收錄使用者每天閱讀的「AI & Data 產業摘要」（約最近 30 天，每天 10-14 則），
主題聚焦在 Data Engineer 轉職 AI Engineer：LLM 應用、RAG、Agent、MCP、LLMOps、資料工程。
使用者問到「我之前讀過的」「最近有哪些…」或需要產業案例時，先用 search_notes 找相關筆記，
引用時附上文章標題、日期與連結。"""


class NoteHit(BaseModel):
    """一筆搜尋結果。定義成 pydantic model，MCP 會自動產生 output schema 給客戶端。"""
    chunk_id: str
    date: str
    kind: str = Field(description="article（文章）或 briefing（當日重點）")
    title: str
    url: str
    source: str
    priority: str = Field(description="must_read / skim / reference")
    tags: list[str]
    score: float = Field(description="BM25 相關度分數，越高越相關")
    matched_terms: list[str] = Field(description="命中的查詢詞，用來解釋為什麼找到這筆")
    snippet: str


class SearchResult(BaseModel):
    query: str
    count: int
    results: list[NoteHit]


class DigestInfo(BaseModel):
    date: str
    articles: int
    briefing: str


def _check_date(value: str | None, name: str) -> str | None:
    if value is None or value == "":
        return None
    if not DATE_RE.match(value):
        raise ToolError(f"{name} 必須是 YYYY-MM-DD 格式，收到：{value!r}")
    return value


def _check_k(k: int) -> int:
    if not 1 <= k <= MAX_K:
        raise ToolError(f"k 必須介於 1 到 {MAX_K}")
    return k


def build_server(digest_dir: Path | str | None = None) -> MCPServer:
    digest_dir = Path(digest_dir or os.environ.get("AIRAG_DIGEST_DIR") or DEFAULT_DIGEST_DIR)
    server = MCPServer("anne-ai-notes", instructions=INSTRUCTIONS)

    def read_digest(date: str) -> str:
        _check_date(date, "date")
        path = digest_dir / f"{date}.md"          # 檔名只由驗證過的日期組成，不會穿越目錄
        if not path.is_file():
            raise ToolError(f"沒有 {date} 的摘要（只保留最近約 30 天）。可先用 list_digests 查可用日期。")
        return path.read_text(encoding="utf-8")

    @server.tool(annotations=READ_ONLY)
    def search_notes(
        query: str,
        k: int = 5,
        date_from: str | None = None,
        date_to: str | None = None,
        priority: str | None = None,
        tag: str | None = None,
    ) -> SearchResult:
        """搜尋使用者的 AI 學習筆記（每日 AI & Data 產業摘要），回傳最相關的文章與連結。

        Args:
            query: 要找的主題，中英文皆可，例如「RAG 評估」「MCP 案例」「vLLM」
            k: 回傳筆數（1-20）
            date_from: 起始日期 YYYY-MM-DD（含）
            date_to: 結束日期 YYYY-MM-DD（含）
            priority: must_read（必讀）/ skim（快速瀏覽）/ reference（存參考）
            tag: 只看含有此標籤的文章，例如「RAG」「評估」
        """
        if not query.strip():
            raise ToolError("query 不能是空的")
        if priority and priority not in PRIORITIES:
            raise ToolError(f"priority 只能是 {PRIORITIES}")
        hits = load_index(digest_dir).search(
            query, k=_check_k(k), date_from=_check_date(date_from, "date_from"),
            date_to=_check_date(date_to, "date_to"), priority=priority, tag=tag,
        )
        return SearchResult(query=query, count=len(hits), results=[NoteHit(**h.to_dict()) for h in hits])

    @server.tool(annotations=READ_ONLY)
    def ask_notes(question: str, k: int = 5) -> str:
        """根據筆記回答問題，附 [S#] 來源引用。有 ANTHROPIC_API_KEY 時用 Claude 生成，否則列出最相關的筆記。

        如果你自己就是 LLM，通常用 search_notes 拿原始資料自己整理更好；這個工具給不想自己整理的客戶端用。
        """
        if not question.strip():
            raise ToolError("question 不能是空的")
        result = rag.answer_question(load_index(digest_dir), question, k=_check_k(k))
        return result.to_markdown()

    @server.tool(annotations=READ_ONLY)
    def list_digests(limit: int = 14) -> list[DigestInfo]:
        """列出可用的每日摘要（新到舊），含日期、文章數與當天重點的開頭。"""
        if not 1 <= limit <= 60:
            raise ToolError("limit 必須介於 1 到 60")
        index = load_index(digest_dir)
        out = []
        for path in reversed(digest_files(digest_dir)[-limit:]):
            date = DATE_FILE_RE.match(path.name).group(1)
            day = [c for c in index.chunks if c.date == date]
            briefing = next((c.summary for c in day if c.kind == "briefing"), "")
            out.append(DigestInfo(
                date=date,
                articles=sum(c.kind == "article" for c in day),
                briefing=briefing[:150] + ("…" if len(briefing) > 150 else ""),
            ))
        return out

    @server.tool(annotations=READ_ONLY)
    def get_digest(date: str) -> str:
        """取得某一天完整的摘要 Markdown（日期格式 YYYY-MM-DD）。"""
        return read_digest(date)

    @server.resource("notes://latest", mime_type="text/markdown")
    def latest_digest() -> str:
        """最新一天的完整摘要。"""
        files = digest_files(digest_dir)
        if not files:
            raise ToolError("目前沒有任何摘要")
        return files[-1].read_text(encoding="utf-8")

    @server.resource("notes://{date}", mime_type="text/markdown")
    def digest_by_date(date: str) -> str:
        """指定日期的完整摘要。"""
        return read_digest(date)

    return server


def main() -> None:
    build_server().run("stdio")


if __name__ == "__main__":
    main()
