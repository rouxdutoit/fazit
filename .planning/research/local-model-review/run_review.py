"""Send Fazit's source to a local llama.cpp server, one file or file part per request.

Standard library only. Usage, from the repository root, with llama-server running on 127.0.0.1:8080:

    python .planning/research/local-model-review/run_review.py

Answers go to .planning/research/local-model-review/raw/. A unit whose answer file
already exists is skipped, so an interrupted run can be restarted.
"""

import json
import pathlib
import sys
import time
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src" / "fazit"
RAW = HERE / "raw"
SERVER = "http://127.0.0.1:8080"
MAX_CHARS = 12_000  # one request's code stays well inside the 32k-token context
SAMPLING = {"temperature": 0.6, "top_p": 0.95, "top_k": 20, "min_p": 0.0, "seed": 42}
MAX_TOKENS = 16_000
GROUPED = ["__init__.py", "__main__.py", "errors.py"]


def principles() -> str:
    text = (REPO / "DECISIONS.md").read_text(encoding="utf-8")
    start = text.index("## Principles")
    end = text.index("\n## ", start + 5)
    return text[start:end].split("\n", 1)[1].strip()


def numbered(lines: list[str], first: int) -> str:
    return "\n".join(f"{first + i:4d}  {line}" for i, line in enumerate(lines))


def is_boundary(line: str) -> bool:
    stripped = line.lstrip()
    return not stripped or len(line) - len(stripped) <= 2


def split(lines: list[str]) -> list[tuple[int, int]]:
    """Cut at an entry boundary once a part reaches MAX_CHARS; hard cut at 1.4 times that."""
    parts, start, size = [], 0, 0
    for i, line in enumerate(lines):
        size += len(line) + 1
        if (size >= MAX_CHARS and is_boundary(line)) or size >= MAX_CHARS * 1.4:
            parts.append((start, i))
            start, size = i, 0
    if parts and size < MAX_CHARS // 6:
        start = parts.pop()[0]  # a short tail joins the part before it
    parts.append((start, len(lines)))
    return [(a, b) for a, b in parts if b > a]


def units() -> list[tuple[str, str, str]]:
    """(name, path label, numbered code) for every request, in a fixed order."""
    result = []
    group = []
    for name in GROUPED:
        lines = (SRC / name).read_text(encoding="utf-8").splitlines()
        group.append(f"=== src/fazit/{name}\n{numbered(lines, 1)}")
    result.append(("src__fazit__package", " (three small files)", "\n\n".join(group)))
    files = sorted(p for p in SRC.glob("*.py") if p.name not in GROUPED)
    files += sorted((SRC / "rules").rglob("*.yaml"))
    files += [SRC / "templates" / "report.html.j2"]
    for path in files:
        rel = path.relative_to(REPO).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        pieces = split(lines)
        for n, (a, b) in enumerate(pieces, 1):
            name = rel.replace("/", "__")
            part = ""
            if len(pieces) > 1:
                name += f".part{n}"
                part = f" (part {n} of {len(pieces)}, lines {a + 1} to {b} of {len(lines)})"
            result.append((name, rel + part, numbered(lines[a:b], a + 1)))
    return result


def ask(prompt: str) -> dict:
    body = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        **SAMPLING,
    }
    req = urllib.request.Request(
        f"{SERVER}/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=3600) as resp:
        return json.load(resp)


def main() -> None:
    RAW.mkdir(exist_ok=True)
    (RAW / "reasoning").mkdir(exist_ok=True)
    template = (HERE / "prompt.txt").read_text(encoding="utf-8")
    fixed = template.replace("{principles}", principles())
    todo = units()
    log = []
    for i, (name, label, code) in enumerate(todo, 1):
        out = RAW / f"{name}.txt"
        if out.exists():
            continue
        path, _, part = label.partition(" (")
        prompt = fixed.replace("{path}", path).replace("{part}", f" ({part}" if part else "")
        prompt = prompt.replace("{code}", code)
        began = time.time()
        reply = ask(prompt)
        seconds = round(time.time() - began, 1)
        message = reply["choices"][0]["message"]
        out.write_text(message.get("content") or "", encoding="utf-8")
        reasoning = message.get("reasoning_content") or ""
        (RAW / "reasoning" / f"{name}.txt").write_text(reasoning, encoding="utf-8")
        entry = {
            "unit": name,
            "label": label,
            "seconds": seconds,
            "finish_reason": reply["choices"][0].get("finish_reason"),
            "usage": reply.get("usage"),
        }
        log.append(entry)
        with (RAW / "run-log.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[{i}/{len(todo)}] {name}: {seconds}s {entry['finish_reason']}", flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    if "--list" in sys.argv:
        for name, label, code in units():
            print(f"{len(code):7d}  {name}  {label}")
    else:
        main()
