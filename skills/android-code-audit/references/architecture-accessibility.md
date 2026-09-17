# Architecture & Accessibility — Android Kotlin/Compose

Two lighter-weight categories, combined into one reference since they're usually reviewed together and are typically Medium/Low severity (unless an architecture violation causes an active bug — in which case also cross-reference the relevant category above).

## Architecture

Evaluate against MVVM / Clean Architecture conventions — the common Android standard — but calibrate to what the project already seems to be doing. Don't demand a full Clean Architecture rewrite of a small app; flag violations of whatever pattern the codebase has evidently chosen.

### 1. Layer violations
- **UI layer (Composable/Activity/Fragment) directly calling network or database code**, bypassing ViewModel/Repository — couples UI to data source implementation and makes testing hard.
- **ViewModel directly instantiating `Retrofit`/`Room` database instances** instead of receiving a `Repository`/data-source dependency (via constructor injection or a DI framework) — makes the ViewModel untestable without a real network/DB.
- **Business logic embedded in Composables** (calculations, validation rules, data transformation) instead of in a ViewModel or domain/use-case layer — hard to unit test, and tends to get duplicated across screens.
- **Domain models leaking framework types** — e.g., a domain/use-case layer returning Room `@Entity` classes or Retrofit response DTOs directly to the UI instead of mapping to a clean domain model — couples UI to a specific data source's shape.

### 2. Dependency direction
- Lower layers (data/domain) depending on upper layers (UI) — e.g., a Repository importing something from a `ui` package. Dependencies should point inward/downward (UI → domain → data), never the reverse.
- Circular dependencies between modules/packages.

### 3. Testability smells
- Classes that can't be unit tested without mocking Android framework classes (`Context`, `Activity`) because framework types are threaded too deep into business logic instead of being abstracted behind an interface.
- Singletons (`object`) used for stateful services (not just stateless utilities) — makes swapping implementations for tests hard, and can cause cross-test state leakage if tests run in the same process.
- Missing or inconsistent dependency injection — mixing manual `Service Locator`-style singletons with a DI framework (Hilt/Koin) inconsistently across the codebase.

### 4. Composable structure
- **Stateful and stateless concerns mixed in one Composable** — a single large Composable owning `remember`/business state *and* rendering UI, instead of separating a stateful "screen" composable from a stateless, preview-friendly, reusable UI composable. Flag large (100+ line) composables doing both as worth splitting.
- Missing `@Preview` composables for reusable UI components, making visual review/regression harder (Low severity, note only if the project otherwise uses previews consistently).

## Accessibility (a11y)

### 1. Missing content descriptions
- `Image`/`Icon` composables (or `ImageView`) conveying meaningful information with no `contentDescription`, or worse, a non-null placeholder description that doesn't describe the actual content.
- Purely decorative images that *should* have `contentDescription = null` explicitly (to be skipped by screen readers) but don't — forces TalkBack to announce meaningless content.

### 2. Touch target sizing
- Interactive elements (buttons, icons, checkboxes) sized below the ~48dp minimum recommended touch target, especially icon-only buttons using a tightly-cropped `Icon` with no padding/minimum-size modifier.

### 3. Text & contrast
- Text color/background combinations with insufficient contrast (flag visually if evident from the code — exact values a Composable declares — but note that a full contrast audit needs a design/visual tool, not just code reading).
- Font sizes hardcoded in a way that doesn't respect the user's system font-scale setting (using raw `dp` for text size instead of `sp`, or a `Modifier` that disables scaling).

### 4. Focus & navigation order
- Custom focus order (`Modifier.focusOrder`/`nextFocus*`) that doesn't match visual reading order, or interactive elements not reachable via keyboard/switch-access navigation at all.
- Custom composables that reimplement a standard interactive component (e.g., a `Box` with `clickable` acting as a button) without semantics (`Modifier.semantics { role = Role.Button }`) — screen readers won't announce it correctly as an interactive element.

### 5. Dynamic content announcements
- State changes that should be announced to screen reader users (e.g., form validation errors appearing, loading states completing) with no `LiveRegion`/semantics support, leaving screen-reader users unaware anything changed.

## How to search

- Grep for: `Retrofit.Builder`, `Room.databaseBuilder` inside ViewModel or Composable files (should live in a DI module/data layer only), `contentDescription`, `contentDescription = null` vs. missing entirely, `Modifier.clickable` without an adjacent `semantics` block, raw `sp`/`dp` usage on text.
- For architecture: trace a few representative features end-to-end (UI → ViewModel → Repository → data source) and check the layering is consistent; sample rather than exhaustively check every feature if the project is large.
- For accessibility: sample the most user-facing/primary screens first (onboarding, main navigation, core flows) rather than exhaustively auditing every screen.
