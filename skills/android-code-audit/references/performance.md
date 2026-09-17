# Performance — Android Kotlin/Compose

Focus on things that cause dropped frames (jank), slow startup, or wasted work. Prioritize main-thread work and unnecessary recomposition — these are the two biggest sources of perceived "lag" in Compose apps.

## 1. Unnecessary/excessive recomposition (Compose)

- **Unstable parameters** passed to a Composable causing it to recompose every time its parent does, even when nothing relevant changed. Common culprits: passing a `lambda` that's re-created every recomposition (not `remember`-wrapped) instead of a stable reference; passing a `List`/`Map` (unstable by default unless `@Immutable`/`kotlinx.collections.immutable`) instead of an immutable collection.
  ```kotlin
  // BAD — lambda re-created every recomposition, defeats skipping
  MyButton(onClick = { viewModel.doThing() })
  // BETTER, if doThing has no captured changing state:
  val onClick = remember { { viewModel.doThing() } }
  ```
- **Reading state too high in the tree** — a `Composable` reading a frequently-changing state (e.g., scroll position, a per-frame animation value) recomposes itself *and everything below it* unless the read is scoped down (e.g., via a lambda passed to `Modifier.offset { }` instead of reading the value directly in the composable body).
- Missing `key()` in `LazyColumn`/`LazyRow` items — without stable keys, item recomposition/animation identity breaks on list changes, causing more recomposition than necessary and glitchy animations.
- Heavy computation (formatting, filtering, sorting) done directly in composable body on every recomposition instead of wrapped in `remember(keys) { }` or `derivedStateOf { }`.
- Overuse of `derivedStateOf` where a simple `remember(key)` would do, or *underuse* where a value is read very frequently (e.g., scroll-derived booleans) and should be derived to avoid recomposing on every pixel of scroll.

## 2. Main-thread blocking

- Any synchronous I/O (file read/write, `SharedPreferences.commit()` instead of `apply()`, synchronous network calls, JSON parsing of large payloads) on the main thread — even if it "works", it risks ANRs under load or on slower devices.
- Heavy computation in `onCreate`/`onCreateView`/composable init path before first frame — slows app startup (cold start). Check for database migrations, large JSON parsing, or reflection-heavy DI setup happening synchronously at startup instead of lazily/async.
- `Bitmap` decoding/scaling on the main thread instead of via an image-loading library's background pipeline (Coil/Glide) or explicit `Dispatchers.Default`/`IO`.

## 3. List & lazy-layout issues

- `LazyColumn`/`LazyRow` items with non-trivial per-item cost (e.g., image decoding, date formatting) not memoized — recalculated every time the item recomposes/scrolls into view.
- Nesting scrollable containers of the same orientation (e.g., `LazyColumn` inside a `Column` inside a `verticalScroll` `Modifier`) — causes measurement/layout inefficiency and can break scrolling correctness.
- Using `Column` + `forEach` to render a long list instead of `LazyColumn` — every item is composed and measured eagerly regardless of visibility, wasting work for long lists.

## 4. Allocation & object-creation hotspots

- Object allocation inside hot paths — a composable body, a scroll listener, `onDraw`, or a tight loop — that could be hoisted out (allocated once, reused) instead of recreated every call/frame.
- Repeated `Regex` compilation inside a function called frequently, instead of compiling once as a top-level/companion `val`.
- Boxing/unboxing costs from using generic collections of primitives in hot paths (less critical, but worth flagging in genuinely hot loops).

## 5. Database & network inefficiency

- **N+1 query patterns**: fetching a list, then looping to fetch related data per item individually instead of a single joined/batched query (Room `@Relation`, or a batched network call).
- Missing indices on Room `@Entity` columns used frequently in `WHERE`/`ORDER BY` clauses (check `@Entity(indices = [...])`).
- Fetching more data than the UI displays (e.g., loading full objects when only a few fields are shown — consider a projection/DTO).
- No caching layer for data that doesn't change often, causing redundant network calls on every screen visit.
- Images loaded at full resolution when displayed at a much smaller size — check image-loading calls specify target size/`Modifier.size` matched to an appropriately sized request.

## 6. APK size / startup (flag only if relevant to what's being reviewed)

- Missing R8/ProGuard minification for release builds (`isMinifyEnabled = true` should be set for `release` buildType).
- Unused large dependencies included in the main app module instead of behind dynamic feature modules, if the project is large enough for this to matter.

## How to search

- Grep for: `remember {`, `derivedStateOf`, `LazyColumn`, `LazyRow`, composables receiving `List<` or `Map<` or lambda parameters directly, `SharedPreferences`, `.commit()`, `Regex(`, `@Entity`, `@Relation`.
- For every `LazyColumn`/`LazyRow`, check: is `key = { }` specified per item? Is per-item work memoized?
- For every composable taking a lambda parameter, check whether the caller wraps it in `remember` or whether it's a fresh lambda literal each recomposition — the latter isn't always a smoking gun (Compose can auto-hoist in many compiler versions) but is worth flagging if the composable is expensive to skip incorrectly.
- Grep call sites of DB/network functions for loops that call a suspend/fetch function per-iteration (N+1 pattern).
