#!/usr/bin/env python3
"""Lint AGENTS.md / CLAUDE.md / DESIGN.md style guides against their repo.

Checks (heuristic, fast, no network):
  - length (too long -> consumes agent context)
  - package.json scripts / composer scripts / make targets referenced in
    commands actually exist
  - backticked relative paths exist in the repo
  - leftover TODO / <placeholder> markers
  - vague filler phrases that add no information
  - likely secrets (API keys, tokens, private keys)
  - duplicated lines (copy/paste between guides)
  - @import targets in CLAUDE.md exist
  - presence of recommended sections (AGENTS.md only)

Exit code 1 if any ERROR is found; warnings do not fail.

Usage:
    python lint_guides.py <file-or-dir> [--root <repo-root>] [--json]
If given a directory, lints every known guide file found directly in it.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

GUIDE_NAMES = {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "DESIGN.md", "ARCHITECTURE.md",
               "TESTING.md", "SECURITY.md", "DATABASE.md", "API.md", "DEPLOYMENT.md",
               "CONTRIBUTING.md", "copilot-instructions.md"}

VAGUE = [
    r"\bbest practices?\b", r"\bclean code\b", r"\bwrite (?:clean|good|high[- ]quality) code\b",
    r"\bfollow (?:solid|dry|kiss)\b", r"\bmodern (?:and )?(?:clean|sleek)\b",
    r"\bmake sure (?:the )?code is (?:clean|good)\b", r"\bpraktik terbaik\b",
    r"\bkode (?:yang )?(?:bersih|rapi)\b", r"\bsenior (?:software )?engineer\b",
    r"\byou are an? (?:expert|senior|world[- ]class)\b", r"\bkamu adalah (?:seorang )?(?:ahli|senior)\b",
]
SECRET_PATTERNS = [
    (r"AIza[0-9A-Za-z_\-]{35}", "Google API key"),
    (r"sk-[A-Za-z0-9]{20,}", "secret key (sk-...)"),
    (r"ghp_[A-Za-z0-9]{30,}", "GitHub token"),
    (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
    (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "private key"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"(?i)(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9/+_\-]{12,}['\"]?", "possible hardcoded credential"),
]
AGENTS_SECTIONS = {
    "commands": r"(?im)^#{1,3}\s*(commands?|perintah|scripts?|setup|getting started)\b",
    "boundaries": r"(?im)^#{1,3}\s*(boundaries|batasan|rules|aturan|do(?:'|n't| not)|never|jangan)\b",
    "structure": r"(?im)^#{1,3}\s*(project structure|struktur|structure|layout|folder)\b",
    "testing": r"(?im)^#{1,3}\s*(testing|tests?|pengujian)\b",
}
CMD_PREFIXES = ("npm run ", "pnpm ", "yarn ", "bun run ", "composer ", "make ")


def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def known_scripts(root: Path):
    s = {"npm": set(), "composer": set(), "make": set()}
    pkg = load_json(root / "package.json")
    if pkg:
        s["npm"] = set((pkg.get("scripts") or {}).keys())
    comp = load_json(root / "composer.json")
    if comp:
        s["composer"] = set((comp.get("scripts") or {}).keys())
    mk = root / "Makefile"
    if mk.exists():
        s["make"] = set(re.findall(r"^([A-Za-z0-9_.-]+):(?!=)", mk.read_text(errors="replace"), re.M))
    return s


BUILTIN_NPM = {"install", "i", "ci", "test", "start", "init", "audit", "update", "outdated", "publish",
               "exec", "x", "add", "remove", "dlx", "create", "link", "pack", "version", "help", "run", "dev"}
BUILTIN_COMPOSER = {"install", "update", "require", "remove", "dump-autoload", "dumpautoload", "audit",
                    "validate", "outdated", "show", "init", "create-project", "run-script", "test"}


def code_spans_and_blocks(text: str):
    """Yield (lineno, command_string) for fenced-block lines and inline code."""
    in_block = False
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_block = not in_block
            continue
        if in_block:
            cmd = line.split("#")[0].strip()
            if cmd:
                yield i, cmd
        else:
            for m in re.finditer(r"`([^`\n]+)`", line):
                yield i, m.group(1).strip()


def check_file(path: Path, root: Path):
    issues = []  # (level, line, message)
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    name = path.name

    def add(level, line, msg):
        issues.append({"level": level, "line": line, "message": msg})

    # length
    limits = {"AGENTS.md": (250, 400), "CLAUDE.md": (150, 300), "GEMINI.md": (60, 150),
              "copilot-instructions.md": (150, 300)}
    warn, err = limits.get(name, (500, 900))
    if len(lines) > err:
        add("ERROR", None, f"{len(lines)} lines - far too long for always-loaded context (target <= {warn}); move detail to docs/ and link it")
    elif len(lines) > warn:
        add("WARN", None, f"{len(lines)} lines - consider trimming or splitting (target <= {warn})")

    # placeholders
    for i, line in enumerate(lines, 1):
        if re.search(r"\bTODO\b", line):
            add("WARN", i, "TODO remaining - confirm with the user before delivering")
        if re.search(r"<[A-Za-z][^<>\n]{1,40}>", line) and "```" not in line and not line.strip().startswith(("<!--", "<img", "<a ", "<br")):
            # template-like placeholder e.g. <Nama Projek>
            m = re.search(r"<([A-Za-z][^<>\n]{1,40})>", line)
            if m and " " in m.group(1) or (m and m.group(1)[0].isupper()):
                add("WARN", i, f"unfilled placeholder {m.group(0)!r}")

    # vague
    for i, line in enumerate(lines, 1):
        for pat in VAGUE:
            if re.search(pat, line, re.I):
                add("WARN", i, "vague/filler guidance - replace with a concrete, checkable rule or delete")
                break

    # secrets
    for i, line in enumerate(lines, 1):
        for pat, label in SECRET_PATTERNS:
            if re.search(pat, line):
                add("ERROR", i, f"looks like a secret: {label} - remove and reference an env var name instead")
                break

    # paths
    seen_paths = set()
    for i, line in enumerate(lines, 1):
        for m in re.finditer(r"`([A-Za-z0-9_.@\-/{}\[\]*]+(?:/[A-Za-z0-9_.@\-/{}\[\]*]+)+/?|[A-Za-z0-9_\-]+\.[A-Za-z0-9]{1,5})`", line):
            p = m.group(1)
            if p in seen_paths or any(c in p for c in "*{}[]") or p.startswith(("http", "/", "@", "~")):
                continue
            if re.match(r"^[0-9.]+$", p) or p.startswith(("e.g", "i.e")):
                continue
            # skip things that look like commands/domains/versions
            if re.match(r"^[a-z0-9\-]+\.(com|org|io|dev|id|net|app|ai)$", p):
                continue
            seen_paths.add(p)
            cand = [root / p, path.parent / p]
            if not any(c.exists() for c in cand):
                # tolerate extensions-only mentions like `.env` or `Foo.kt` without folder
                if "/" in p:
                    add("WARN", i, f"path not found in repo: {p}")

    # commands vs scripts
    sc = known_scripts(root)
    for i, cmd in code_spans_and_blocks(text):
        for chain in re.split(r"\s*(?:&&|;|\|\|)\s*", cmd):
            chain = chain.strip().lstrip("$ ").strip()
            if chain.startswith("npm run ") or chain.startswith("bun run "):
                s = chain.split()[2] if len(chain.split()) > 2 else ""
                if s and sc["npm"] and s not in sc["npm"]:
                    add("ERROR", i, f"script '{s}' not found in package.json scripts")
            elif chain.startswith(("pnpm ", "yarn ")):
                parts = chain.split()
                s = parts[1] if len(parts) > 1 else ""
                if s == "run" and len(parts) > 2:
                    s = parts[2]
                if s and sc["npm"] and s not in sc["npm"] and s not in BUILTIN_NPM and not s.startswith("-") and s not in {"dlx", "exec", "workspace", "workspaces", "filter"}:
                    add("WARN", i, f"'{chain.split()[0]} {s}': not in package.json scripts (verify)")
            elif chain.startswith("composer "):
                parts = chain.split()
                s = parts[1] if len(parts) > 1 else ""
                if s == "run-script" and len(parts) > 2:
                    s = parts[2]
                if s and sc["composer"] is not None and (root / "composer.json").exists() \
                        and s not in sc["composer"] and s not in BUILTIN_COMPOSER and not s.startswith("-"):
                    add("ERROR", i, f"composer script '{s}' not found in composer.json")
            elif chain.startswith("make "):
                parts = chain.split()
                s = parts[1] if len(parts) > 1 else ""
                if s and (root / "Makefile").exists() and s not in sc["make"]:
                    add("ERROR", i, f"make target '{s}' not found in Makefile")
            elif chain.startswith("php artisan ") and not (root / "artisan").exists():
                add("ERROR", i, "php artisan used but no 'artisan' file in repo root")
            elif chain.startswith("./gradlew") and not (root / "gradlew").exists():
                add("ERROR", i, "./gradlew used but no gradlew in repo root")

    # CLAUDE.md imports
    if name == "CLAUDE.md":
        for i, line in enumerate(lines, 1):
            m = re.match(r"^\s*@([^\s]+)\s*$", line)
            if m and not (path.parent / m.group(1)).exists() and not (root / m.group(1)).exists():
                add("ERROR", i, f"import target not found: @{m.group(1)}")

    # sections for AGENTS.md
    if name == "AGENTS.md":
        for key, pat in AGENTS_SECTIONS.items():
            if not re.search(pat, text):
                add("INFO", None, f"no '{key}' section detected (add one unless intentionally omitted)")
        if len(re.findall(r"```", text)) < 2:
            add("WARN", None, "no fenced command block - agents need exact runnable commands near the top")
        first_code = text.find("```")
        if first_code > 3500:
            add("WARN", None, "first command block appears late; put Commands near the top")

    # shouting
    caps = [i for i, l in enumerate(lines, 1) if re.search(r"\b(?:NEVER|ALWAYS|JANGAN|SELALU|MUST|WAJIB)\b.*!{2,}", l)]
    if caps:
        add("WARN", caps[0], "heavy emphasis (e.g. '!!!') - prefer a calm rule plus the reason")

    # duplicates within file
    norm = [re.sub(r"\s+", " ", l.strip().lower()) for l in lines if len(l.strip()) > 40 and not l.strip().startswith(("|", "```", "#"))]
    dup = [l for l, c in Counter(norm).items() if c > 1]
    for d in dup[:5]:
        add("WARN", None, f"duplicated line: {d[:70]}...")

    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target")
    ap.add_argument("--root", help="repo root (default: directory of target, or target itself)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    t = Path(args.target).resolve()
    if t.is_dir():
        root = Path(args.root).resolve() if args.root else t
        files = [p for p in sorted(t.iterdir()) if p.name in GUIDE_NAMES]
        gh = t / ".github" / "copilot-instructions.md"
        if gh.exists():
            files.append(gh)
        docs = t / "docs"
        if docs.is_dir():
            files += [p for p in sorted(docs.glob("*.md")) if p.name in GUIDE_NAMES]
    elif t.is_file():
        root = Path(args.root).resolve() if args.root else t.parent
        files = [t]
    else:
        print(f"error: {t} not found", file=sys.stderr)
        sys.exit(2)

    if not files:
        print("No guide files found.")
        return

    all_issues = {}
    for f in files:
        all_issues[str(f.relative_to(root)) if root in f.parents or f.parent == root else str(f)] = check_file(f, root)

    # cross-file duplicate detection
    bodies = {}
    for f in files:
        for l in f.read_text(errors="replace").splitlines():
            n = re.sub(r"\s+", " ", l.strip().lower())
            if len(n) > 60 and not n.startswith(("|", "```", "#", "-->")):
                bodies.setdefault(n, set()).add(f.name)
    cross = [(l, fs) for l, fs in bodies.items() if len(fs) > 1]
    if cross:
        first = next(iter(all_issues))
        for l, fs in cross[:5]:
            all_issues[first].append({"level": "WARN", "line": None,
                                      "message": f"same line appears in {sorted(fs)}: '{l[:60]}...' (keep one source of truth)"})

    if args.json:
        print(json.dumps(all_issues, indent=2, ensure_ascii=False))
    else:
        for fn, issues in all_issues.items():
            print(f"\n== {fn} ==")
            if not issues:
                print("  OK - no issues found")
            for it in issues:
                loc = f"L{it['line']}" if it["line"] else "   "
                print(f"  [{it['level']:<5}] {loc:<5} {it['message']}")
        n_err = sum(1 for v in all_issues.values() for i in v if i["level"] == "ERROR")
        n_warn = sum(1 for v in all_issues.values() for i in v if i["level"] == "WARN")
        print(f"\nSummary: {n_err} error(s), {n_warn} warning(s)")
    sys.exit(1 if any(i["level"] == "ERROR" for v in all_issues.values() for i in v) else 0)


if __name__ == "__main__":
    main()
