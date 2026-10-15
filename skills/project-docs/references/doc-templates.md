# Documentation templates

Fill every section from facts found in the code. Delete sections that do not apply instead of leaving them empty. Replace `<...>` placeholders. Mark unconfirmed facts with `TODO(verify)`.

## Contents
- [Root README.md](#root-readmemd)
- [docs/README.md (index)](#docsreadmemd-index)
- [01-overview.md](#01-overviewmd)
- [02-architecture.md](#02-architecturemd)
- [03-how-it-works.md](#03-how-it-worksmd)
- [04-data-model.md](#04-data-modelmd)
- [05-api-reference.md](#05-api-referencemd)
- [06-setup-and-development.md](#06-setup-and-developmentmd)
- [07-configuration.md](#07-configurationmd)
- [08-deployment.md](#08-deploymentmd)
- [09-testing.md](#09-testingmd)
- [10-contributing.md](#10-contributingmd)
- [11-troubleshooting.md](#11-troubleshootingmd)
- [ADR](#adr-adrnnnn-titlemd)
- [CHANGELOG.md](#changelogmd)

---

## Root README.md

````markdown
# <Project name>

<One sentence: what it does and for whom.>

## Features
- <3-7 concrete, user-visible features>

## Tech stack
| Layer | Technology |
|---|---|
| Frontend / App | <e.g. React 18 + TypeScript + Vite> |
| Backend | <e.g. Laravel 11 (PHP 8.3)> |
| Database / Storage | <e.g. MySQL 8, Firestore> |
| Hosting | <e.g. cPanel, Cloud Run> |

## Quick start
<The shortest path that works: clone, install, configure, run. 5-8 lines of commands.>

## Documentation
Full docs are in [`docs/`](docs/README.md): architecture, how it works, setup, deployment.

## Project structure (short)
<Top-level folders with a one-line purpose each.>

## License / Contact
<If known.>
````

---

## docs/README.md (index)

````markdown
# <Project> documentation

**Last verified against code:** <date or commit>
**Audience:** <who>

## Reading order
1. [Overview](01-overview.md): what and why
2. [Architecture](02-architecture.md): how it is built
3. [How it works](03-how-it-works.md): main flows end to end
4. ... (list every file with one line)

## Keep docs in sync
| When you change... | Update... |
|---|---|
| env vars / config | 07-configuration.md |
| routes / endpoints | 05-api-reference.md |
| DB schema / collections | 04-data-model.md |
| deploy process | 08-deployment.md |
````

---

## 01-overview.md

````markdown
# Overview

## Purpose
<The problem this solves and for whom. 1-2 paragraphs.>

## Users and roles
| Role | What they can do |
|---|---|

## Feature list
| Feature | Description | Main code location |
|---|---|---|

## Scope
**In scope:** ...
**Out of scope / not implemented:** ...

## Glossary
| Term | Meaning |
|---|---|
<Domain words, abbreviations, local-language terms used in code.>
````

---

## 02-architecture.md

````markdown
# Architecture

## Summary
<Style in 2-3 sentences: monolith / SPA + API / offline-first mobile + cloud sync / serverless, etc.>

## System diagram
<Mermaid flowchart: clients, backend, data stores, external services.>

## Components
| Component | Responsibility | Tech | Location |
|---|---|---|---|

## Tech stack and versions
| Area | Tool | Version | Notes |
|---|---|---|---|

## Folder structure
<Annotated tree, 2-3 levels, one comment per meaningful folder.>

## Layers and dependencies
<How code is layered (Controller -> Service -> Repository -> Model; UI -> ViewModel -> Repository -> Room/Firestore). What may depend on what.>

## Cross-cutting concerns
- **Authentication & authorization:** ...
- **State management:** ...
- **Error handling & logging:** ...
- **Caching / offline:** ...
- **Security:** (encryption, validation, rules)
- **Performance:** ...

## External services
| Service | Used for | Where configured |
|---|---|---|

## Key decisions
<Short bullets, link to ADRs: "We use X because Y.">
````

---

## 03-how-it-works.md

One section per main flow. Aim for 3-6 flows.

````markdown
# How it works

## Flow 1: <User action, e.g. "Student sends a message">

**Trigger:** <what starts it>
**Actors:** <user, service, job>

<Mermaid sequenceDiagram>

**Step by step**
1. <UI event>: `path/to/File.kt` -> `onSend()`
2. <validation / mapping>: `path/to/Service.php::method`
3. <persistence>: writes to `<collection/table>`
4. <side effects>: notification, queue job, sync
5. <response / UI update>

**Data touched:** <tables/collections/keys>
**Failure modes:** <what happens on timeout, offline, invalid input, permission denied>
**Notes / gotchas:** <non-obvious behavior>

## Background jobs and scheduled tasks
| Job | Trigger / schedule | What it does | Location |
|---|---|---|---|

## Lifecycle / state machines
<If entities have statuses (order: pending -> paid -> shipped), show a stateDiagram and who can trigger each transition.>
````

---

## 04-data-model.md

````markdown
# Data model

## Overview
<Database type(s), where the schema lives (migrations, rules, Room entities), naming conventions.>

## ER diagram
<Mermaid erDiagram.>

## Entities
### <Entity / table / collection>
**Purpose:** ...
**Location:** `path`
| Field | Type | Required | Description |
|---|---|---|---|
**Relations:** ...
**Indexes / constraints:** ...
**Access rules:** (Firestore rules, policies, soft delete, etc.)

## Migrations and seeding
<How schema changes are applied; commands.>

## Data lifecycle
<Retention, backups, soft deletes, encryption of sensitive fields.>
````

---

## 05-api-reference.md

````markdown
# API reference

**Base URL:** `<env-specific>`
**Auth:** <Bearer token / session / Firebase ID token>
**Format:** JSON · **Errors:** <standard error shape>

## <Resource group>

### `METHOD /path`
Purpose: ...
Auth: required / role

**Request**
| Param | In (path/query/body) | Type | Required | Notes |
|---|---|---|---|---|

**Response 200**
```json
{ }
```
**Errors:** `401` ..., `422` ... (validation fields)
Implemented in: `path/to/Controller.php::method`
````

For non-HTTP interfaces (Cloud Functions, callable functions, Realtime Database paths, events), keep the same shape: name, trigger, input, output, errors, location.

---

## 06-setup-and-development.md

````markdown
# Setup and development

## Prerequisites
| Tool | Version | Check |
|---|---|---|
| PHP | >= 8.2 | `php -v` |

## Install
<Numbered, copy-pasteable commands: clone, dependencies, env file, key generation, DB create + migrate + seed, build.>

## Run locally
| Goal | Command |
|---|---|
| Dev server | `...` |
| Build | `...` |
| Lint / format | `...` |
| Tests | `...` |

## Default accounts / seed data
<Only non-secret demo credentials the project already documents or seeds.>

## Daily workflow
<How to add a feature: where code goes, what to run before committing.>

## IDE and tooling notes
<Android Studio version, JDK, emulator, Node version manager, Docker, etc.>
````

---

## 07-configuration.md

````markdown
# Configuration

Config is read from: `<.env / local.properties / firebase config / remote config>`.

| Key | Required | Example (fake) | Description | Used in |
|---|---|---|---|---|
| `APP_URL` | yes | `http://localhost:8000` | base URL | `config/app.php` |

## Environments
| Environment | Differences |
|---|---|
| local / staging / production | ... |

## Secrets handling
<Where secrets live, who has access, how to rotate. Never include values.>

## Feature flags
...
````

---

## 08-deployment.md

````markdown
# Deployment

## Environments and hosting
| Env | Host | URL | Deploy method |
|---|---|---|---|

## Build
<Commands, output folder, artifacts (APK/AAB, dist/, Docker image).>

## Deploy steps
1. <Pre-checks: tests, migrations reviewed, version bump.>
2. <Build.>
3. <Upload / push / release.>
4. <Post-deploy: migrate, cache clear, queue restart, smoke test.>

## Host-specific notes
<cPanel: document root, .htaccess, PHP version selector, cron.
Cloud Run: Dockerfile, env/secret mapping, region, min instances.
VPS / aaPanel: site config, reverse proxy, supervisor/pm2, SSL.
Play Store: signing, track.>

## CI/CD
<Pipelines, triggers, secrets they need.>

## Rollback
<How to return to the previous version.>

## Monitoring and backups
...
````

---

## 09-testing.md

````markdown
# Testing

| Type | Tool | Command | Location |
|---|---|---|---|
| Unit | | | |
| Integration | | | |
| E2E / UI | | | |

## What is covered / not covered
## Conventions (naming, fixtures, mocks)
## How to add a test (small example)
## Manual test checklist for critical flows
````

---

## 10-contributing.md

````markdown
# Contributing

## Branching and commits
<Strategy actually used (check git log): trunk, feature branches, conventional commits?>

## Code style
<Linters/formatters and their config files; naming conventions seen in code.>

## Pull request checklist
- [ ] builds and tests pass
- [ ] docs updated (see the sync table in docs/README.md)
- [ ] migrations / config changes noted

## Adding common things
- New endpoint / screen / model: <steps and files to touch>
````

---

## 11-troubleshooting.md

````markdown
# Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|

## FAQ
## Known limitations and tech debt
<Honest list of issues found while reading: TODO/FIXME clusters, duplicated logic, missing tests.>
````

---

## ADR (`adr/NNNN-title.md`)

````markdown
# ADR NNNN: <decision title>

- **Status:** accepted | superseded by ADR-XXXX
- **Date:** <date or "unknown (reconstructed from code)">

## Context
<Forces and constraints.>

## Decision
<What was chosen.>

## Consequences
<Benefits, costs, follow-ups.>

## Alternatives considered
<Only if known; otherwise omit.>
````

When reconstructing an ADR from code, say so in the Date or Context line so nobody mistakes inference for recorded history.

---

## CHANGELOG.md

Follow Keep a Changelog. Build entries from `git log` or release tags if available; otherwise start with the current state.

````markdown
# Changelog

## [Unreleased]
### Added
### Changed
### Fixed

## [1.0.0] - YYYY-MM-DD
````
