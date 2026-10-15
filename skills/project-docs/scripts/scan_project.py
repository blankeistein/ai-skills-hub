#!/usr/bin/env python3
"""Scan a software project and print a Markdown "fact sheet" for documentation.

Usage:
    python scan_project.py <project-root> [--depth 3] [--max-per-dir 25]

What it reports: detected stack, folder tree, language/file counts, manifest
scripts and dependencies, env var NAMES (from .env.example-style files only),
routes, Android components, Firebase usage, CI/Docker/deploy files, tests,
TODO/FIXME counts and existing docs.

Safety: it never reads real .env files, keystores or service-account JSON, and
it prints env var names only, never values.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

IGNORE_DIRS = {
    "node_modules", "vendor", ".git", ".idea", ".vscode", ".gradle", "build",
    "dist", "out", "target", "__pycache__", ".venv", "venv", "env", ".next",
    ".nuxt", ".cache", "coverage", ".dart_tool", "Pods", "storage", ".svn",
    ".DS_Store", "bower_components", ".turbo", ".parcel-cache",
}
KEEP_HIDDEN = {".github", ".gitlab", ".husky", ".circleci"}
SECRET_NAMES = {
    ".env", ".env.local", ".env.production", ".env.development", ".env.staging",
    "google-services.json", "serviceAccountKey.json", "keystore.properties",
    "local.properties", "id_rsa",
}
SECRET_SUFFIXES = (".jks", ".keystore", ".pem", ".p12", ".key")
ENV_EXAMPLE_RE = re.compile(r"^\.env(\.[\w-]+)?\.(example|sample|dist|template)$|^\.env\.example$")

LANG_EXT = {
    ".php": "PHP", ".js": "JavaScript", ".jsx": "JavaScript (JSX)",
    ".ts": "TypeScript", ".tsx": "TypeScript (TSX)", ".kt": "Kotlin",
    ".kts": "Kotlin script", ".java": "Java", ".py": "Python", ".go": "Go",
    ".rs": "Rust", ".dart": "Dart", ".swift": "Swift", ".rb": "Ruby",
    ".cs": "C#", ".vue": "Vue", ".svelte": "Svelte", ".html": "HTML",
    ".css": "CSS", ".scss": "SCSS", ".blade.php": "Blade", ".sql": "SQL",
    ".xml": "XML", ".sh": "Shell",
}
TEXT_READ_LIMIT = 400_000  # bytes per file
MAX_FILES = 40_000


def is_secret(path: Path) -> bool:
    return path.name in SECRET_NAMES or path.suffix.lower() in SECRET_SUFFIXES or (
        path.name.startswith(".env") and not ENV_EXAMPLE_RE.match(path.name)
    )


def safe_read(path: Path) -> str:
    if is_secret(path):
        return ""
    try:
        with open(path, "rb") as f:
            return f.read(TEXT_READ_LIMIT).decode("utf-8", errors="replace")
    except OSError:
        return ""


def collect_files(root: Path):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            d for d in dirnames
            if d not in IGNORE_DIRS and (not d.startswith(".") or d in KEEP_HIDDEN)
        )
        for fn in sorted(filenames):
            files.append(Path(dirpath) / fn)
            if len(files) >= MAX_FILES:
                return files, True
    return files, False


def rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def print_tree(root: Path, depth: int, max_per_dir: int):
    lines = [f"{root.name}/"]

    def rec(d: Path, prefix: str, level: int):
        try:
            entries = [
                e for e in sorted(d.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                if not (e.is_dir() and (e.name in IGNORE_DIRS or (e.name.startswith(".") and e.name not in KEEP_HIDDEN)))
                and not is_secret(e)
                and e.name != ".DS_Store"
            ]
        except OSError:
            return
        shown = entries[:max_per_dir]
        for i, e in enumerate(shown):
            last = i == len(shown) - 1 and len(entries) <= max_per_dir
            branch = "└── " if last else "├── "
            lines.append(f"{prefix}{branch}{e.name}{'/' if e.is_dir() else ''}")
            if e.is_dir() and level < depth:
                rec(e, prefix + ("    " if last else "│   "), level + 1)
        if len(entries) > max_per_dir:
            lines.append(f"{prefix}└── … {len(entries) - max_per_dir} more")

    rec(root, "", 1)
    return "\n".join(lines)


def load_json(path: Path):
    try:
        return json.loads(safe_read(path))
    except (json.JSONDecodeError, ValueError):
        return {}


def find(files, name):
    return [f for f in files if f.name == name]


def section(title):
    print(f"\n## {title}\n")


def detect_stack(root, files, names):
    stack = []
    for pj in find(files, "package.json"):
        data = load_json(pj)
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        where = rel(root, pj)
        tags = []
        for key, label in [
            ("react", "React"), ("next", "Next.js"), ("vite", "Vite"),
            ("typescript", "TypeScript"), ("vue", "Vue"), ("svelte", "Svelte"),
            ("express", "Express"), ("firebase", "Firebase JS SDK"),
            ("firebase-functions", "Firebase Cloud Functions"),
            ("tailwindcss", "Tailwind CSS"), ("react-router-dom", "React Router"),
            ("redux", "Redux"), ("@reduxjs/toolkit", "Redux Toolkit"),
            ("zustand", "Zustand"), ("@tanstack/react-query", "React Query"),
            ("prisma", "Prisma"), ("mongoose", "Mongoose"), ("sequelize", "Sequelize"),
            ("@google/generative-ai", "Gemini API"), ("@google/genai", "Gemini API"),
            ("pdfjs-dist", "pdf.js"), ("opencv.js", "OpenCV.js"),
        ]:
            if key in deps:
                tags.append(f"{label} {deps[key]}")
        stack.append(f"Node project `{where}`" + (": " + ", ".join(tags) if tags else ""))
    for cj in find(files, "composer.json"):
        data = load_json(cj)
        req = data.get("require", {})
        tags = []
        if "laravel/framework" in req:
            tags.append(f"Laravel {req['laravel/framework']}")
        if "php" in req:
            tags.append(f"PHP {req['php']}")
        for k in ("laravel/sanctum", "laravel/passport", "spatie/laravel-permission",
                  "livewire/livewire", "inertiajs/inertia-laravel", "laravel/breeze",
                  "laravel/fortify", "maatwebsite/excel", "barryvdh/laravel-dompdf",
                  "kreait/laravel-firebase", "midtrans/midtrans-php"):
            if k in req:
                tags.append(k)
        stack.append(f"PHP project `{rel(root, cj)}`" + (": " + ", ".join(tags) if tags else ""))
    gradles = [f for f in files if f.name in ("build.gradle", "build.gradle.kts")]
    if gradles or "AndroidManifest.xml" in names:
        stack.append("Android / Gradle project")
    for pat, label in [
        ("pubspec.yaml", "Flutter / Dart"), ("requirements.txt", "Python (requirements.txt)"),
        ("pyproject.toml", "Python (pyproject)"), ("go.mod", "Go module"),
        ("Cargo.toml", "Rust (Cargo)"), ("Gemfile", "Ruby"), ("pom.xml", "Java (Maven)"),
        ("Dockerfile", "Docker"), ("docker-compose.yml", "Docker Compose"),
        ("docker-compose.yaml", "Docker Compose"), ("firebase.json", "Firebase config"),
        ("artisan", "Laravel artisan present"), ("manage.py", "Django"),
    ]:
        if pat in names:
            stack.append(label)
    return list(dict.fromkeys(stack))


def report_node(root, files):
    for pj in find(files, "package.json"):
        data = load_json(pj)
        if not data:
            continue
        print(f"### `{rel(root, pj)}`\n")
        if data.get("name"):
            print(f"- name: `{data['name']}`  version: `{data.get('version', '?')}`")
        pm = "pnpm" if (pj.parent / "pnpm-lock.yaml").exists() else \
             "yarn" if (pj.parent / "yarn.lock").exists() else \
             "bun" if (pj.parent / "bun.lockb").exists() else \
             "npm" if (pj.parent / "package-lock.json").exists() else "unknown (no lockfile)"
        print(f"- package manager (from lockfile): {pm}")
        if data.get("engines"):
            print(f"- engines: {data['engines']}")
        if data.get("scripts"):
            print("- scripts:")
            for k, v in data["scripts"].items():
                print(f"  - `{k}`: `{v}`")
        deps = data.get("dependencies", {})
        if deps:
            print(f"- dependencies ({len(deps)}): " + ", ".join(f"`{k}`" for k in list(deps)[:40])
                  + (" …" if len(deps) > 40 else ""))
        dev = data.get("devDependencies", {})
        if dev:
            print(f"- devDependencies ({len(dev)}): " + ", ".join(f"`{k}`" for k in list(dev)[:25])
                  + (" …" if len(dev) > 25 else ""))
        print()


def report_php(root, files):
    for cj in find(files, "composer.json"):
        data = load_json(cj)
        if not data:
            continue
        print(f"### `{rel(root, cj)}`\n")
        req = data.get("require", {})
        print("- require: " + ", ".join(f"`{k}` {v}" for k, v in req.items()))
        if data.get("scripts"):
            print("- composer scripts: " + ", ".join(f"`{k}`" for k in data["scripts"]))
        print()
    route_files = [f for f in files if f.parent.name == "routes" and f.suffix == ".php"]
    for rf in route_files:
        text = safe_read(rf)
        hits = re.findall(r"^\s*(Route::[^\n;]+;?)", text, flags=re.M)
        print(f"### Routes in `{rel(root, rf)}` ({len(hits)} Route:: statements)\n")
        for h in hits[:60]:
            print(f"- `{h.strip()[:140]}`")
        if len(hits) > 60:
            print(f"- … {len(hits) - 60} more")
        print()
    for label, pattern in [
        ("Controllers", "Controllers"), ("Models", "Models"), ("Migrations", "migrations"),
        ("Jobs", "Jobs"), ("Middleware", "Middleware"), ("Policies", "Policies"),
        ("Console commands", "Commands"), ("Livewire components", "Livewire"),
    ]:
        items = [f for f in files if pattern in f.parts and f.suffix == ".php"]
        if items:
            names = ", ".join(f"`{f.stem}`" for f in items[:40])
            print(f"- **{label}** ({len(items)}): {names}" + (" …" if len(items) > 40 else ""))
    print()


def report_express(root, files):
    pat = re.compile(r"\b(app|router|api)\.(get|post|put|patch|delete)\(\s*['\"`]([^'\"`]+)")
    rows = []
    for f in files:
        if f.suffix in (".js", ".ts", ".mjs", ".cjs") and "node_modules" not in f.parts:
            text = safe_read(f)
            if "express" in text or "router" in text:
                for m in pat.finditer(text):
                    rows.append((m.group(2).upper(), m.group(3), rel(root, f)))
    if rows:
        print("### Express-style routes (heuristic)\n")
        for method, path, file in rows[:60]:
            print(f"- `{method} {path}` — `{file}`")
        if len(rows) > 60:
            print(f"- … {len(rows) - 60} more")
        print()


def report_react(root, files):
    entry = [f for f in files if f.name in (
        "main.tsx", "main.jsx", "index.tsx", "index.jsx", "App.tsx", "App.jsx", "vite.config.ts", "vite.config.js",
        "next.config.js", "next.config.mjs", "tailwind.config.js", "tailwind.config.ts", "tsconfig.json")]
    if entry:
        print("### Frontend entry/config files\n")
        for f in entry[:20]:
            print(f"- `{rel(root, f)}`")
        print()
    route_pat = re.compile(r"<Route[^>]*\bpath=['\"{]+([^'\"}>]+)")
    rows = []
    for f in files:
        if f.suffix in (".tsx", ".jsx"):
            for m in route_pat.finditer(safe_read(f)):
                rows.append((m.group(1), rel(root, f)))
    if rows:
        print("### React Router paths (heuristic)\n")
        for p, f in rows[:50]:
            print(f"- `{p}` — `{f}`")
        print()
    nextpages = [f for f in files if "app" in f.parts and f.name in ("page.tsx", "page.jsx", "page.js")]
    if nextpages:
        print("### Next.js app-router pages\n")
        for f in nextpages[:50]:
            print(f"- `{rel(root, f)}`")
        print()


def report_android(root, files):
    gradles = [f for f in files if f.name in ("build.gradle", "build.gradle.kts")]
    for g in gradles:
        text = safe_read(g)
        info = {}
        for key, pat in [
            ("applicationId/namespace", r"(?:applicationId|namespace)\s*=?\s*[\"']([^\"']+)"),
            ("compileSdk", r"compileSdk\s*=?\s*(\d+)"),
            ("minSdk", r"minSdk\s*=?\s*(\d+)"),
            ("targetSdk", r"targetSdk\s*=?\s*(\d+)"),
            ("versionName", r"versionName\s*=?\s*[\"']([^\"']+)"),
            ("versionCode", r"versionCode\s*=?\s*(\d+)"),
        ]:
            m = re.search(pat, text)
            if m:
                info[key] = m.group(1)
        libs = [k for k in ("compose", "hilt", "dagger", "koin", "room", "retrofit", "okhttp", "coil",
                            "firebase", "workmanager", "datastore", "navigation", "paging", "coroutines",
                            "lifecycle", "camerax", "mlkit", "ksp", "kapt", "sqlcipher", "security-crypto")
                if re.search(k, text, re.I)]
        if info or libs:
            print(f"### `{rel(root, g)}`\n")
            if info:
                print("- " + ", ".join(f"{k}: `{v}`" for k, v in info.items()))
            if libs:
                print("- notable libraries/plugins mentioned: " + ", ".join(f"`{l}`" for l in libs))
            print()
    for mf in find(files, "AndroidManifest.xml"):
        text = safe_read(mf)
        acts = re.findall(r"<activity[^>]*android:name=\"([^\"]+)\"", text)
        svcs = re.findall(r"<service[^>]*android:name=\"([^\"]+)\"", text)
        recv = re.findall(r"<receiver[^>]*android:name=\"([^\"]+)\"", text)
        perms = re.findall(r"<uses-permission[^>]*android:name=\"([^\"]+)\"", text)
        print(f"### `{rel(root, mf)}`\n")
        if acts: print("- activities: " + ", ".join(f"`{a}`" for a in acts))
        if svcs: print("- services: " + ", ".join(f"`{a}`" for a in svcs))
        if recv: print("- receivers: " + ", ".join(f"`{a}`" for a in recv))
        if perms: print("- permissions: " + ", ".join(f"`{p.split('.')[-1]}`" for p in perms))
        print()
    kt = [f for f in files if f.suffix == ".kt"]
    for label, pat in [("ViewModels", r"class\s+(\w+ViewModel)"), ("Room entities", r"@Entity[^\n]*\n(?:[^\n]*\n){0,3}?\s*data class\s+(\w+)"),
                       ("DAOs", r"@Dao[^\n]*\n\s*interface\s+(\w+)"),
                       ("Composable screens", r"@Composable\s*\n\s*fun\s+(\w+Screen)\b"),
                       ("Workers", r"class\s+(\w+Worker)\b")]:
        found = []
        for f in kt:
            found += re.findall(pat, safe_read(f))
        found = list(dict.fromkeys(found))
        if found:
            print(f"- **{label}** ({len(found)}): " + ", ".join(f"`{x}`" for x in found[:40]) + (" …" if len(found) > 40 else ""))
    print()


def report_firebase(root, files):
    cfg = [f for f in files if f.name in (
        "firebase.json", ".firebaserc", "firestore.rules", "firestore.indexes.json",
        "database.rules.json", "storage.rules")]
    if cfg:
        print("### Firebase config files\n")
        for f in cfg:
            print(f"- `{rel(root, f)}`")
        print()
    for f in cfg:
        if f.name == ".firebaserc":
            data = load_json(f)
            projects = data.get("projects", {})
            if projects:
                print("- project aliases: " + ", ".join(f"`{k}` → `{v}`" for k, v in projects.items()))
        if f.name in ("firestore.rules", "database.rules.json", "storage.rules"):
            text = safe_read(f)
            open_rule = bool(re.search(r"allow\s+[^:]*:\s*if\s+true", text)) or '".read": true' in text.replace(" ", "")
            if open_rule:
                print(f"- ⚠ `{rel(root, f)}` appears to contain an open rule (`if true` / `.read: true`) — verify.")
    # collections
    coll = Counter()
    pat = re.compile(r"\.(?:collection|collectionGroup)\(\s*[\"']([\w\-./{}$]+)[\"']|getReference\(\s*[\"']([\w\-./{}$]+)[\"']|\.ref\(\s*[\"']([\w\-./{}$]+)[\"']")
    for f in files:
        if f.suffix in (".ts", ".tsx", ".js", ".jsx", ".kt", ".java", ".dart"):
            for m in pat.finditer(safe_read(f)):
                coll[next(g for g in m.groups() if g)] += 1
    if coll:
        print("\n### Firestore/RTDB paths referenced in code (heuristic)\n")
        for name, n in coll.most_common(40):
            print(f"- `{name}` ({n}×)")
    fx = [f for f in files if "functions" in f.parts and f.suffix in (".ts", ".js") and "node_modules" not in f.parts]
    exports = []
    pat2 = re.compile(r"exports\.(\w+)\s*=|export\s+const\s+(\w+)\s*=\s*(?:functions\.|on\w+|https\.|onCall|onRequest|onSchedule|onDocument)")
    for f in fx:
        for m in pat2.finditer(safe_read(f)):
            exports.append((next(g for g in m.groups() if g), rel(root, f)))
    if exports:
        print("\n### Cloud Functions exports (heuristic)\n")
        for n, f in exports[:40]:
            print(f"- `{n}` — `{f}`")
    print()


def report_python(root, files):
    for f in files:
        if f.name in ("requirements.txt",):
            lines = [l.strip() for l in safe_read(f).splitlines() if l.strip() and not l.startswith("#")]
            print(f"### `{rel(root, f)}` ({len(lines)} entries)\n")
            print(", ".join(f"`{l}`" for l in lines[:40]) + (" …" if len(lines) > 40 else "") + "\n")
        if f.name in ("pyproject.toml",):
            print(f"### `{rel(root, f)}` present — read it for dependencies and scripts.\n")


def report_env(root, files):
    ex = [f for f in files if ENV_EXAMPLE_RE.match(f.name)]
    real = [f for f in files if f.name.startswith(".env") and not ENV_EXAMPLE_RE.match(f.name)]
    if ex:
        for f in ex:
            keys = re.findall(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=", safe_read(f), flags=re.M)
            print(f"### `{rel(root, f)}` — {len(keys)} variables (names only)\n")
            print(", ".join(f"`{k}`" for k in keys) + "\n")
    else:
        print("_No `.env.example`-style file found._ Env vars must be discovered from code (`env(`, `process.env.`, `import.meta.env.`, `BuildConfig`).\n")
    if real:
        print("Real env files exist (" + ", ".join(f"`{rel(root, f)}`" for f in real) +
              ") — **not read** by this scanner. Make sure they are git-ignored.\n")
    # env usage in code
    used = Counter()
    pats = [r"process\.env\.([A-Z0-9_]+)", r"import\.meta\.env\.([A-Z0-9_]+)",
            r"\benv\(\s*['\"]([A-Z0-9_]+)['\"]", r"getenv\(\s*['\"]([A-Z0-9_]+)['\"]",
            r"os\.environ(?:\.get)?\(?\[?\s*['\"]([A-Z0-9_]+)['\"]"]
    for f in files:
        if f.suffix in (".js", ".jsx", ".ts", ".tsx", ".php", ".py", ".mjs"):
            text = safe_read(f)
            for p in pats:
                for m in re.finditer(p, text):
                    used[m.group(1)] += 1
    if used:
        print("### Env vars referenced in code\n")
        print(", ".join(f"`{k}`" for k, _ in used.most_common(60)) + "\n")


def report_infra(root, files):
    patterns = [
        ("Docker", lambda f: f.name.startswith("Dockerfile") or f.name.startswith("docker-compose")),
        ("CI workflows", lambda f: ".github" in f.parts and "workflows" in f.parts
         or f.name in (".gitlab-ci.yml", "Jenkinsfile", "cloudbuild.yaml", "cloudbuild.yml", "bitbucket-pipelines.yml")),
        ("Web server / hosting config", lambda f: f.name in (".htaccess", "nginx.conf", "vercel.json", "netlify.toml",
                                                         "app.yaml", "Procfile", "ecosystem.config.js", "supervisord.conf")),
        ("Build / release config", lambda f: f.name in ("proguard-rules.pro", "gradle.properties", "capacitor.config.ts",
                                                       "eas.json", "fastlane", "Fastfile")),
    ]
    for label, test in patterns:
        hits = [f for f in files if test(f)]
        if hits:
            print(f"- **{label}:** " + ", ".join(f"`{rel(root, f)}`" for f in hits[:15]))
    if not any(test(f) for _, test in patterns for f in files):
        print("- none found (deployment is probably manual; ask the author how it is shipped)")
    wf = [f for f in files if ".github" in f.parts and "workflows" in f.parts]
    for f in wf[:5]:
        text = safe_read(f)
        name = re.search(r"^name:\s*(.+)$", text, flags=re.M)
        on = re.search(r"^on:\s*(.*)$", text, flags=re.M)
        print(f"  - `{rel(root, f)}`: name={name.group(1).strip() if name else '?'}; triggers={on.group(1).strip() if on and on.group(1).strip() else '(see file)'}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="project root directory")
    ap.add_argument("--depth", type=int, default=3, help="tree depth (default 3)")
    ap.add_argument("--max-per-dir", type=int, default=25, help="max entries shown per directory (default 25)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")

    # If a zip was extracted into a single wrapper folder, descend into it.
    entries = [e for e in root.iterdir() if not e.name.startswith(".")]
    if len(entries) == 1 and entries[0].is_dir() and entries[0].name not in IGNORE_DIRS:
        root = entries[0]

    files, truncated = collect_files(root)
    names = {f.name for f in files}

    print(f"# Project scan: {root.name}\n")
    print(f"- root: `{root}`")
    print(f"- files scanned: {len(files)}" + (" (truncated)" if truncated else ""))
    print(f"- git repository: {'yes' if (root / '.git').exists() else 'no'}")

    section("Detected stack")
    stack = detect_stack(root, files, names)
    print("\n".join(f"- {s}" for s in stack) if stack else "- nothing detected; inspect manually")

    section("Folder tree")
    print("```")
    print(print_tree(root, args.depth, args.max_per_dir))
    print("```")

    section("Language / file breakdown")
    counts, lines = Counter(), Counter()
    for f in files:
        name = f.name.lower()
        ext = ".blade.php" if name.endswith(".blade.php") else f.suffix.lower()
        lang = LANG_EXT.get(ext)
        if lang:
            counts[lang] += 1
            if f.stat().st_size < 1_000_000:
                lines[lang] += safe_read(f).count("\n")
    if counts:
        print("| Language | Files | Approx. lines |\n|---|---|---|")
        for lang, n in counts.most_common(12):
            print(f"| {lang} | {n} | {lines[lang]} |")

    section("Manifests, scripts and dependencies")
    report_node(root, files)
    report_php(root, files)
    report_python(root, files)

    if "AndroidManifest.xml" in names or any(f.name in ("build.gradle", "build.gradle.kts") for f in files):
        section("Android")
        report_android(root, files)

    section("Web routes and frontend")
    report_express(root, files)
    report_react(root, files)

    section("Firebase")
    report_firebase(root, files)

    section("Configuration (env var names only)")
    report_env(root, files)

    section("Infrastructure, CI and deployment files")
    report_infra(root, files)

    section("Tests")
    test_files = [f for f in files if re.search(r"(^|[._-])(test|spec)s?([._-]|$)|Test\.(kt|java|php)$", f.name, re.I)
                  or any(p in ("tests", "test", "__tests__", "androidTest") for p in f.parts)]
    print(f"- test files found: {len(test_files)}")
    for f in test_files[:10]:
        print(f"  - `{rel(root, f)}`")

    section("Code health signals")
    marks = Counter()
    by_file = defaultdict(int)
    for f in files:
        if f.suffix.lower() in LANG_EXT:
            t = safe_read(f)
            for m in re.findall(r"\b(TODO|FIXME|HACK|XXX)\b", t):
                marks[m] += 1
                by_file[rel(root, f)] += 1
    print("- markers: " + (", ".join(f"{k}={v}" for k, v in marks.items()) or "none"))
    for fn, n in sorted(by_file.items(), key=lambda x: -x[1])[:5]:
        print(f"  - `{fn}`: {n}")
    big = sorted(((f.stat().st_size, f) for f in files if f.suffix.lower() in LANG_EXT), reverse=True)[:5]
    if big:
        print("- largest source files: " + ", ".join(f"`{rel(root, f)}` ({s // 1024} KB)" for s, f in big))

    section("Existing documentation")
    docs = [f for f in files if f.suffix.lower() in (".md", ".mdx", ".rst", ".txt")
            and (f.parent == root or "docs" in f.parts or "doc" in f.parts or f.name.upper().startswith(("README", "CHANGELOG", "CONTRIBUTING", "LICENSE")))]
    print("\n".join(f"- `{rel(root, f)}` ({f.stat().st_size // 1024 or 1} KB)" for f in docs[:25]) or "- none found")

    print("\n---\nHeuristic scan. Verify against the code before documenting; secrets were intentionally not read.")


if __name__ == "__main__":
    main()
