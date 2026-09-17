# Memory Leaks — Android Kotlin/Compose

Android memory leaks almost always follow one shape: **something long-lived holds a reference to something short-lived** (an `Activity`, `Fragment`, `View`, or `Composable`'s scope) past that short-lived thing's death. Look for these specific patterns.

## 1. Context leaks

- **Static/companion object holding an `Activity` or `View` context.**
  ```kotlin
  // BAD — leaks the Activity forever
  companion object {
      var activity: Activity? = null
  }
  ```
  Fix: use `applicationContext` when a long-lived reference to Context is genuinely needed, or don't hold it statically at all.

- **Singleton (`object`) storing a `Context` passed at init time without using `applicationContext`.**
- **`Context` captured in a lambda/listener that outlives the `Activity`** (e.g., passed into a singleton event bus, a static callback list, or a long-lived repository).

## 2. Listener / callback leaks

- Registered listeners (`addOnXListener`, `LocationListener`, `SensorEventListener`, `BroadcastReceiver`) that are **never unregistered** in the matching lifecycle callback (`onDestroy`, `onStop`, `onDetach`, `DisposableEffect`'s `onDispose`).
- Anonymous inner classes / lambdas registered as listeners implicitly hold `this` (the enclosing `Activity`/`Fragment`) — check every `register*`/`add*Listener` call has a corresponding `unregister*`/`remove*Listener`.

## 3. Coroutines & Jobs

- **`GlobalScope.launch { ... }`** inside an Activity/Fragment/ViewModel — this coroutine is never automatically cancelled and can hold references to the caller for its entire (possibly infinite) duration. Almost always a bug unless the work is genuinely meant to outlive the app UI (rare — e.g., a foreground sync explicitly designed for that).
- **`CoroutineScope` created manually but never cancelled** — e.g. `val scope = CoroutineScope(Dispatchers.IO)` stored as a class field with no `scope.cancel()` in `onDestroy`/`onCleared`.
- Correct patterns to check for and confirm are actually in place: `viewModelScope` (auto-cancelled in `onCleared`), `lifecycleScope` (auto-cancelled with the lifecycle), `rememberCoroutineScope()` in Compose (scoped to composition).
- A coroutine launched with `lifecycleScope.launch` that isn't tied to a specific `repeatOnLifecycle`/`launchWhenX` state can still run (and hold references) while the UI is stopped — check if that's intended.

## 4. Compose-specific leaks

- **`remember { }` capturing a `Context`/`Activity`/`NavController` that should instead be obtained via `LocalContext.current` fresh, or scoped correctly** — objects in `remember` survive recompositions and can outlive what they should.
- **`DisposableEffect` without a proper `onDispose { }` cleanup** — any listener/callback registered inside `DisposableEffect`'s body MUST be torn down in `onDispose`, or it leaks across recompositions/navigation.
  ```kotlin
  // BAD — no onDispose, listener accumulates
  DisposableEffect(Unit) {
      val listener = ...
      someManager.addListener(listener)
      onDispose { } // empty!
  }
  ```
- **`LaunchedEffect` doing long-running work keyed on a value that changes often**, relaunching without cancelling prior work cleanly (should self-cancel via structured concurrency, but verify no side-launched jobs escape it).
- Bitmap/Drawable/large object references held in `remember` without `remember(key)` invalidation, causing accumulation across recompositions or navigation back-stack retention.

## 5. View system (if project mixes XML Views with Compose, or is legacy)

- `Adapter`s holding a reference to the parent `Activity`/`Fragment` instead of `applicationContext` or a weak reference, especially in `RecyclerView.Adapter` constructors.
- `Handler` instances as **non-static inner classes** (implicitly hold outer `Activity`) combined with `postDelayed` — the delayed message keeps the `Activity` alive until it fires, even after the user navigates away. Check for `removeCallbacksAndMessages` in teardown.
- `ViewBinding`/`DataBinding` in a `Fragment` not nulled out in `onDestroyView` (`_binding = null`) — the `View` tree leaks until the `Fragment` itself is destroyed.

## 6. Image / resource leaks

- `Bitmap`s not recycled (pre-Compose/legacy code) or loaded at full resolution into memory unnecessarily (check for an image-loading library like Coil/Glide being bypassed with manual `BitmapFactory.decode*` calls without sizing options).
- Open `Cursor`, `InputStream`, `FileOutputStream`, or database connections not closed in a `finally`/`use { }` block.
- `MediaPlayer`/`ExoPlayer`/`Camera` instances not released in the matching lifecycle teardown.

## How to search

- Grep for: `GlobalScope`, `companion object` combined with `var.*Context|Activity|View`, `addListener` / `register`, `DisposableEffect`, `remember {`, `Handler(`, `postDelayed`, `BitmapFactory`, `MediaPlayer`, `ExoPlayer`.
- For every listener/scope/resource acquisition found, verify there's a matching teardown by checking the enclosing lifecycle method or `onDispose`/`finally`/`use`.
- Cross-check ViewModels: `grep` for stored `Context`, `View`, `Activity`, or `Fragment` types as class properties — a ViewModel should essentially never hold any of these directly.
