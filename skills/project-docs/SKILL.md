---
name: project-docs
description: Create complete, accurate software project documentation (README, architecture, how-it-works, data model, API reference, setup, deployment, configuration, testing, contributing, troubleshooting, ADR) by actually reading the codebase. Use this skill whenever the user wants to document a software project, app, website, API, library or repo, even if they only say "buat dokumentasi", "dokumentasikan projek ini", "jelaskan struktur dan cara kerja projek", "bikin README", "dokumentasi teknis", "onboarding doc", "handover", "arsitektur sistem", "technical documentation", "document this codebase", or upload code/zip/folder and ask how it is organized or how it works. Also use it to update, restructure or audit existing docs. Covers web (Laravel/PHP, React/TypeScript, Node), Android (Kotlin/Jetpack Compose), Firebase, and deployment (cPanel, Cloud Run, VPS) but works for any stack.
---

# Project Documentation

Produce documentation that a new engineer could use to understand, run, and safely change a project without asking the author. The code is the source of truth: read it, then write. Never invent features, endpoints, commands, or config that you did not see.

A good doc set answers six questions, in this order:

1. **What is this?** purpose, users, scope
2. **How is it organized?** structure, modules, tech stack
3. **How does it work?** the main flows end to end, and why it was built that way
4. **How do I run it?** setup, config, scripts
5. **How do I ship it?** build, deploy, environments
6. **How do I change it safely?** conventions, tests, pitfalls

## Workflow

### 1. Scope (keep it short)

Decide these four things. Infer from the request and the files; ask the user only if a wrong guess would waste a lot of work, and ask everything in one message.

- **Audience**: new teammate, client/handover, open-source user, or the author's future self. Default: a new developer joining the project.
- **Depth**: Lite, Standard, or Full (see table below). Default: Standard.
- **Language**: write in the language the user writes in. Indonesian request → Indonesian docs. Keep code identifiers, commands, file paths and well-known technical terms in English.
- **Format**: Markdown files in a `docs/` folder by default (renders on GitHub/GitLab, easy to version). Use the docx or pdf skills only if the user asks for Word/PDF.

| Depth | When | Files |
|---|---|---|
| **Lite** | small project, quick handover, "just a README" | `README.md` only, with a short architecture and how-it-works section |
| **Standard** (default) | most apps | `README.md` + overview, architecture, how-it-works, setup, configuration, deployment |
| **Full** | production systems, client handover, teams | Standard + data model, API reference, testing, contributing, troubleshooting, ADRs, changelog |

### 2. Discover the codebase

Never document from the file names alone. Build a factual picture first.

- If the code is on disk (project workspace, cloned repo, or unzipped archive), run the scanner. It prints stack, tree, scripts, env var names, routes, data stores and CI in one pass:
  ```bash
  python <path-to-skill>/scripts/scan_project.py <project-root>
  ```
  Use the path where this SKILL.md lives (e.g., `skills/project-docs/scripts/scan_project.py`). If the script fails or cannot run, fall back to viewing files and directory listings.
- Then read the files that carry the real logic. `references/analysis-guide.md` lists, per stack, what to open and what to extract (entry points, routing, state, auth, data access, background work, build/deploy config). Read it for the stack you detected.
- If there is no code access (the user only describes the project or pastes fragments), interview briefly, document what is known, and mark the rest `TODO(verify)`. Say plainly which sections are thin and why.

While reading, keep a private list of: entry points, main flows (user actions that cross layers), external services, data stores, config keys, and anything surprising (workarounds, odd naming, dead code). Surprises are often the most valuable thing to document.

### 3. Plan the doc set

Pick files from the depth level, then drop any that have nothing real to say (for example no API reference for a project with no API). Do not pad. Use the index below and the templates in `references/doc-templates.md`.

