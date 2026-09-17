# General Bugs — Android Kotlin/Compose

Catch-all for logic errors, null-handling mistakes, lifecycle misuse, and state-management bugs that don't fall cleanly into leak/race/performance buckets.

## 1. Null-safety misuse

- **`!!` (non-null assertion) on values that can genuinely be null** at that point — especially on `Intent` extras, `savedInstanceState` values, nullable API/DB fields, or `findViewById` results. Each `!!` is a candidate crash site; check if the surrounding logic actually guarantees non-null or if it's a latent NPE.
- `lateinit var` accessed before initialization is possible on some code path (e.g., a property expected to be set in `onCreate` but read from a callback that can fire earlier, like a fragment's `onAttach`).
- Unsafe cast (`as Type` instead of `as? Type`) where the actual runtime type isn't guaranteed.

## 2. Lifecycle misuse

- Fragment/Activity code interacting with Views after `onDestroyView`/`onDestroy` (e.g., a network callback that completes late and touches a now-null/detached view without checking `isAdded`/lifecycle state or view-binding nullability).
- `onSaveInstanceState`/process-death not handled for state the user would expect to survive rotation or backgrounding (check for `rememberSaveable` vs plain `remember` in Compose where state should survive config changes; check for `ViewModel` usage vs. Activity-scoped fields for the same reason).
- Double-initialization bugs: logic in `onCreate`/`onResume`/`LaunchedEffect(Unit)` that assumes it runs exactly once, but Android lifecycle can call these multiple times (e.g., `onResume` on every foreground) — check for accidental duplicate listener registration, duplicate analytics events, or duplicate data loads.

## 3. State-management bugs (Compose/ViewModel)

- **Reading a stale closure value** — a lambda capturing a `val` from an outer scope that's since changed, instead of reading current state at call time. Common in Compose event handlers capturing a parameter from an earlier composition pass.
- UI state that can represent impossible/contradictory combinations because it's modeled as several independent booleans (`isLoading`, `isError`, `isSuccess` all mutable independently) instead of a sealed class/single source of truth — flag as a bug-prone pattern even if no concrete bug is observed yet, since these combinations tend to eventually produce an inconsistent UI.
- `LaunchedEffect`/`SideEffect` with an incorrect or missing key causing the effect to run with stale parameters, or to never re-run when it should.
- Off-by-one or boundary errors in pagination logic (loading next page), list index access, or date/time range calculations (especially timezone handling — mixing `LocalDateTime` without a zone and `Instant`/zoned equivalents is a common source of subtle bugs).

## 4. Exception handling gaps

- Empty or overly broad `catch (e: Exception) { }` blocks that swallow errors silently, especially around network/DB calls — makes real bugs invisible and hard to diagnose from user reports.
- Coroutine exceptions not surfaced: an unhandled exception in a `launch` block crashes the app unless caught, while in some structured-concurrency setups it can silently cancel a parent scope — check whether exception handling strategy is intentional (`CoroutineExceptionHandler`, `try/catch` at the right level, or `supervisorScope` where child failures shouldn't cancel siblings).
- Force-unwrapping or assuming success on `Result`/`Either`-style return types without handling the failure branch.

## 5. Configuration & resource bugs

- Hardcoded strings instead of `strings.xml` (breaks localization — flag if the project otherwise uses string resources consistently, indicating a slip rather than an intentional choice).
- Hardcoded dimensions instead of `dp`/`sp` resources, or dimensions not scaling with device density/font-size settings.
- Missing handling for configuration changes affecting layout logic beyond just rotation (e.g., multi-window/split-screen resizing, foldables) if the project targets those.

## How to search

- Grep for: `!!`, `lateinit var`, `as ` (hard cast), `catch (e: Exception)`, `catch (e: Throwable)`, hardcoded string literals inside composables/layout code, `LaunchedEffect(Unit)`.
- For every `!!`, trace backward to confirm whether non-null is actually guaranteed by preceding logic.
- For UI state classes, check whether independent boolean flags could combine into a state that makes no sense (e.g., `isLoading = true` and `isSuccess = true` simultaneously).
- For every `catch` block, check the body isn't empty and isn't swallowing an error the user would want surfaced (logged, retried, or shown in UI).
