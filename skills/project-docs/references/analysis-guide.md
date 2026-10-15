# Codebase analysis guide

How to learn a project quickly and accurately before documenting it. Start with the general order, then jump to the section for the detected stack. Real projects often combine several (for example Laravel API + React admin + Android app + Firebase).

## Contents
- [General discovery order](#general-discovery-order)
- [Laravel / PHP](#laravel--php)
- [React / TypeScript / Vite / Next](#react--typescript--vite--next)
- [Node / Express](#node--express)
- [Android: Kotlin + Jetpack Compose](#android-kotlin--jetpack-compose)
- [Firebase](#firebase)
- [Python](#python)
- [Docker, CI and hosting](#docker-ci-and-hosting)
- [Reading git history](#reading-git-history)
- [Questions to ask the author](#questions-to-ask-the-author)

---

## General discovery order

1. **Manifest and scripts**: `package.json`, `composer.json`, `build.gradle(.kts)`, `requirements.txt`/`pyproject.toml`, `go.mod`. These give the stack, versions, and the real commands.
2. **Existing docs**: README, `docs/`, comments at the top of main files, wiki links. Treat them as claims to verify, not truth.
3. **Entry points**: where execution starts (`public/index.php`, `src/main.tsx`, `MainActivity.kt`, `server.js`, `functions/index.ts`).
4. **Routing / navigation**: the list of things the system can do (HTTP routes, screens, CLI commands, Cloud Functions, scheduled jobs).
5. **Data layer**: models/entities, migrations, security rules, repositories. This reveals the domain.
6. **One vertical slice**: pick the most important feature and read it top to bottom. Repeat for 3-6 features; those become the "how it works" flows.
7. **Cross-cutting code**: auth, middleware/interceptors, error handling, logging, config loading, encryption, localization.
8. **Build and deploy config**: Dockerfile, CI workflow, `.htaccess`, `firebase.json`, signing configs, env examples.
9. **Tests**: they show intended behavior and edge cases. Note what is and is not covered.
10. **Smells worth documenting**: `TODO`/`FIXME`/`HACK` comments, duplicated logic, very large files, unused dependencies, commented-out code, magic numbers, hard-coded URLs.

Rules while reading:
- Do not open or quote real `.env`, keystores, service-account JSON or credentials. Use `.env.example`. If you stumble on a secret, do not reproduce it; tell the user it should be rotated and kept out of the repo.
- Skip generated and vendored code (`vendor/`, `node_modules/`, `build/`, `dist/`, `.gradle/`, `storage/`, lockfiles except to read the package manager).
- When two files disagree (README vs code), the code wins; note the drift.

---

## Laravel / PHP

**Identify:** `composer.json` (`laravel/framework` version, PHP constraint), `artisan`, `bootstrap/app.php`.

**Read in this order**
- `routes/web.php`, `routes/api.php`, `routes/console.php` (and `php artisan route:list` if runnable): the surface area.
- `app/Http/Controllers/*`, `app/Http/Requests/*` (validation), `app/Http/Middleware/*`, `app/Policies/*` and `app/Providers/AuthServiceProvider.php` (authorization).
- `app/Models/*`: fillable/guarded, casts, relations, scopes, observers.
- `database/migrations/*`, `database/seeders/*`, `database/factories/*`: schema and demo data.
- `app/Services`, `app/Actions`, `app/Jobs`, `app/Events`, `app/Listeners`, `app/Console/Commands`, `app/Console/Kernel.php` or `routes/console.php` (scheduler).
- `config/*.php` and `.env.example`: configurable behavior; note custom config keys.
- `resources/views` (Blade) or `resources/js` (Inertia/Livewire/Vite assets); `vite.config.js`.
- `tests/Feature`, `tests/Unit`.

**Extract:** auth method (Sanctum, Passport, session, Fortify, Breeze), roles/permissions package (Spatie), queue driver, cache/session driver, file storage disk, mail driver, third-party SDKs, scheduler entries, API versioning and response shape (Resources).

**Document specially:** `php artisan` commands for setup (`key:generate`, `migrate --seed`, `storage:link`, `optimize`), queue worker and cron requirements, file permissions for `storage/` and `bootstrap/cache`.

---

## React / TypeScript / Vite / Next

**Identify:** `package.json` deps (`react`, `vite`, `next`, `typescript`), `vite.config.ts`, `next.config.js`, `tsconfig.json`.

**Read in this order**
- Entry: `src/main.tsx` / `src/index.tsx`, `App.tsx`, router definition (`react-router`, Next `app/` or `pages/` directory).
- Structure: `components/`, `pages|routes|screens/`, `hooks/`, `services|api/`, `store|context/`, `lib|utils/`, `types/`.
- State: Redux Toolkit, Zustand, Context, React Query/SWR; where server state vs UI state lives.
- API layer: base URL handling, interceptors, auth token storage, error handling.
- Auth: protected routes, token refresh, role checks.
- Forms and validation (react-hook-form, zod, yup).
- Styling: Tailwind config, CSS modules, component library (shadcn, MUI), theme/design tokens.
- Build: env prefix (`VITE_`, `NEXT_PUBLIC_`), aliases, code splitting, PWA/service worker.
- Heavy client logic (for example PDF/image processing, OCR, canvas): describe the pipeline and its limits.

**Extract:** route table (path → component → guard), global state shape, API endpoints consumed, env vars, build output folder and how it is served.

---

## Node / Express

**Read:** `server.js`/`app.ts`, route files, middleware order (order matters: CORS, body parsing, auth, error handler), controllers/services, DB client setup (Prisma, Sequelize, Mongoose, knex), job runners, process manager config (`ecosystem.config.js`).

**Extract:** endpoint list (method, path, middleware), validation, error response shape, DB schema (`schema.prisma`, migrations), env vars, ports, health check.

---

## Android: Kotlin + Jetpack Compose

**Identify:** `settings.gradle(.kts)`, `app/build.gradle(.kts)`, `gradle/libs.versions.toml`, `AndroidManifest.xml`.

**Read in this order**
- Gradle: `applicationId`, `minSdk`/`targetSdk`/`compileSdk`, build types and flavors, signing config *names* (never keystore passwords), dependencies (Compose BOM, Hilt/Koin, Room, Retrofit, Coil, Firebase, WorkManager, DataStore).
- Manifest: launcher activity, other activities/services/receivers, permissions, deep links, `Application` class.
- Entry and navigation: `MainActivity`, `NavHost`/navigation graph, route definitions.
- Architecture: MVVM/MVI layout; `ui/` (screens, components, theme), `viewmodel`, `domain`/`usecase`, `data/` (repository, local, remote, mappers), `di/`.
- State: `StateFlow`/`mutableStateOf`, UI state classes, one-time events.
- Local storage: Room entities/DAOs/migrations, DataStore, encrypted prefs.
- Remote: Retrofit interfaces, Firebase SDK calls, WebSocket/FCM handling.
- Background: WorkManager workers, foreground services, sync strategy and conflict handling.
- Design system: theme (colors, typography, shapes), reusable components, accessibility and child-friendly choices if present.
- Security: encryption helpers, key storage (Keystore), ProGuard/R8 rules, network security config.

**Extract:** screen map (route → composable → ViewModel), data flow per feature (UI → VM → repo → local/remote), offline and sync behavior, permissions and why, release build steps (AAB, signing, versionCode bump).

---

## Firebase

**Identify:** `firebase.json`, `.firebaserc`, `firestore.rules`, `firestore.indexes.json`, `database.rules.json`, `storage.rules`, `functions/`, `google-services.json` (do not print contents).

**Read**
- Security rules: they define the real access model. Summarize per collection/path who can read/write and under what conditions. Flag rules that are open (`if true`) or rely only on client data.
- Data structure: infer collections and fields from SDK calls (`collection("x")`, `doc(...)`, `ref("path")`), converters/data classes, and rules. Document paths with placeholders (`/classes/{classId}/messages/{messageId}`).
- Indexes: composite indexes and why they exist.
- Cloud Functions: trigger type (HTTPS, callable, Firestore/RTDB trigger, scheduled, Auth), runtime, region, inputs/outputs, secrets used.
- Auth: providers, custom claims, how roles are assigned.
- Realtime Database vs Firestore: when each is used and why (presence, chat, counters, offline).
- Hosting/rewrites in `firebase.json`; emulator config.

**Extract:** data model per collection, rule matrix, function list, auth flow, deployment commands (`firebase deploy --only functions,firestore:rules`), project IDs per environment (non-secret).

---

## Python

**Read:** `pyproject.toml`/`requirements.txt`, entry (`main.py`, `manage.py`, `app.py`), framework (Django: `settings.py`, `urls.py`, `models.py`, `views.py`; FastAPI: routers, Pydantic schemas, dependencies), migrations (Alembic/Django), workers (Celery), CLI (`argparse`/`typer`/`click`), tests (`pytest`).

---

## Docker, CI and hosting

- `Dockerfile`, `docker-compose.yml`: base image, build stages, exposed ports, volumes, services and their roles.
- `.github/workflows/*`, `.gitlab-ci.yml`: triggers, jobs, required secrets (names only), deploy targets.
- **cPanel / shared hosting:** look for `.htaccess`, `public_html` layout, document root pointing at `public/`, PHP version selection, cron entries, build-then-upload flow, file permission notes.
- **Google Cloud Run:** container port (`PORT`), Dockerfile, `cloudbuild.yaml`, service name and region, env vars and secret mappings, min/max instances.
- **VPS / aaPanel:** Nginx/Apache site config, reverse proxy, PHP-FPM version, supervisor/pm2/systemd units, SSL, firewall ports, cron, backup.
- **Android release:** signing, `bundleRelease`, Play Console track, versioning scheme.

---

## Reading git history

If `.git` is available: `git log --oneline | head -50`, `git shortlog -sn`, `git log --stat -5`, tags/releases. Use it to learn the commit convention, active areas, and to build the changelog. Use `git log -S "<term>"` or `git blame` only to answer a specific "why" question.

---

## Questions to ask the author

Ask only what the code cannot answer, all in one message, and limit to the few that unblock the docs:

- Who is the intended audience, and is there a deadline or handover?
- Which environments exist and where is production hosted?
- Are there business rules or domain terms that are not obvious from the code?
- Any known bugs, planned refactors or things the docs should warn about?
- Anything that must stay out of the docs (clients, credentials, internal URLs)?
