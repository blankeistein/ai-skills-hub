---
name: android-code-audit
description: Systematic audit of Android Kotlin/Jetpack Compose projects for bugs, memory leaks, race conditions/concurrency bugs, performance regressions, security issues, architecture violations, and accessibility gaps. Use this whenever the user asks to review, audit, debug, find issues in, or check the quality/performance/security of an Android project, module, or Kotlin file — including vague requests like "kenapa app ini lag", "cek kodenya", "ada bug gak", "kok crash", "kenapa lemot", or "review before release". Also use proactively when opening an Android codebase for any nontrivial task, since issues found early save rework. Covers Kotlin, Jetpack Compose, Coroutines/Flow, ViewModel/LiveData, Room, and standard Android lifecycle components. This skill is intentionally AI-tool-agnostic — written to be followed by any coding assistant with file-read access to the project (not just Claude).
---

# Android Code Audit

A systematic method for auditing an Android Kotlin/Compose codebase across six categories: **bugs, memory leaks, concurrency (race conditions), performance, security, and architecture/accessibility**. Report-first: identify and explain issues, do NOT modify code unless the user explicitly asks for fixes to be applied.

## Ground rules

1. **Report, don't auto-fix.** Default behavior is find + explain + suggest. Only edit files if the user explicitly says to apply/implement the fix.
2. **Cite exact locations.** Every finding needs `file path : line number(s)` (or function/composable name if line numbers aren't available). A finding without a location is not actionable — dig until you have one.
3. **Explain root cause, not just symptom.** "This leaks memory" is not enough — explain *why* (e.g., "the Job outlives the Fragment because it's not cancelled in onDestroyView").
4. **Severity every finding.** Use the scale below so the user can triage.
5. **No hallucinated APIs.** If unsure whether something is actually a bug (vs. intentional), say so — flag as "worth confirming" rather than asserting.
6. **Scale effort to project size.** For a single file/snippet, do a direct read-through. For a full project, follow the triage workflow below so you don't miss modules or drown in low-value output.

## Severity scale

| Severity | Meaning |
|---|---|
| **Critical** | Crashes, ANRs, data loss/corruption, security exposure (secrets, injection, insecure storage of sensitive data) |
| **High** | Memory leak, race condition with real user-facing impact, severe jank (dropped frames, main-thread blocking) |
| **Medium** | Performance inefficiency, architecture violation that will cause pain at scale, accessibility blocker |
| **Low** | Style/best-practice deviation, minor inefficiency, small accessibility gap |

## Workflow

### Step 1 — Scope the audit
Determine what's being reviewed:
- **Single file/snippet pasted in chat** → read it directly, skip to Step 3 for the relevant category(ies).
- **Full project opened/attached** → do Step 2 first (triage) before deep-diving.

If the user's request is vague ("cek kodenya", "ada bug gak"), don't ask too many clarifying questions — default to auditing all six categories at project scope, then let the report's structure allow the user to say "focus on X" for a follow-up pass.

### Step 2 — Triage a full project (skip if reviewing a single file)
Before deep-reading every file, build a map so effort goes where risk is highest:

1. List the module/package structure (`app/src/main/java/...`).
2. Identify high-risk zones first — these are where bugs/leaks/races concentrate:
   - Anything touching `Activity`/`Fragment` lifecycle + background work (coroutines, listeners, callbacks)
   - `ViewModel`s holding references to `Context`, `View`, or `Activity`
   - Any class implementing `Runnable`, `Handler`, `BroadcastReceiver`, `Service`
   - Singleton objects (`object` declarations) that hold or accumulate state
   - Places using `GlobalScope`, raw `Thread`, `AsyncTask` (legacy), or unscoped coroutine launches
   - Network/DB layer (Retrofit, Room) — check for main-thread violations and unhandled exceptions
   - Anywhere secrets/keys/tokens might be hardcoded (`local.properties` leakage into code, API keys in strings.xml, etc.)
3. Skim `build.gradle`(`.kts`) for red flags: outdated dependencies with known issues, `minifyEnabled false` in release, missing ProGuard/R8 rules for a shipped app.
4. From this map, prioritize deep-reads in this order: high-risk zones → frequently-modified/core files → everything else time permits.

### Step 3 — Category-specific deep read
Load the reference file(s) relevant to the audit scope. Each reference has concrete patterns to grep/read for, with good vs. bad Kotlin/Compose examples.

| Category | Reference file | Load when |
|---|---|---|
| Bugs (general logic errors, null handling, state bugs) | `references/bugs.md` | Always for a general audit |
| Memory leaks | `references/memory-leaks.md` | Always for a general audit, or when user mentions leaks/OOM |
| Race conditions & concurrency | `references/concurrency.md` | Always for a general audit, or when user mentions crashes that are intermittent/hard to repro, coroutines, threading |
| Performance | `references/performance.md` | Always for a general audit, or when user mentions "lag", "lemot", "jank", "slow", dropped frames |
| Security | `references/security.md` | Always for a general audit, or when user mentions secrets, auth, storage, "before release" |
| Architecture & accessibility | `references/architecture-accessibility.md` | Always for a general audit, or when user mentions structure, testability, MVVM, a11y |

For a targeted request ("cek race condition di sini aja"), load only the matching reference(s) — don't load all six.

### Step 4 — Compile the report
Use the format in "Report format" below. Group findings by severity (Critical first), not by category — severity is what the user needs to triage on.

**Output medium:**
- Small number of findings (roughly ≤10) → report directly in the chat/conversation.
- Large number of findings, or a full-project audit → write a Markdown report file (see naming below), and summarize the top 3–5 Critical/High findings inline so the user isn't stuck opening a file to know if anything urgent exists.

### Step 5 — Offer next steps
End by asking whether the user wants:
- A deeper pass on any specific category or module
- Fixes drafted (as diffs) for specific findings — only after explicit confirmation, per Ground rule 1

## Report format

For each finding:

```
### [SEVERITY] Short title of the issue
**Location:** path/to/File.kt:42-58 (or composable/function name)
**Category:** Memory Leak | Race Condition | Performance | Bug | Security | Architecture | Accessibility

**What's happening:**
Root cause explanation — why this occurs, not just what.

**Impact:**
Concrete consequence (e.g., "Fragment instance leaks after every rotation,
compounding ~2MB per leak in a screen with a RecyclerView of images").

**Suggested fix:**
Specific, concrete suggestion (code sketch is fine) — but do not apply it
unless asked.
```

If writing a report file, open with a short summary table (severity counts, files touched) before the detailed findings.

## Notes for AI assistants using this skill

This skill is written to be followed by any coding assistant with file-read access to a project — it doesn't assume Claude-specific tools. To use it:
- Read files directly from the project's filesystem/working directory.
- Use whatever code-search capability you have (grep, semantic search, or manual traversal) to locate the patterns described in each reference file.
- If your environment lacks file-write access, always default to reporting in the conversation rather than attempting to write a report file.
