"""把筆記用到的 Markdown 子集轉成 Notion 區塊。

支援：# / ## / ### 標題、段落、- 清單、1. 清單、> 提示框、``` 程式碼、
| 表格 |、---、<details><summary> 可收合區塊，以及行內 **粗體**、`程式碼`、[連結](url)。
第一個 # 標題當作頁面標題，不放進內文。
"""

from __future__ import annotations

import re

from aidigest.notion import bullet, callout, divider, heading, numbered, paragraph, rich_text

_INLINE_RE = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\((https?://[^)\s]+)\)")
_NUMBERED_RE = re.compile(r"^\d+\.\s+")
_SUMMARY_RE = re.compile(r"<summary>(.*?)</summary>", re.S)

# Notion 程式碼區塊只接受固定的語言名稱
_LANGUAGES = {"": "plain text", "text": "plain text", "py": "python", "sh": "shell",
              "bash": "bash", "python": "python", "sql": "sql", "json": "json", "yaml": "yaml"}

_CALLOUT_STYLES = {"⚠️": "yellow_background", "🎯": "green_background", "💡": "blue_background"}


def inline(text: str) -> list[dict]:
    """把一行文字切成 Notion rich_text，處理粗體、行內程式碼與連結。"""
    if not text:
        return []
    out: list[dict] = []
    pos = 0
    for m in _INLINE_RE.finditer(text):
        if m.start() > pos:
            out += rich_text(text[pos:m.start()])
        bold, code, label, url = m.groups()
        if bold is not None:
            out += _inline_bold(bold)
        elif code is not None:
            out += rich_text(code, code=True)
        else:
            out += rich_text(label, link=url)
        pos = m.end()
    if pos < len(text) or not out:
        out += rich_text(text[pos:])
    return out


def _inline_bold(text: str) -> list[dict]:
    """粗體裡可能還有 `code`，兩種標註要疊加。"""
    parts = inline(text)
    for item in parts:
        item["annotations"]["bold"] = True
    return parts


def code_block(code: str, language: str) -> dict:
    lang = _LANGUAGES.get(language.strip().lower(), "plain text")
    return {"object": "block", "type": "code",
            "code": {"rich_text": rich_text(code), "language": lang}}


def table_block(rows: list[list[str]]) -> dict:
    width = max(len(r) for r in rows)
    children = []
    for row in rows:
        cells = row + [""] * (width - len(row))
        children.append({"object": "block", "type": "table_row",
                         "table_row": {"cells": [inline(c) for c in cells]}})
    return {"object": "block", "type": "table",
            "table": {"table_width": width, "has_column_header": True,
                      "has_row_header": False, "children": children}}


def callout_block(text: str) -> dict:
    for emoji, color in _CALLOUT_STYLES.items():
        if text.startswith(emoji):
            body = text[len(emoji):].strip()
            block = callout("", emoji=emoji, color=color)
            block["callout"]["rich_text"] = inline(body)
            return block
    block = callout("")
    block["callout"]["rich_text"] = inline(text)
    return block


def toggle_block(summary: str, children: list[dict]) -> dict:
    return {"object": "block", "type": "toggle",
            "toggle": {"rich_text": inline(summary), "children": children}}


def _split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?", line.strip()))


def parse(md: str) -> tuple[str, list[dict]]:
    """回傳 (頁面標題, 區塊列表)。"""
    lines = md.splitlines()
    title = ""
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            lines = lines[:i] + lines[i + 1:]
            break
    return title, _parse_lines(lines)


def _parse_lines(lines: list[str]) -> list[dict]:
    blocks: list[dict] = []
    para: list[str] = []
    i = 0

    def flush() -> None:
        if para:
            blocks.append(paragraph(inline(" ".join(para))))
            para.clear()

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if line.startswith("```"):
            flush()
            lang = line[3:]
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            blocks.append(code_block("\n".join(lines[i + 1:j]), lang))
            i = j + 1
            continue

        if line.startswith("<details"):
            flush()
            depth, j = 1, i + 1
            while j < len(lines) and depth:
                s = lines[j].strip()
                depth += s.startswith("<details") - s.startswith("</details>")
                j += 1
            inner = "\n".join(lines[i + 1:j - 1])
            m = _SUMMARY_RE.search(inner)
            summary = m.group(1).strip() if m else "展開"
            if m:
                inner = inner[:m.start()] + inner[m.end():]
            blocks.append(toggle_block(summary, _parse_lines(inner.splitlines())))
            i = j
            continue

        if line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not _is_separator(lines[i]):
                    rows.append(_split_row(lines[i]))
                i += 1
            blocks.append(table_block(rows))
            continue

        if not line:
            flush()
        elif line.startswith("### "):
            flush()
            blocks.append(heading(line[4:].strip(), 3))
        elif line.startswith("## "):
            flush()
            blocks.append(heading(line[3:].strip(), 2))
        elif line == "---":
            flush()
            blocks.append(divider())
        elif line.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            blocks.append(callout_block(" ".join(quote)))
            continue
        elif line.startswith("- "):
            flush()
            blocks.append(bullet(inline(line[2:].strip())))
        elif _NUMBERED_RE.match(line):
            flush()
            blocks.append(numbered(inline(_NUMBERED_RE.sub("", line, count=1))))
        else:
            para.append(line)
        i += 1

    flush()
    return blocks
