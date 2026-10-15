#!/usr/bin/env python3
"""Extract raw design-token candidates from a repo to seed DESIGN.md.

Looks at: CSS custom properties, Tailwind config, Compose Color/Type/Shape
files, Android colors.xml, theme JSON/TS files, @font-face / Google Fonts
links, fonts in assets, icon libraries, UI component libraries, and the
most frequently used hex colors across source files.

Detector only: it finds candidates. A human/AI must decide which are real
tokens versus one-off values, and assign semantic roles.

Usage:
    python extract_design_tokens.py <repo-path> [--json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

IGNORE_DIRS = {
    ".git", "node_modules", "vendor", "dist", "build", ".next", ".gradle",
    ".idea", "__pycache__", ".venv", "venv", "target", ".dart_tool", "Pods",
    ".cache", "coverage", "storage", ".firebase", "public/build",
}
SRC_EXT = {".css", ".scss", ".sass", ".less", ".ts", ".tsx", ".js", ".jsx", ".vue",
           ".svelte", ".html", ".blade.php", ".php", ".kt", ".xml", ".dart", ".json"}
MAX_FILE = 300_000

HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
CSS_VAR = re.compile(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;}{]+);")
KT_COLOR = re.compile(r"val\s+([A-Za-z0-9_]+)\s*=\s*Color\(\s*(0x[0-9A-Fa-f]{6,8})\s*\)")
XML_COLOR = re.compile(r"<color\s+name=\"([^\"]+)\"[^>]*>\s*(#[0-9A-Fa-f]{3,8})\s*</color>")
FONT_FACE = re.compile(r"font-family\s*:\s*([^;}{]+)[;}]")
GOOGLE_FONTS = re.compile(r"fonts\.googleapis\.com/[^\"'\s)]+")
KT_FONT = re.compile(r"(FontFamily\([^)]*\)|Font\(\s*R\.font\.[A-Za-z0-9_]+[^)]*\)|GoogleFont\(\"[^\"]+\"\))")
KT_SHAPE = re.compile(r"RoundedCornerShape\(\s*([0-9.]+)\.dp\s*\)")
KT_TEXT = re.compile(r"fontSize\s*=\s*([0-9.]+)\.sp")
RADIUS = re.compile(r"border-radius\s*:\s*([^;}{]+)[;}]")
SPACING_PX = re.compile(r"(?:padding|margin|gap)[a-z-]*\s*:\s*([0-9]+(?:\.[0-9]+)?(?:px|rem))")

UI_LIBS = {
    "tailwindcss": "Tailwind CSS", "@radix-ui/react-slot": "shadcn/ui (Radix)",
    "@mui/material": "MUI", "antd": "Ant Design", "@chakra-ui/react": "Chakra UI",
    "bootstrap": "Bootstrap", "daisyui": "daisyUI", "@headlessui/react": "Headless UI",
    "lucide-react": "lucide icons", "react-icons": "react-icons",
    "@heroicons/react": "Heroicons", "@fortawesome/fontawesome-free": "Font Awesome",
    "framer-motion": "Framer Motion", "motion": "Motion", "class-variance-authority": "cva (variants)",
    "storybook": "Storybook", "@storybook/react": "Storybook",
}


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for f in filenames:
            p = Path(dirpath) / f
            if p.suffix.lower() in SRC_EXT or f.endswith(".blade.php"):
                try:
                    if p.stat().st_size <= MAX_FILE:
                        yield p
                except OSError:
                    pass


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"error: {root} not a directory", file=sys.stderr)
        sys.exit(2)

    res = {
        "root": str(root),
        "css_variables": {},          # file -> {name: value}
        "tailwind_config": None,
        "compose_colors": {},         # file -> {name: hex}
        "android_xml_colors": {},     # file -> {name: hex}
        "fonts": {"font_family_decls": [], "google_fonts_links": [], "compose_fonts": [], "font_files": []},
        "radii": Counter(), "spacing_px": Counter(), "compose_corner_dp": Counter(),
        "compose_font_sp": Counter(), "hex_usage": Counter(),
        "ui_libraries": [], "component_dirs": [], "dark_mode_hints": [], "token_files": [],
    }

    # package.json -> UI libs
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(read(pkg_path))
            deps = {**(pkg.get("dependencies") or {}), **(pkg.get("devDependencies") or {})}
            res["ui_libraries"] = sorted({UI_LIBS[k] for k in deps if k in UI_LIBS})
        except Exception:
            pass

    # Gradle -> Compose / Material
    for g in root.rglob("build.gradle*"):
        if any(part in IGNORE_DIRS for part in g.parts):
            continue
        t = read(g).lower()
        if "compose" in t and "Jetpack Compose" not in res["ui_libraries"]:
            res["ui_libraries"].append("Jetpack Compose")
        if "material3" in t and "Material 3" not in res["ui_libraries"]:
            res["ui_libraries"].append("Material 3")

    # Tailwind config
    for name in ("tailwind.config.ts", "tailwind.config.js", "tailwind.config.cjs", "tailwind.config.mjs"):
        p = root / name
        if p.exists():
            text = read(p)
            res["tailwind_config"] = {
                "file": name,
                "dark_mode": (re.search(r"darkMode\s*:\s*([^,\n]+)", text) or [None, None])[1],
                "hex_colors": sorted(set(HEX.findall(text)))[:60],
                "has_extend_colors": bool(re.search(r"extend\s*:\s*{[^}]*colors", text, re.S)),
                "has_fontFamily": "fontFamily" in text,
                "has_borderRadius": "borderRadius" in text,
                "snippet": text[:1500],
            }
            break

    for p in iter_files(root):
        rel = str(p.relative_to(root))
        text = read(p)
        ext = p.suffix.lower()

        if ext in {".css", ".scss", ".sass", ".less", ".html", ".vue", ".svelte"} or rel.endswith(".blade.php"):
            vars_ = {}
            for m in CSS_VAR.finditer(text):
                vals = vars_.setdefault(m.group(1), [])
                v = m.group(2).strip()
                if v not in vals:
                    vals.append(v)  # keep every value (light/dark/theme overrides)
            if len(vars_) >= 3:
                res["css_variables"][rel] = {k: " | ".join(v) for k, v in list(vars_.items())[:80]}
                res["token_files"].append(rel)
            for m in FONT_FACE.finditer(text):
                v = m.group(1).strip()
                if v not in res["fonts"]["font_family_decls"]:
                    res["fonts"]["font_family_decls"].append(v)
            res["fonts"]["google_fonts_links"] += [m.group(0) for m in GOOGLE_FONTS.finditer(text)]
            for m in RADIUS.finditer(text):
                res["radii"][m.group(1).strip()] += 1
            for m in SPACING_PX.finditer(text):
                res["spacing_px"][m.group(1)] += 1
            if "prefers-color-scheme: dark" in text or re.search(r"\.dark\b|\[data-theme=.dark.\]", text):
                res["dark_mode_hints"].append(rel)

        if ext == ".kt":
            cs = {m.group(1): m.group(2) for m in KT_COLOR.finditer(text)}
            if cs:
                res["compose_colors"][rel] = dict(list(cs.items())[:80])
                res["token_files"].append(rel)
            for m in KT_FONT.finditer(text):
                s = m.group(1)
                if s not in res["fonts"]["compose_fonts"]:
                    res["fonts"]["compose_fonts"].append(s)
            for m in KT_SHAPE.finditer(text):
                res["compose_corner_dp"][m.group(1)] += 1
            for m in KT_TEXT.finditer(text):
                res["compose_font_sp"][m.group(1)] += 1
            if "isSystemInDarkTheme" in text or "darkColorScheme" in text:
                res["dark_mode_hints"].append(rel)

        if ext == ".xml" and "/values" in rel:
            cs = {m.group(1): m.group(2) for m in XML_COLOR.finditer(text)}
            if cs:
                res["android_xml_colors"][rel] = dict(list(cs.items())[:80])
                res["token_files"].append(rel)

        if ext in {".ts", ".tsx", ".js", ".jsx", ".json"} and re.search(r"(theme|tokens|colors|palette)", p.stem, re.I):
            res["token_files"].append(rel)

        # global hex frequency (skip lockfiles/json data noise)
        if ext in {".css", ".scss", ".ts", ".tsx", ".js", ".jsx", ".vue", ".svelte", ".html", ".kt", ".xml", ".php"}:
            for h in HEX.findall(text):
                res["hex_usage"][h.upper()] += 1

    # fonts bundled
    for pat in ("**/*.ttf", "**/*.otf", "**/*.woff", "**/*.woff2"):
        for p in root.glob(pat):
            if any(part in IGNORE_DIRS for part in p.parts):
                continue
            res["fonts"]["font_files"].append(str(p.relative_to(root)))
    res["fonts"]["font_files"] = res["fonts"]["font_files"][:30]
    res["fonts"]["google_fonts_links"] = list(dict.fromkeys(res["fonts"]["google_fonts_links"]))[:10]

    # component dirs
    for cand in ("src/components/ui", "src/components", "components/ui", "components",
                 "resources/js/components", "resources/views/components", "app/src/main/java",
                 "core/designsystem", "design-system", "src/design-system", "src/ui"):
        p = root / cand
        if p.exists() and p.is_dir():
            names = sorted(x.name for x in p.iterdir() if not x.name.startswith("."))[:40]
            res["component_dirs"].append({"dir": cand, "entries": names})

    res["token_files"] = sorted(dict.fromkeys(res["token_files"]))
    res["dark_mode_hints"] = sorted(dict.fromkeys(res["dark_mode_hints"]))[:15]
    for k in ("radii", "spacing_px", "compose_corner_dp", "compose_font_sp", "hex_usage"):
        res[k] = dict(Counter(res[k]).most_common(25))

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return

    print(f"# Design token scan: {res['root']}\n")
    print("## UI libraries:", ", ".join(res["ui_libraries"]) or "(none detected)")
    print("\n## Likely token files")
    for f in res["token_files"][:30]:
        print(f"- {f}")
    if res["tailwind_config"]:
        t = res["tailwind_config"]
        print(f"\n## Tailwind ({t['file']}): darkMode={t['dark_mode']}, extend.colors={t['has_extend_colors']}, "
              f"fontFamily={t['has_fontFamily']}, borderRadius={t['has_borderRadius']}")
        print("hex in config:", ", ".join(t["hex_colors"]) or "(none)")
    for title, key in (("CSS custom properties", "css_variables"),
                       ("Compose colors", "compose_colors"),
                       ("Android XML colors", "android_xml_colors")):
        if res[key]:
            print(f"\n## {title}")
            for f, items in res[key].items():
                print(f"### {f}")
                for k, v in list(items.items())[:40]:
                    print(f"- {k}: {v}")
    print("\n## Fonts")
    for k, v in res["fonts"].items():
        if v:
            print(f"- {k}: {v}")
    for title, key in (("Border radius (css) frequency", "radii"), ("Spacing frequency (css)", "spacing_px"),
                       ("Compose RoundedCornerShape dp", "compose_corner_dp"), ("Compose fontSize sp", "compose_font_sp"),
                       ("Most used hex colors across source", "hex_usage")):
        if res[key]:
            print(f"\n## {title}")
            print(", ".join(f"{k} (x{v})" for k, v in res[key].items()))
    if res["component_dirs"]:
        print("\n## Component directories")
        for c in res["component_dirs"]:
            print(f"- {c['dir']}: {', '.join(c['entries'])}")
    if res["dark_mode_hints"]:
        print("\n## Dark mode hints in:", ", ".join(res["dark_mode_hints"]))
    print("\nNOTE: candidates only. Raw hex frequency may include one-off values; decide roles/tokens deliberately.")


if __name__ == "__main__":
    main()
