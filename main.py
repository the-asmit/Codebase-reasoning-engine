from fastmcp import FastMCP
import os

from pathlib import Path 
import re 

mcp = FastMCP("Codebase MCP - Stage 1")

CODEBASE_DIR = "./codebase" # ADD THE PATH OF CODEBASE FOLDER HERE

ALLOWED_EXTENSIONS = {
    ".py", ".cpp", ".c", ".h", ".hpp", ".js", ".ts"
}


@mcp.tool()
def list_files():
    root = Path(CODEBASE_DIR).resolve()

    if not root.exists() or not root.is_dir(): 
        return []

    files = []

    for path in root.rglob("*"): 
        if path.is_file() and path.suffix in ALLOWED_EXTENSIONS:
            files.append(str(path.relative_to(root)))

    files.sort()
    return files


@mcp.tool()
def explain_file(path: str):
    root = Path(CODEBASE_DIR).resolve()

    if not path or path.startswith("/") or ".." in path:
        return {"error": "Invalid path"}

    file_path = (root / path).resolve()

    if not file_path.exists() or not file_path.is_file():
        return {"error": "File not found or not allowed"}

    if file_path.suffix not in ALLOWED_EXTENSIONS:
        return {"error": "File extension not allowed"}

    if root not in file_path.parents:
        return {"error": "Access outside codebase is not allowed"}

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"error": "Failed to read file"}

    if not content.strip():
        return {
            "file": path,
            "summary": "This file is empty.",
            "key_elements": []
        }

    # ---------- heuristic extraction ----------

    lines = content.splitlines() 
    total_lines = len(lines)

    
    function_pattern = re.compile(
        r"^\s*(?:public|private|protected|static|inline)?\s*"
        r"[a-zA-Z_][a-zA-Z0-9_<>,\s]*\s+"
        r"([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
        re.MULTILINE
    )

    functions = function_pattern.findall(content)
    unique_functions = sorted(set(functions))

    lowered = content.lower()

    
    if any(k in lowered for k in ["auth", "login", "token", "password"]):
        topic = "authentication-related logic"
    elif any(k in lowered for k in ["biome", "block", "entity", "world"]):
        topic = "game-world or domain-specific logic"
    elif any(k in lowered for k in ["sort", "merge", "quick", "heap"]):
        topic = "sorting or data-processing logic"
    elif len(unique_functions) >= 8:
        topic = "multiple related operations"
    else:
        topic = "general utility logic"

    summary = (
        f"This file contains approximately {total_lines} lines of code "
        f"and defines {len(unique_functions)} function(s), primarily related to {topic}."
    )

    return {
        "file": path,
        "summary": summary,
        "key_elements": unique_functions[:10]
    }



@mcp.tool()
def search_code(query: str):
    if not query or not query.strip():
        return []

    root = Path(CODEBASE_DIR).resolve()
    query_lower = query.lower()

    MAX_HITS_PER_FILE = 3
    MAX_FALLBACK_LINES = 25

    results = []

    def is_function_start(line: str):
        return (
            re.search(r"\b(def|function)\b", line) or
            re.search(r"\b[a-zA-Z_][a-zA-Z0-9_<>\s\*]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(", line)
        )

    def indentation(line: str):
        return len(line) - len(line.lstrip())

    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in ALLOWED_EXTENSIONS:
            continue

        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            continue

        total_lines = len(lines)
        hits = 0

        for idx, line in enumerate(lines):
            if query_lower not in line.lower():
                continue

            confidence = 0.3
            start = idx
            end = idx

            # -------- Attempt 1: function boundary detection --------
            func_start = None
            base_indent = indentation(lines[idx])

            for i in range(idx, -1, -1):
                if is_function_start(lines[i]):
                    func_start = i
                    base_indent = indentation(lines[i])
                    break

            if func_start is not None:
                for j in range(func_start + 1, total_lines):
                    if lines[j].strip() == "":
                        continue
                    if indentation(lines[j]) <= base_indent:
                        end = j - 1
                        break
                    end = j

                start = func_start
                confidence = 0.9

            # -------- Attempt 2: block-based (blank-line separated) --------
            if confidence < 0.9:
                s = idx
                e = idx

                while s > 0 and lines[s - 1].strip():
                    s -= 1
                while e < total_lines - 1 and lines[e + 1].strip():
                    e += 1

                if e - s <= MAX_FALLBACK_LINES:
                    start, end = s, e
                    confidence = 0.6

            # -------- Attempt 3: fixed fallback --------
            if confidence < 0.6:
                start = max(0, idx - 5)
                end = min(total_lines - 1, idx + 5)
                confidence = 0.4

            snippet = "\n".join(lines[start:end + 1])

            results.append({
                "file": str(path.relative_to(root)),
                "match_line": idx + 1,
                "context_start": start + 1,
                "context_end": end + 1,
                "confidence": round(confidence, 2),
                "snippet": snippet
            })

            hits += 1
            if hits >= MAX_HITS_PER_FILE:
                break

    return results



if __name__ == "__main__":
    mcp.run(port=8001)
