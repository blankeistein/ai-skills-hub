---
name: compose-optimizer
description: Review and audit Jetpack Compose components and screens (Kotlin) for performance issues (unnecessary recomposition, unstable parameters, missing keys/remember), structural problems (reusability, single-responsibility, naming), and architecture issues (state hoisting, ViewModel usage, side-effect handling). Use this skill whenever the user shares Compose code (a @Composable function, a whole screen file, or a component) and asks to optimize, review, audit, refactor, check performance, or "clean up" it — even if they don't use the word "optimize" explicitly. Also trigger on phrases like "kenapa komponen ini lag", "kenapa recompose terus", "compose best practice", or when the user pastes a .kt file with @Composable and asks for feedback.
---

# Compose Optimizer

A skill for reviewing Jetpack Compose code (components and full screens) and producing a structured, prioritized optimization report — covering performance, code structure, and architecture.

## When to use this skill

Trigger whenever the user:
- Shares Compose code (a `@Composable` function, a screen, a reusable component) and asks for review, audit, optimization, refactor suggestions, or "kenapa ini lambat/lag/recompose terus"
- Asks general Compose best-practice questions in the context of their own code
- Asks to check for unnecessary recomposition, unstable classes, missing `remember`/`key`, or misuse of `LaunchedEffect`/`DisposableEffect`/`derivedStateOf`
- Asks whether their state hoisting / ViewModel usage / screen structure follows good practice

Do NOT use this skill for:
- Writing brand-new Compose UI from scratch with no existing code to review (that's just normal coding help)
- Non-Compose Kotlin/Android code (plain XML views, non-UI logic) unless Compose is involved

## Workflow

1. **Get the code.** If the user references a file but hasn't pasted it, read it (`view` or the file-reading skill if needed). If they pasted a snippet, work with that directly — don't ask them to re-paste.
2. **Skim first, then go deep per category.** Read the whole file/component once to understand its role (is it a leaf component, a screen, a shared reusable piece?) before flagging issues — this avoids suggesting fixes that ignore the component's actual purpose.
3. **Check against the three categories below** (`references/performance.md`, `references/structure.md`, `references/architecture.md`). Load only the reference file(s) relevant to what you find — you don't need all three for every review if the code is simple.
4. **Produce the report** using the format in "Output format" below.
5. **Offer to apply fixes.** After the review, ask if the user wants you to actually apply the suggested changes to the file(s), rather than doing it unprompted — reviews and edits are different asks.

## Output format

Structure the review as:

1. **Ringkasan singkat** (2-3 kalimat): apa fungsi komponen/screen ini, dan kondisi umumnya (sudah cukup baik / ada beberapa isu / perlu perhatian serius).
2. **Temuan per kategori**, hanya kategori yang relevan:
   - **Performance** — masalah + kenapa ini masalah + fix konkret (potongan kode)
   - **Struktur & Reusability** — masalah + fix konkret
   - **Arsitektur** — masalah + fix konkret
3. Setiap temuan diberi label prioritas: 🔴 **High** (nyata memengaruhi performa/kebenaran), 🟡 **Medium** (best practice, akan jadi masalah saat scale), 🟢 **Low** (nice-to-have / gaya kode).
4. Tutup dengan pertanyaan singkat: apakah user mau langsung diterapkan perbaikannya.

Jangan tulis ulang seluruh file kode di laporan kecuali untuk potongan kecil yang menunjukkan before/after suatu fix. Jangan membanjiri user dengan isu kosmetik kalau ada isu performa/arsitektur yang lebih penting — urutkan dari yang paling berdampak.

## Quick reference — common issues to scan for

**Performance**
- Lambda/object literals created inline in composable calls without `remember` (new instance every recomposition)
- Passing unstable types (plain `List`, `Map`, mutable classes without `@Stable`/`@Immutable`) as parameters to composables that should skip recomposition
- Reading a frequently-changing state (e.g. scroll position) directly in a composable that has a large recomposition scope, instead of narrowing scope or using `derivedStateOf`
- Missing or wrong `key` in `LazyColumn`/`LazyRow` items
- Heavy work (formatting, filtering, sorting) done inline in the composable body instead of `remember(keys) { }` or hoisted to ViewModel
- `Modifier` chains built with unstable inputs on every recomposition
- Overuse of `mutableStateOf` at high scope causing whole-tree recomposition instead of narrowing state down to leaf composables

**Structure & Reusability**
- Composables that mix UI with business logic / data fetching directly
- Components not parameterized (hardcoded strings, colors, dimensions) that could be reused
- Very large composable functions doing too much (screen-level function with no decomposition into smaller pieces)
- Missing `Modifier` parameter (with default `Modifier`) on reusable components, breaking composability
- Preview functions missing or not covering key states (empty, loading, error, filled)

**Architecture**
- State not hoisted — component owns state it shouldn't (e.g. screen-level state living inside a leaf component)
- ViewModel doing UI-only work, or UI directly manipulating data-layer objects
- Side effects (`LaunchedEffect`, `DisposableEffect`, `SideEffect`) misused — wrong keys causing repeated/missed execution, or side effects that should be plain state instead
- No single source of truth for UI state (state duplicated between ViewModel and local `remember`)
- Navigation logic embedded inside composables instead of hoisted to caller/navigation layer

For deeper detail and code examples on any of these, read the matching file in `references/`.
