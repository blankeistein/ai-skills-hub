#!/usr/bin/env python3
"""Scan a repository and print a JSON summary useful for writing AGENTS.md.

Detects: stack/framework hints, runnable commands (package.json scripts,
composer scripts, Makefile targets, Gradle tasks hints, CI commands),
runtime versions, top-level structure, generated folders, env files,
and existing AI-guidance files.

This is a *detector*, not an interpreter. Treat output as raw material and
verify by reading the real files before writing anything into a guide.

Usage:
    python scan_project.py <repo-path> [--depth 2] [--text]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", ".next", ".nuxt",
    ".gradle", ".idea", ".vscode", "__pycache__", ".venv", "venv", "target",
    ".dart_tool", "Pods", ".cache", "coverage", ".turbo", ".svelte-kit",
    "storage", ".firebase",
}

GUIDE_FILES = [
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", "DESIGN.md", "ARCHITECTURE.md",
    "CONTRIBUTING.md", "TESTING.md", "SECURITY.md", "DATABASE.md", "API.md",
    "DEPLOYMENT.md", "README.md", ".cursorrules", ".clinerules",
    ".github/copilot-instructions.md", ".windsurfrules",
]
GUIDE_DIRS = [".cursor/rules", ".github/instructions", ".claude", ".windsurf/rules", "docs"]

GENERATED_HINTS = {
    "dist", "build", "generated", "gen", "__generated__", ".next", "out",
    "migrations", "vendor", "node_modules", "bootstrap/cache", "public/build",
}


def read_text(p: Path, limit: int = 400_000) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def load_json(p: Path):
    try:
        return json.loads(read_text(p))
    except Exception:
        return None


def walk(root: Path, max_depth: int):
    """Yield (relative_path, is_dir) up to max_depth, skipping ignored dirs."""
    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        depth = 0 if str(rel) == "." else len(rel.parts)
        dirnames[:] = sorted(d for d in dirnames if d not in IGNORE_DIRS)
        if depth >= max_depth:
            dirnames[:] = []
        for d in dirnames:
            yield (rel / d), True
        for f in sorted(filenames):
            yield (rel / f), False


def detect_js(root: Path, out: dict):
    pkg_path = root / "package.json"
    pkg = load_json(pkg_path)
    if not pkg:
        return
    deps = {}
    for k in ("dependencies", "devDependencies", "peerDependencies"):
        deps.update(pkg.get(k) or {})
    names = set(deps)

    def has(*n):
        return any(x in names for x in n)

    stack = []
    for label, keys in [
        ("React", ("react",)), ("Next.js", ("next",)), ("Vue", ("vue",)),
        ("Nuxt", ("nuxt",)), ("Svelte", ("svelte",)), ("Angular", ("@angular/core",)),
        ("Vite", ("vite",)), ("TypeScript", ("typescript",)), ("Tailwind CSS", ("tailwindcss",)),
        ("Express", ("express",)), ("Fastify", ("fastify",)), ("NestJS", ("@nestjs/core",)),
        ("Firebase JS SDK", ("firebase",)), ("Firebase Admin", ("firebase-admin",)),
        ("Firebase Functions", ("firebase-functions",)), ("Prisma", ("prisma", "@prisma/client")),
        ("Drizzle", ("drizzle-orm",)), ("TanStack Query", ("@tanstack/react-query",)),
        ("Redux", ("redux", "@reduxjs/toolkit")), ("Zustand", ("zustand",)),
        ("React Router", ("react-router", "react-router-dom")), ("Zod", ("zod",)),
        ("Vitest", ("vitest",)), ("Jest", ("jest",)), ("Playwright", ("@playwright/test",)),
        ("Cypress", ("cypress",)), ("ESLint", ("eslint",)), ("Prettier", ("prettier",)),
        ("Biome", ("@biomejs/biome",)), ("shadcn/ui (radix)", ("@radix-ui/react-slot",)),
        ("MUI", ("@mui/material",)), ("Inertia", ("@inertiajs/react", "@inertiajs/vue3")),
        ("Storybook", ("storybook", "@storybook/react")),
        ("Google Gemini SDK", ("@google/generative-ai", "@google/genai")),
    ]:
        if has(*keys):
            v = next((deps[k] for k in keys if k in deps), "")
            stack.append(f"{label} {v}".strip())
    out["stack"].extend(stack)

    pm = "npm"
    for lock, name in [("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"),
                       ("bun.lockb", "bun"), ("bun.lock", "bun"), ("package-lock.json", "npm")]:
        if (root / lock).exists():
            pm = name
            break
    out["package_manager"] = pm
    scripts = pkg.get("scripts") or {}
    run = {"npm": "npm run", "pnpm": "pnpm", "yarn": "yarn", "bun": "bun run"}[pm]
    out["commands"]["package.json scripts"] = {k: f"{run} {k}  ->  {v}" for k, v in scripts.items()}
    if pkg.get("workspaces"):
        out["monorepo"].append(f"package.json workspaces: {pkg['workspaces']}")
    if pkg.get("engines"):
        out["runtime_versions"]["engines"] = pkg["engines"]
    if "type" in pkg:
        out["notes"].append(f"package.json type={pkg['type']} (ESM/CJS)")


def detect_php(root: Path, out: dict):
    comp = load_json(root / "composer.json")
    if not comp:
        return
    req = {}
    req.update(comp.get("require") or {})
    req.update(comp.get("require-dev") or {})
    if "laravel/framework" in req:
        out["stack"].append(f"Laravel {req['laravel/framework']}")
    for pkg, label in [
        ("livewire/livewire", "Livewire"), ("inertiajs/inertia-laravel", "Inertia"),
        ("laravel/sanctum", "Sanctum"), ("laravel/breeze", "Breeze"),
        ("laravel/jetstream", "Jetstream"), ("laravel/fortify", "Fortify"),
        ("pestphp/pest", "Pest"), ("phpunit/phpunit", "PHPUnit"),
        ("laravel/pint", "Pint"), ("larastan/larastan", "Larastan"),
        ("nunomaduro/larastan", "Larastan"), ("phpstan/phpstan", "PHPStan"),
        ("spatie/laravel-permission", "spatie/laravel-permission"),
        ("laravel/horizon", "Horizon"), ("filament/filament", "Filament"),
    ]:
        if pkg in req:
            out["stack"].append(f"{label} {req[pkg]}")
    if "php" in req:
        out["runtime_versions"]["php"] = req["php"]
    if (root / "artisan").exists():
        out["notes"].append("artisan present: Laravel app (php artisan ...)")
    scripts = comp.get("scripts") or {}
    out["commands"]["composer scripts"] = {k: f"composer {k}  ->  {v}" for k, v in scripts.items()}


def detect_gradle(root: Path, out: dict):
    gradle_files = [p for p in root.rglob("build.gradle*")
                    if not any(part in IGNORE_DIRS for part in p.parts)][:30]
    if not gradle_files and not (root / "settings.gradle").exists() and not (root / "settings.gradle.kts").exists():
        return
    out["stack"].append("Gradle project")
    text = ""
    for p in gradle_files:
        text += read_text(p, 60_000) + "\n"
    for p in (root / "gradle" / "libs.versions.toml",):
        if p.exists():
            text += read_text(p, 60_000)
            out["notes"].append("version catalog: gradle/libs.versions.toml")
    def find(pat):
        m = re.search(pat, text)
        return m.group(1) if m else None
    for label, pat in [
        ("compileSdk", r"compileSdk(?:Version)?\s*[=(]?\s*(\d+)"),
        ("minSdk", r"minSdk(?:Version)?\s*[=(]?\s*(\d+)"),
        ("targetSdk", r"targetSdk(?:Version)?\s*[=(]?\s*(\d+)"),
        ("kotlin", r"kotlin\s*=\s*\"([\d.]+)\""),
        ("agp", r"agp\s*=\s*\"([\d.]+)\""),
    ]:
        v = find(pat)
        if v:
            out["runtime_versions"][label] = v
    low = text.lower()
    for label, key in [
        ("Jetpack Compose", "compose"), ("Hilt", "hilt"), ("Koin", "koin"),
        ("Room", "androidx.room"), ("Retrofit", "retrofit"), ("Ktor", "ktor"),
        ("Firebase", "firebase"), ("Material 3", "material3"),
        ("Navigation Compose", "navigation-compose"), ("DataStore", "datastore"),
        ("Coil", "coil"), ("Kotlin Coroutines", "coroutines"),
        ("ktlint", "ktlint"), ("detekt", "detekt"), ("Kotlin Serialization", "serialization"),
    ]:
        if key in low:
            out["stack"].append(label)
    mods = []
    s = read_text(root / "settings.gradle.kts") or read_text(root / "settings.gradle")
    for m in re.finditer(r"include\(?\s*[\"']([^\"']+)[\"']", s):
        mods.append(m.group(1))
    if mods:
        out["monorepo"].append(f"Gradle modules: {mods[:30]}")
    out["commands"]["gradle (verify task names in the project)"] = {
        "build": "./gradlew assembleDebug",
        "unit tests": "./gradlew testDebugUnitTest",
        "lint": "./gradlew lint",
    }


def detect_python(root: Path, out: dict):
    py = root / "pyproject.toml"
    req = root / "requirements.txt"
    if not py.exists() and not req.exists() and not (root / "manage.py").exists():
        return
    text = read_text(py) + "\n" + read_text(req)
    low = text.lower()
    for label, key in [
        ("Django", "django"), ("FastAPI", "fastapi"), ("Flask", "flask"),
        ("SQLAlchemy", "sqlalchemy"), ("Alembic", "alembic"), ("Pydantic", "pydantic"),
        ("pytest", "pytest"), ("ruff", "ruff"), ("mypy", "mypy"), ("Celery", "celery"),
        ("Poetry", "[tool.poetry]"), ("uv", "[tool.uv]"),
    ]:
        if key in low:
            out["stack"].append(label)
    if (root / "manage.py").exists():
        out["notes"].append("manage.py present: Django (python manage.py ...)")


def detect_misc(root: Path, out: dict):
    if (root / "go.mod").exists():
        m = re.search(r"^go\s+([\d.]+)", read_text(root / "go.mod"), re.M)
        out["stack"].append("Go " + (m.group(1) if m else ""))
    if (root / "Cargo.toml").exists():
        out["stack"].append("Rust (Cargo)")
    if (root / "pubspec.yaml").exists():
        out["stack"].append("Flutter/Dart")
    if (root / "Gemfile").exists():
        out["stack"].append("Ruby (Bundler)")
    if (root / "Dockerfile").exists():
        out["notes"].append("Dockerfile present")
    if (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists() or (root / "compose.yaml").exists():
        out["notes"].append("docker compose file present")
    if (root / "firebase.json").exists():
        fb = load_json(root / "firebase.json") or {}
        out["stack"].append("Firebase config: " + ", ".join(sorted(fb.keys())))
        for f in ("firestore.rules", "firestore.indexes.json", "storage.rules", "database.rules.json"):
            if (root / f).exists():
                out["notes"].append(f"{f} present")
    if (root / ".firebaserc").exists():
        out["notes"].append(".firebaserc present (check project aliases per environment)")
    for f, label in [(".nvmrc", "node"), (".node-version", "node"), (".php-version", "php"),
                     (".python-version", "python"), (".java-version", "java"), (".ruby-version", "ruby")]:
        if (root / f).exists():
            out["runtime_versions"][f] = read_text(root / f).strip()
    if (root / ".tool-versions").exists():
        out["runtime_versions"][".tool-versions"] = read_text(root / ".tool-versions").strip()
    for f in ("aaPanel", ".htaccess"):
        pass


def detect_makefile(root: Path, out: dict):
    mk = root / "Makefile"
    if not mk.exists():
        return
    targets = re.findall(r"^([A-Za-z0-9_.-]+):(?!=)", read_text(mk), re.M)
    targets = [t for t in targets if not t.startswith(".")]
    if targets:
        out["commands"]["Makefile targets"] = {t: f"make {t}" for t in targets[:40]}


def detect_ci(root: Path, out: dict):
    cmds = []
    wf = root / ".github" / "workflows"
    files = list(wf.glob("*.y*ml")) if wf.exists() else []
    for extra in (root / ".gitlab-ci.yml", root / "bitbucket-pipelines.yml", root / ".circleci" / "config.yml"):
        if extra.exists():
            files.append(extra)
    for f in files:
        text = read_text(f)
        for m in re.finditer(r"^\s*-?\s*run:\s*(.+)$", text, re.M):
            c = m.group(1).strip()
            if c and c not in ("|", ">", "|-"):
                cmds.append((f.name, c))
        for m in re.finditer(r"^\s*-\s+((?:npm|pnpm|yarn|composer|php|\./gradlew|gradle|pytest|go|cargo|make)\b.+)$", text, re.M):
            cmds.append((f.name, m.group(1).strip()))
    if cmds:
        seen, uniq = set(), []
        for f, c in cmds:
            if c not in seen:
                seen.add(c)
                uniq.append(f"{f}: {c}")
        out["commands"]["CI commands (best source for the 'correct' verify commands)"] = uniq[:40]
    out["ci_files"] = [str(f.relative_to(root)) for f in files]


def detect_hooks_and_lint(root: Path, out: dict):
    found = []
    for f in (".husky", "lefthook.yml", ".pre-commit-config.yaml", "commitlint.config.js",
              "commitlint.config.cjs", ".eslintrc", ".eslintrc.json", ".eslintrc.cjs",
              "eslint.config.js", "eslint.config.mjs", "eslint.config.ts", ".prettierrc", ".prettierrc.json",
              "prettier.config.js", "biome.json", ".editorconfig", "pint.json", "phpstan.neon",
              "phpstan.neon.dist", "phpcs.xml", ".php-cs-fixer.php", "ruff.toml", ".ktlint",
              "detekt.yml", "config/detekt/detekt.yml", "tsconfig.json"):
        if (root / f).exists():
            found.append(f)
    out["lint_and_hooks_config"] = found


def detect_env(root: Path, out: dict):
    envs = [p.name for p in root.glob(".env*")]
    out["env_files"] = envs
    ex = root / ".env.example"
    if ex.exists():
        keys = []
        for line in read_text(ex).splitlines():
            m = re.match(r"^\s*([A-Z][A-Z0-9_]+)\s*=", line)
            if m:
                keys.append(m.group(1))
        out["env_example_keys"] = keys[:80]
    if any(e == ".env" for e in envs):
        out["notes"].append("A real .env exists locally; ensure it is gitignored and never quoted in docs")


def detect_guides(root: Path, out: dict):
    found = {}
    for f in GUIDE_FILES:
        p = root / f
        if p.exists():
            found[f] = {"lines": len(read_text(p).splitlines())}
    for d in GUIDE_DIRS:
        p = root / d
        if p.exists() and p.is_dir():
            files = [str(x.relative_to(root)) for x in p.rglob("*") if x.is_file()][:30]
            found[d + "/"] = {"files": files}
    out["existing_guides"] = found


def detect_structure(root: Path, depth: int, out: dict):
    tree, generated = [], []
    for rel, is_dir in walk(root, depth):
        s = str(rel)
        if is_dir:
            tree.append(s + "/")
            if rel.name in GENERATED_HINTS or s in GENERATED_HINTS:
                generated.append(s + "/")
    out["tree"] = tree[:200]
    out["possible_generated_or_protected"] = generated


def detect_tests(root: Path, out: dict):
    tests = []
    for pat in ("**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*Test.php", "**/*Test.kt",
                "**/test_*.py", "**/*_test.go"):
        for p in root.glob(pat):
            if any(part in IGNORE_DIRS for part in p.parts):
                continue
            tests.append(str(p.relative_to(root)))
            if len(tests) >= 8:
                break
        if len(tests) >= 8:
            break
    out["sample_test_files"] = tests


def print_text(out: dict):
    def h(t):
        print(f"\n## {t}")
    print(f"# Project scan: {out['root']}")
    h("Stack (detected - verify)")
    for s in dict.fromkeys(out["stack"]):
        print(f"- {s}")
    if out.get("package_manager"):
        print(f"- package manager: {out['package_manager']}")
    h("Runtime versions")
    for k, v in out["runtime_versions"].items():
        print(f"- {k}: {v}")
    h("Commands")
    for group, cmds in out["commands"].items():
        print(f"### {group}")
        items = cmds.items() if isinstance(cmds, dict) else enumerate(cmds)
        for k, v in items:
            print(f"- {v}" if not isinstance(cmds, dict) else f"- {v}")
    h("Monorepo hints")
    for m in out["monorepo"]:
        print(f"- {m}")
    h("Notes")
    for n in out["notes"]:
        print(f"- {n}")
    h("Lint/format/hooks config present")
    print(", ".join(out.get("lint_and_hooks_config", [])) or "(none)")
    h("Existing guides")
    for k, v in out.get("existing_guides", {}).items():
        print(f"- {k}: {v}")
    h("Env files / example keys")
    print(", ".join(out.get("env_files", [])) or "(none)")
    if out.get("env_example_keys"):
        print("keys:", ", ".join(out["env_example_keys"]))
    h("Possible generated/protected dirs")
    for g in out.get("possible_generated_or_protected", []):
        print(f"- {g}")
    h("Sample test files")
    for t in out.get("sample_test_files", []):
        print(f"- {t}")
    h("Tree")
    for t in out.get("tree", []):
        print(t)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--depth", type=int, default=2, help="tree depth (default 2)")
    ap.add_argument("--text", action="store_true", help="human-readable output instead of JSON")
    args = ap.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        sys.exit(2)

    out = {
        "root": str(root), "stack": [], "package_manager": None,
        "runtime_versions": {}, "commands": {}, "monorepo": [], "notes": [],
    }
    detect_js(root, out)
    detect_php(root, out)
    detect_gradle(root, out)
    detect_python(root, out)
    detect_misc(root, out)
    detect_makefile(root, out)
    detect_ci(root, out)
    detect_hooks_and_lint(root, out)
    detect_env(root, out)
    detect_guides(root, out)
    detect_structure(root, args.depth, out)
    detect_tests(root, out)

    out["stack"] = list(dict.fromkeys(out["stack"]))
    if args.text:
        print_text(out)
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
