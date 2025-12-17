# MCP Codebase Reasoning Engine

A **local Model Context Protocol (MCP) server** that allows LLM clients
(such as **Claude Desktop**) to explore, understand, and reason about
an entire codebase using structured tools.

This project works **entirely on your local machine** and is suitable for
private, unpushed, or confidential repositories.

---

## 🚀 Why this project?

LLMs struggle with real-world codebases because:
- the full project rarely fits into context
- private/local code cannot be uploaded
- understanding requires exploration, not dumping files

This MCP server solves that by allowing an LLM to:
- discover files dynamically
- search across the codebase
- read files on demand
- build understanding incrementally

All communication happens via **MCP tool calls**.

---

## 🧠 High-Level Architecture

```
LLM Client (Claude Desktop)
        ↓
Model Context Protocol (MCP)
        ↓
Codebase Reasoning Engine (this server)
        ↓
Local Codebase (any folder on your system)
```

---

## ✨ Features

- MCP-compliant server
- Works with Claude Desktop, Autonomous AI Agents
- Codebase-wide file discovery
- Text search across files
- File content inspection
- Local-first (no cloud dependency)
- Fast, reproducible setup using `uv`

---

## 📁 Repository Structure

```
CODEBASE-REASONING-ENGINE/
│
├── main.py                # file having all the mcp tools 
├── sample_codebase/       # put your project/codebase in this folder 
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
└── .python-version
```

---

## 🧪 Sample Codebase

The `sample_codebase/` directory is included **only for demonstration
and local testing**.

The MCP server is **not tied** to this folder and can be pointed to
**any codebase** on your machine.

---

## ⚙️ Prerequisites

- Python >=3.13
- `uv` installed

Install uv:
```
pip install uv
```

Verify:
```
uv --version
```

---

## 📦 Setup

```
git clone <your-repo-url>
cd CODEBASE-REASONING-ENGINE
uv init .
uv add fastmcp
```

---

## ▶️ Run the MCP Server

```
uv run --with fastmcp fastmcp run main.py
```

---

## 🧩 Claude Desktop Integration (Windows Example)

```
uv run fastmcp install claude-desktop main.py
```

```json
{
  "Codebase_reasoning_engine": {
    "command": "uv",       // replace it with your uv path
    "args": [
      "run",
      "--with",
      "fastmcp",
      "fastmcp",
      "run",
      "/main.py"           // replace this with the path of your main.py file
    ]
  }
}
```

Restart Claude Desktop after adding this.

---

## 🛣️ Future Enhancements

- Modular tools
- Smarter indexing
- Dependency graphs
- Semantic search

---

## 📜 License

MIT License