| File | Purpose |
|---|---|
| `README.md` (repo root) | front door: what, why, quick start, link to docs |
| `docs/README.md` | documentation index and reading order |
| `docs/01-overview.md` | purpose, users, features, scope, glossary |
| `docs/02-architecture.md` | components, tech stack, folder structure, diagrams, key decisions |
| `docs/03-how-it-works.md` | end-to-end flows (auth, main user journeys, background jobs, sync) |
| `docs/04-data-model.md` | entities, relations, collections/tables, rules, migrations |
| `docs/05-api-reference.md` | endpoints / functions / events with request, response, errors, auth |
| `docs/06-setup-and-development.md` | prerequisites, install, run, scripts, daily workflow |
| `docs/07-configuration.md` | env vars and config, with meaning, required/optional, example (no secrets) |
| `docs/08-deployment.md` | build, environments, deploy steps, rollback, hosting specifics |
| `docs/09-testing.md` | how to run tests, what is covered, how to add tests |
| `docs/10-contributing.md` | code style, branching, commit and PR conventions, review checklist |
| `docs/11-troubleshooting.md` | known problems with cause and fix, FAQ |
| `docs/adr/NNNN-title.md` | one architecture decision each: context, decision, consequences |
| `CHANGELOG.md` | notable changes per version |

### 4. Write

Write each file from its template, filling it with facts from step 2. Principles that matter most:

- **Trace real flows for "how it works".** Pick the 3–6 most important user actions (login, checkout, send message, upload and process a file) and follow each through the layers: UI → handler/controller → service → data store → external call → response. Name the actual files and functions at each hop. This is what turns a file tour into understanding.
- **Explain why, not only what.** When code shows a deliberate choice (offline-first sync, queue for heavy jobs, Firestore instead of SQL, encryption of stored data), say what problem it solves. Mark inferred reasons as such ("likely because…") unless the code or comments state them.
- **Cite paths.** Refer to `app/Http/Controllers/OrderController.php` rather than "the order controller", so readers can jump to the source and you can be checked.
- **Commands must be copy-pasteable** and match the project's real scripts, package manager (check the lockfile), and versions.
- **Diagrams only where they clarify.** Use Mermaid (see `references/diagrams.md`): one architecture diagram, one or two sequence diagrams for key flows, an ER diagram when there are more than ~3 related entities. Keep each under ~15 nodes.
- **Secrets:** document config key names, purpose and format. Never copy real keys, tokens, passwords or connection strings into docs. Use placeholders like `YOUR_API_KEY`.
- **Be honest about gaps.** Use `TODO(verify): …` for anything you could not confirm, and list them at the end of your reply. A visible gap is better than a confident fabrication.
- **Keep it maintainable.** Prefer short sections, tables for reference data, and links between docs instead of repeating content. State in `docs/README.md` which files must be updated when what changes (for example, "update 07-configuration.md when you add an env var").

### 5. Verify before delivering

Run this checklist against what you wrote:

- Every file path, command, script name, and env var mentioned exists in the code (grep to confirm anything doubtful).
- Setup steps are in a working order and nothing needed is missing (runtime versions, DB creation, migrations, seeds, build step).
- Flows in `03-how-it-works.md` match the actual code path, not what the names suggest.
- Diagrams render (valid Mermaid) and agree with the text.
- Links between docs resolve; the index lists every file.
- No secrets, no personal data, no placeholder text left like `[TODO]` unless it is a deliberate `TODO(verify)`.
- Tone and language are consistent with the chosen language.

### 6. Deliver

- Write files directly following the `docs/` layout (and root `README.md`), or to the output directory requested by the user. If delivering as an archive or requested, bundle the docs into a `.zip`.
- In the reply, give a short summary: which files were created, the 3–5 most important things the docs explain, and the list of `TODO(verify)` gaps or questions for the author. Offer a next step only if it is concrete (for example "generate the OpenAPI spec" or "convert to a single PDF").

## Updating or auditing existing docs

If docs already exist, read them first and keep their structure and voice unless the user wants a restructure. Compare them against the code and report drift (missing endpoints, renamed env vars, outdated commands) before rewriting. Preserve content that is still true; fix only what is wrong or missing, and say what you changed.

## Reference files

- `references/doc-templates.md`: a template for every file in the doc set. Read it when you start writing.
- `references/analysis-guide.md`: what to read and extract per stack (Laravel, React/TypeScript, Node, Kotlin/Compose, Firebase, Python, Docker/hosting). Read it during discovery.
- `references/diagrams.md`: Mermaid patterns for architecture, sequence, ER, state and deployment diagrams.
- `scripts/scan_project.py`: one-shot project scanner (stack, tree, scripts, env var names, routes, data stores, CI). It reads `.env.example`-style files only, never real `.env` values.
