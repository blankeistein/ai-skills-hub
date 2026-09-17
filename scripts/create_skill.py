#!/usr/bin/env python3
"""
create_skill.py
CLI utility to scaffold a new AI agent skill from the standard template.

Usage:
    python scripts/create_skill.py <skill-name> --description "<description>"
"""

import sys
import os
import shutil
import argparse
import re
from pathlib import Path


def create_skill(name: str, description: str):
    root_dir = Path(__file__).resolve().parent.parent
    template_dir = root_dir / "templates" / "skill-template"
    target_dir = root_dir / "skills" / name

    # Validate name format
    if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name):
        print(f"Error: Skill name '{name}' must be lowercase alphanumeric with hyphens (e.g., 'flutter-lint-audit')")
        sys.exit(1)

    if target_dir.exists():
        print(f"Error: Skill directory '{target_dir}' already exists.")
        sys.exit(1)

    if not template_dir.exists():
        print(f"Error: Template directory '{template_dir}' not found.")
        sys.exit(1)

    # Copy template
    shutil.copytree(template_dir, target_dir)

    # Replace placeholders in SKILL.md
    skill_file = target_dir / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    
    # Capitalize words for title
    title = " ".join(word.capitalize() for word in name.split("-"))
    
    content = content.replace("your-skill-name", name)
    content = content.replace("Clear, third-person explanation of what this skill does and when an AI agent should activate it. Include specific triggers and use cases.", description)
    content = content.replace("# Skill Name", f"# {title}")

    skill_file.write_text(content, encoding="utf-8")

    print(f"Successfully created skill: '{name}'")
    print(f"Location: {target_dir}")
    print("\nNext steps:")
    print(f"1. Edit {skill_file.relative_to(root_dir)} to define your instructions.")
    print(f"2. Add reference guides in {target_dir.relative_to(root_dir)}/references/ if needed.")
    print(f"3. Run 'python scripts/validate_skills.py' to verify.")


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new AI agent skill.")
    parser.add_argument("name", help="Name of the skill in kebab-case (e.g., 'react-performance-audit')")
    parser.add_argument("--description", "-d", default="Describe what this skill does and when the AI should activate it.", help="Skill trigger description")

    args = parser.parse_args()
    create_skill(args.name, args.description)


if __name__ == "__main__":
    main()
