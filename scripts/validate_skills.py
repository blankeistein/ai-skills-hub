#!/usr/bin/env python3
"""
validate_skills.py
Validates skill definitions against the standard AI Agent Skills specification.

Checks:
1. Directory structure (skills/<skill-name>/SKILL.md)
2. Valid YAML frontmatter (name, description)
3. Skill name convention (lowercase, hyphens, alphanumeric)
4. Description quality & completeness
5. Relative markdown links resolution (no broken references)
6. Generates/updates catalog.json
"""

import sys
import os
import re
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Color helpers for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def parse_frontmatter(content: str):
    """Simple parser for YAML frontmatter between triple dashes."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "Missing opening '---' frontmatter delimiter"

    end_idx = -1
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return None, "Missing closing '---' frontmatter delimiter"

    yaml_block = lines[1:end_idx]
    data = {}
    current_key = None
    current_val = []

    for line in yaml_block:
        # Check for top-level key
        key_match = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*)$", line)
        if key_match:
            if current_key:
                val_str = "\n".join(current_val).strip()
                if val_str.startswith(">-") or val_str.startswith(">"):
                    val_str = " ".join(val_str.split("\n")[1:]).strip() if "\n" in val_str else ""
                data[current_key] = val_str
            current_key = key_match.group(1).strip()
            val_first = key_match.group(2).strip()
            current_val = [val_first] if val_first else []
        elif current_key is not None:
            current_val.append(line.strip())

    if current_key:
        val_str = "\n".join(current_val).strip()
        if val_str.startswith(">-") or val_str.startswith(">") or val_str.startswith("|"):
            # Fold multiline string
            lines_val = val_str.split("\n")[1:] if "\n" in val_str else []
            val_str = " ".join(l.strip() for l in lines_val if l.strip())
        # Strip quotes if present
        if (val_str.startswith('"') and val_str.endswith('"')) or (val_str.startswith("'") and val_str.endswith("'")):
            val_str = val_str[1:-1]
        data[current_key] = val_str

    return data, None


def check_markdown_links(file_path: Path):
    """Find all relative markdown links and verify target files exist."""
    content = file_path.read_text(encoding="utf-8")
    errors = []

    # Strip fenced code blocks (e.g. ```lang ... ``` or ````lang ... ````)
    # so template code examples aren't mistaken for real relative links.
    clean_content = re.sub(r"(?ms)^(`{3,})[^\n]*\n.*?\n\1\s*$", "", content)
    # Also strip inline code spans
    clean_content = re.sub(r"`[^`\n]+`", "", clean_content)

    # Regex matching markdown links [text](target) excluding external URLs and anchor-only links
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for match in link_pattern.finditer(clean_content):
        target = match.group(2).strip()
        # Ignore external links, mailto, and in-page anchors
        if target.startswith("http://") or target.startswith("https://") or target.startswith("mailto:") or target.startswith("#"):
            continue
        
        # Strip query parameters or internal hash
        clean_target = target.split("#")[0].split("?")[0]
        if not clean_target:
            continue
        
        target_path = (file_path.parent / clean_target).resolve()
        if not target_path.exists():
            errors.append(f"Broken link '{target}' -> target not found: {clean_target}")

    return errors


def validate_skill_dir(skill_dir: Path):
    """Validate an individual skill directory."""
    errors = []
    warnings = []
    skill_info = {}

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"Missing required file: {skill_file.name}")
        return False, errors, warnings, skill_info

    content = skill_file.read_text(encoding="utf-8")
    data, err = parse_frontmatter(content)
    if err:
        errors.append(f"Frontmatter error: {err}")
        return False, errors, warnings, skill_info

    # Validate Name
    name = data.get("name", "").strip()
    if not name:
        errors.append("Frontmatter missing 'name' field")
    else:
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
            errors.append(f"Skill name '{name}' must be lowercase alphanumeric with hyphens (e.g., 'android-code-audit')")
        if name != skill_dir.name:
            warnings.append(f"Skill name '{name}' does not match directory name '{skill_dir.name}'")

    # Validate Description
    desc = data.get("description", "").strip()
    if not desc:
        errors.append("Frontmatter missing 'description' field")
    elif len(desc) < 30:
        warnings.append(f"Description is very brief ({len(desc)} chars). Provide clear trigger scenarios and instructions.")

    # Check Markdown links in SKILL.md
    link_errors = check_markdown_links(skill_file)
    errors.extend(link_errors)

    # Check references folder if present
    ref_dir = skill_dir / "references"
    if ref_dir.exists() and ref_dir.is_dir():
        for ref_file in ref_dir.glob("*.md"):
            ref_link_errors = check_markdown_links(ref_file)
            for e in ref_link_errors:
                errors.append(f"In {ref_file.name}: {e}")

    skill_info = {
        "name": name or skill_dir.name,
        "directory": skill_dir.name,
        "path": f"skills/{skill_dir.name}",
        "description": desc,
        "has_references": ref_dir.exists(),
        "has_scripts": (skill_dir / "scripts").exists(),
        "has_examples": (skill_dir / "examples").exists(),
        "has_assets": (skill_dir / "assets").exists()
    }

    is_valid = len(errors) == 0
    return is_valid, errors, warnings, skill_info


def main():
    root_dir = Path(__file__).resolve().parent.parent
    skills_dir = root_dir / "skills"

    print(f"\n{BOLD}{CYAN}=== AI Agent Skills Validator ==={RESET}")
    print(f"Scanning directory: {skills_dir}\n")

    if not skills_dir.exists():
        print(f"{RED}[FAIL] 'skills/' directory not found!{RESET}")
        sys.exit(1)

    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if not skill_dirs:
        print(f"{YELLOW}[WARN] No skill directories found in 'skills/'{RESET}")
        sys.exit(0)

    total_skills = len(skill_dirs)
    passed_skills = 0
    catalog = []

    for s_dir in sorted(skill_dirs, key=lambda x: x.name):
        valid, errors, warnings, info = validate_skill_dir(s_dir)
        
        status_tag = f"{GREEN}[PASS]{RESET}" if valid else f"{RED}[FAIL]{RESET}"
        print(f"{status_tag} {BOLD}{s_dir.name}{RESET}")

        if valid:
            passed_skills += 1
            catalog.append(info)

        for w in warnings:
            print(f"   {YELLOW}↳ WARNING: {w}{RESET}")
        for e in errors:
            print(f"   {RED}↳ ERROR: {e}{RESET}")

    # Generate catalog.json
    catalog_file = root_dir / "catalog.json"
    catalog_data = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "AI Skills Catalog",
        "description": "Index of all curated AI agent skills available in this repository.",
        "skills_count": len(catalog),
        "skills": catalog
    }
    catalog_file.write_text(json.dumps(catalog_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{GREEN}[OK] Updated catalog manifest: {catalog_file.name}{RESET}")

    # Summary
    print(f"\n{BOLD}Result: {passed_skills}/{total_skills} skills passed validation.{RESET}\n")

    if passed_skills < total_skills:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
