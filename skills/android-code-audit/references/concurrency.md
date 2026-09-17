# Race Conditions & Concurrency — Android Kotlin/Coroutines

These bugs are the hardest to catch because they're often intermittent and non-reproducible in normal testing. Look for shape, not just symptoms.

## 1. Shared mutable state without synchronization

- Plain `var`/mutable collections (`MutableList`, `MutableMap`, `HashMap`) accessed from multiple coroutines/threads without a `Mutex`, `synchronized`, or a thread-confined dispatcher.
  ```kotlin
  // BAD — race if launched from multiple coroutines concurrently
  class Repository {
      private val cache = mutableMapOf<String, Data>()
      suspend fun get(id: String): Data {
          return cache[id] ?: fetch(id).also { cache[id] = it }
      }
  }
  ```
  Fix options: `Mutex().withLock { }`, confine mutation to a single dispatcher, or use a thread-safe structure (`ConcurrentHashMap` — still verify compound operations like check-then-act are atomic).

- **Check-then-act races**: `if (x == null) { x = ... }` or `if (!list.contains(y)) list.add(y)` across coroutines — the check and the act are not atomic even if each individual operation is "safe".

## 2. StateFlow / LiveData / Compose state races

- Multiple coroutines calling `.value = ` on the same `MutableStateFlow` without coordination, where the new value depends on the old value (`_state.value = _state.value.copy(...)`) — under concurrent access this can lose updates. Prefer `.update { it.copy(...) }` which is atomic, and flag any `.value = _state.value.copy(...)` pattern as a candidate race.
- `mutableStateOf` (Compose) mutated from a background thread/dispatcher instead of the main thread — Compose state is expected to be read/written consistent with snapshot semantics; writes from non-main threads without `Snapshot.withMutableSnapshot` or dispatching back to Main can cause subtle bugs or crashes.

## 3. Coroutine scope & structured concurrency violations

- **Unstructured `launch` inside `launch`** where the inner job isn't tied to the outer job's lifecycle intentionally (e.g., fire-and-forget work inside a `viewModelScope.launch` using a *different*, unscoped `CoroutineScope`) — breaks cancellation propagation.
- **Multiple concurrent writers to the same resource** (e.g., two `viewModelScope.launch` blocks both writing to the same Room table / same file without any ordering guarantee) — check if this is intentional or accidental.
- **`async` results never awaited**, or awaited in the wrong order, causing effectively-random completion order for operations the user assumes are sequential.
- Initialization races: a `ViewModel` firing multiple `init { viewModelScope.launch { ... } }` blocks that all mutate the same state, where the last one to finish wins non-deterministically instead of by design.

## 4. Main-thread / background-thread contract violations

- Room DAO calls not marked `suspend` or not run off the main thread (Room throws at runtime if this is violated on a blocking call — check for `allowMainThreadQueries()` which disables this safety net and should almost never be present in production code).
- Network calls (Retrofit without `suspend`, raw `HttpURLConnection`/`OkHttp` synchronous calls) invoked directly from a UI-triggered code path without a dispatcher switch.
- File I/O in `LaunchedEffect`/`viewModelScope.launch` without `withContext(Dispatchers.IO)`.

## 5. Double-execution / duplicate-trigger bugs

- Button click handlers or `LaunchedEffect(Unit)` blocks that can fire more than once (e.g., due to recomposition, or a button not being disabled after first tap) triggering the same network call/purchase/submission twice. Check for a debounce/disable-while-loading guard.
- `LaunchedEffect(key)` where `key` changes more often than intended (e.g., keyed on an object without stable `equals`, or on `Unit` when it should be keyed on a specific value), causing the effect to relaunch and overlap with a prior still-running instance.

## 6. Deadlock-shaped patterns

- Nested `Mutex.withLock` calls where the same mutex could be acquired twice from a call path that re-enters (Kotlin `Mutex` is **not** reentrant, unlike `synchronized` — this is a common mistake when migrating from Java).
- `runBlocking` called from a coroutine that's already inside a dispatcher tied to a limited-thread pool, causing thread starvation under load.

## How to search

- Grep for: `MutableStateFlow`, `.value =`, `mutableStateOf`, `GlobalScope`, `runBlocking`, `Mutex`, `synchronized`, `async {`, `launch {` nested inside another `launch {`, `allowMainThreadQueries`.
- For every mutable shared field (class-level `var` or mutable collection) in a class used across coroutines, check every read/write site — are they all on the same dispatcher, or protected by the same lock?
- For every `StateFlow`/`mutableStateOf` update, check if it reads-then-writes (`copy()` pattern) — flag non-atomic read-modify-write sequences under concurrent callers.
- Trace `init` blocks in ViewModels for multiple independent `launch` calls that touch the same state.
