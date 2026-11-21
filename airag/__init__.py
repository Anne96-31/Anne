"""airag：把每日 AI & Data 摘要變成可查詢的學習筆記（RAG + MCP）。

- corpus.py      第 1 步：切塊（Markdown → 帶 metadata 的 chunk）
- index.py       第 2 步：檢索（中英混合 BM25）
- evaluate.py    第 3 步：評估（hit@k、MRR、消融實驗）
- answer.py      第 4 步：生成（Claude + 引用驗證 + 退路）
- mcp_server.py  第 5 步：MCP server（讓 AI 工具直接查筆記）

教學文件：docs/rag-mcp-tutorial.md
"""
