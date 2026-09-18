---
name: android-testing-setup
description: Set up, write, and review tests for Android/Kotlin projects — unit tests (ViewModel, Repository, UseCase, plain Kotlin classes) and UI tests (Jetpack Compose testing API). Covers initial project setup (Gradle dependencies, folder structure, base test classes, fakes/test doubles), generating new tests for existing code, and reviewing existing tests for gaps or anti-patterns. Use this skill whenever the user asks to add tests, write unit tests, set up testing, test a ViewModel/Repository/Composable, review test coverage, or mentions JUnit/MockK/Turbine/Compose UI testing in an Android/Kotlin context. Also trigger on "belum ada test sama sekali, bantu setup" or "gimana cara test ViewModel ini".
---

# Android Testing Setup

A skill for setting up, writing, and reviewing tests in Android/Kotlin projects — covering both unit tests and Compose UI tests.

## Recommended stack (default recommendation)

Unless the project already uses something else, recommend and use:

| Purpose | Library |
|---|---|
| Test runner / assertions | JUnit4 (`junit:junit`) |
| Mocking | MockK (`io.mockk:mockk`) — Kotlin-first, handles `object`/`final` classes without extra config |
| Coroutines testing | `kotlinx-coroutines-test` (`runTest`, `TestDispatcher`) |
| Flow testing | Turbine (`app.cash.turbine:turbine`) |
| Assertions (optional, nicer syntax) | Google Truth (`com.google.truth:truth`) or plain JUnit `assertEquals`/`assertThat` — don't force Truth if the project already uses plain JUnit assertions |
| Compose UI testing | `androidx.compose.ui:ui-test-junit4` + `androidx.compose.ui:ui-test-manifest` (debug only) |
| Instrumented test runner (for UI tests) | AndroidX Test (`androidx.test.ext:junit`, `androidx.test:runner`) |

Always check the project's existing `build.gradle`/`libs.versions.toml` first — if it already has JUnit5, Kotest, or Robolectric set up, work with what's there instead of pushing the default stack.

## Workflow

1. **Figure out what's being asked**: setup from scratch, write tests for specific existing code, or review existing tests. If ambiguous and code is attached with no clear ask, default to asking briefly which of the three, unless context makes it obvious (e.g. "test file ini kok gagal" = review/fix, not setup).
2. **Check current state** before assuming: read `build.gradle`(`.kts`)/`libs.versions.toml` for existing test dependencies, and look for an existing `src/test/` or `src/androidTest/` folder structure. Don't propose a stack that conflicts with what's already there.
3. **Setup** (`references/setup.md`): add Gradle dependencies, ensure `testImplementation`/`androidTestImplementation`/`debugImplementation` are correctly split, set up base test classes (e.g. a `MainDispatcherRule` for coroutines) if missing.
4. **Unit tests** (`references/unit-testing.md`): for ViewModel/Repository/UseCase — structure test using Given-When-Then / AAA (Arrange-Act-Assert), fake or mock dependencies, test StateFlow/Flow emissions with Turbine, cover success/error/loading states and edge cases.
5. **UI tests** (`references/ui-testing.md`): for Composables — use `createComposeRule()`, semantics-based finders (`onNodeWithText`, `onNodeWithTag`), avoid testing implementation details, test user-visible behavior and state transitions.
6. **Review mode**: when reviewing existing tests, check against the anti-patterns list in each reference file (over-mocking, testing implementation instead of behavior, missing edge cases, flaky async handling) and report findings the same way the `compose-optimizer` skill does — grouped, prioritized, with concrete fixes — rather than rewriting everything unprompted.

## Output expectations

- When **writing new tests**, create/edit actual test files in the project's existing test source set (`src/test/java/...` for unit tests, `src/androidTest/java/...` for UI/instrumented tests) — don't just show snippets unless the user only asked for an example.
- When **reviewing**, give a short structured report (what's covered, what's missing, anti-patterns found) before touching any files, then ask before applying fixes — same review-then-ask pattern as the `compose-optimizer` skill.
- Test names should describe behavior, in backticks-with-spaces style if the codebase already uses it (e.g. `` fun `emits error state when repository throws`() ``), otherwise camelCase — match whatever convention already exists in the project's test files.
- Don't chase 100% coverage as a goal by itself — prioritize tests for business logic, state transitions, and error handling over trivial getters/pure UI layout.

## Quick reference — what to test where

**ViewModel** — state exposed via `StateFlow`/`State` in response to actions; loading/success/error states; that it calls the right repository/use-case methods; debouncing/throttling logic if present.

**Repository** — correct mapping between data sources (remote/local) and domain models; offline-first fallback behavior (e.g. Room-first, Firestore sync) if applicable; error propagation.

**UseCase / domain logic** — pure business rules, edge cases, input validation.

**Composable (UI test)** — does the right content render for a given state; does user interaction (click, type, scroll) trigger the right callback; conditional visibility (loading spinner, error message, empty state) shows/hides correctly. Do NOT unit-test Composables for internal recomposition count or implementation detail — that's what `compose-optimizer`'s performance review is for, not correctness testing.

For setup steps, unit test patterns, or UI test patterns in depth, read the matching file in `references/`.
