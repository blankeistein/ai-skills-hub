# Catatan per stack

Gunakan sebagai **daftar periksa pertanyaan dan kandidat isi**, bukan fakta final: selalu verifikasi dengan file repo (versi, nama script, struktur). Baca hanya bagian stack yang terdeteksi.

Daftar isi: [Laravel/PHP](#laravelphp) · [React + TypeScript + Vite](#react--typescript--vite) · [Next.js](#nextjs) · [Kotlin + Jetpack Compose](#kotlin--jetpack-compose-android) · [Firebase](#firebase) · [Node/Express](#nodeexpress) · [Python](#python-djangofastapiflask) · [Go](#go) · [Flutter](#flutter) · [Monorepo & tooling](#monorepo--tooling) · [Hosting](#hosting-dan-deployment)

## Laravel/PHP

**Deteksi**: `composer.json`, `artisan`, `app/`, `routes/`.
**Perintah umum** (verifikasi di composer.json "scripts"):
```bash
composer install && cp .env.example .env && php artisan key:generate
php artisan serve            # dev server
php artisan migrate          # jangan migrate:fresh di luar lokal
php artisan test             # atau ./vendor/bin/pest, ./vendor/bin/phpunit
./vendor/bin/pint            # format (jika ada)
./vendor/bin/phpstan analyse # atau larastan
npm run dev / build          # Vite untuk aset
```
**Tanyakan/catat**: versi Laravel & PHP; Blade/Livewire/Inertia/API-only; pola layer (Service/Action/Repository); Form Request; Policy/Gate; queue driver & worker; scheduler (cron); storage disk; cache driver; paket auth (Sanctum/Breeze/Jetstream/Fortify); multi-tenancy; lokalisasi `lang/`.
**Jebakan umum**: edit `.env` tidak berpengaruh bila config di-cache (`php artisan config:clear`); mass assignment (`$fillable`/`$guarded`); N+1 (`with()`); migrasi pada tabel besar; timezone `config/app.php`; `storage:link`; izin folder `storage/` & `bootstrap/cache` di hosting; jangan commit `vendor/` kecuali deploy shared hosting mewajibkannya (catat jika begitu).

## React + TypeScript + Vite

**Deteksi**: `package.json` (react, vite), `tsconfig.json`, `vite.config.*`.
**Perintah**: `npm run dev|build|preview|lint|test|typecheck` (cek `scripts`; bisa pnpm/yarn/bun: lihat lockfile).
**Catat**: strictness TS; router (React Router/TanStack Router); server state (TanStack Query/SWR) vs state klien (Context/Zustand/Redux); styling (Tailwind/CSS Modules/styled); library komponen (shadcn/MUI/Ant); form (React Hook Form + Zod); alias import (`@/`); struktur (feature-based vs layer-based); env var prefix `VITE_` (terekspos ke klien!); test (Vitest + Testing Library); i18n.
**Jebakan**: variabel `VITE_*` tampil di bundle (jangan simpan secret); import alias harus sinkron di `tsconfig` dan `vite.config`; efek ganda StrictMode di dev; kunci `key` pada list; pemanggilan API langsung di komponen vs lapisan data; kunci API pihak ketiga (mis. Gemini) tidak boleh ada di klien produksi tanpa proxy.

## Next.js

**Catat**: App Router vs Pages Router; Server vs Client Components (`"use client"`); data fetching & caching/revalidate; Route Handlers/Server Actions; middleware; runtime (edge vs node); env (`NEXT_PUBLIC_`); gambar (`next/image`), font; deployment (Vercel/Docker/standalone).
**Jebakan**: caching default berubah antar versi; hydration mismatch; akses `window` di server; secret di komponen klien.

## Kotlin + Jetpack Compose (Android)

**Deteksi**: `build.gradle(.kts)`, `settings.gradle`, `app/src/main`, `libs.versions.toml`.
**Perintah** (verifikasi nama modul/variant):
```bash
./gradlew assembleDebug
./gradlew :app:testDebugUnitTest
./gradlew :app:connectedDebugAndroidTest   # perlu emulator/perangkat
./gradlew lint ktlintCheck detekt          # bila dikonfigurasi
./gradlew :app:dependencies                # debug dependency
```
**Catat**: minSdk/targetSdk/compileSdk; versi Kotlin/AGP/Compose BOM; arsitektur (MVVM/MVI, Clean, UDF) & di mana ViewModel/UseCase/Repository tinggal; DI (Hilt/Koin); navigasi (Navigation Compose, type-safe routes); persistensi (Room/DataStore); jaringan (Retrofit/Ktor); coroutine/Flow (dispatcher, scope, `stateIn`); state di UI (`StateFlow` + `collectAsStateWithLifecycle`); tema (Material 3, `MaterialTheme`); modularisasi; build variant & signing (jangan commit keystore); ProGuard/R8; Firebase `google-services.json`.
**Jebakan**: `remember` vs `rememberSaveable`; recomposition tak perlu (stabilitas parameter, `key`); kebocoran konteks; operasi berat di main thread; `LazyColumn` tanpa `key`; string hardcode (pakai `strings.xml` untuk i18n); izin runtime & perubahan perilaku per API level; perangkat Android murah (RAM kecil) untuk target pengguna anak; enkripsi data lokal (Keystore) bila menyimpan data sensitif; versi Compose BOM yang tidak cocok dengan Kotlin compiler.

## Firebase

**Deteksi**: `firebase.json`, `.firebaserc`, `firestore.rules`, `functions/`.
**Perintah**:
```bash
firebase emulators:start         # Auth, Firestore, Functions, Storage
firebase deploy --only functions # jangan deploy ke prod tanpa instruksi eksplisit
firebase deploy --only firestore:rules
```
**Catat**: layanan yang dipakai (Auth, Firestore, Realtime Database, Storage, Functions, Hosting, FCM, App Check); proyek per lingkungan (`.firebaserc` aliases); struktur koleksi & model data; aturan keamanan & cara mengujinya; indeks komposit (`firestore.indexes.json`); runtime & region Functions; trigger (onCreate/HTTP/scheduled); pola sinkronisasi/offline; batas biaya (baca/tulis, listener).
**Jebakan**: aturan keamanan terlalu longgar (`allow read, write: if true`); listener realtime tak dilepas -> biaya & kebocoran; denormalisasi tanpa strategi pembaruan; batas 1 tulis/dtk per dokumen; transaksi vs batch; `serverTimestamp()` vs waktu klien; cold start Functions; kunci Admin SDK di repo; Firestore vs Realtime Database dicampur tanpa aturan jelas (tulis kapan memakai yang mana).

## Node/Express

**Catat**: ESM vs CJS; struktur (routes/controllers/services); validasi (Zod/Joi); ORM (Prisma/Drizzle/Sequelize/Knex) + perintah migrasi; auth (JWT/session) & middleware; penanganan error terpusat; logging; env & config; test (Jest/Vitest + Supertest); proses (pm2/Docker).
**Jebakan**: error async tak tertangkap; urutan middleware; CORS; rate limit; graceful shutdown.

## Python (Django/FastAPI/Flask)

**Perintah**: `python -m venv .venv && source .venv/bin/activate`, `pip install -r requirements.txt` / `uv sync` / `poetry install`; `pytest`; `ruff check . && ruff format .`; `mypy`; Django `python manage.py migrate|test|runserver`; FastAPI `uvicorn app.main:app --reload`.
**Catat**: manajer paket; versi Python; struktur app; ORM & migrasi (Alembic/Django); skema (Pydantic); tugas latar (Celery/RQ); typing strictness.
**Jebakan**: venv tidak aktif; migrasi konflik; N+1 di ORM; blocking call di handler async.

## Go

**Perintah**: `go build ./...`, `go test ./... -race`, `go vet ./...`, `golangci-lint run`.
**Catat**: layout (cmd/, internal/, pkg/), penanganan error (wrapping `%w`), context propagation, DI manual vs wire, konfigurasi, migrasi DB.

## Flutter

**Perintah**: `flutter pub get`, `flutter run`, `flutter test`, `flutter analyze`, `dart format .`, `dart run build_runner build --delete-conflicting-outputs`.
**Catat**: state management (Riverpod/Bloc/Provider), routing (go_router), struktur fitur, flavor/env, file generated (`*.g.dart`, `*.freezed.dart`) tidak diedit tangan.

## Monorepo & tooling

- **Workspace**: pnpm/npm/yarn workspaces, Turborepo, Nx, Gradle multi-module. Catat perintah dengan filter (`pnpm --filter`, `turbo run test --filter=web`, `./gradlew :feature:x:test`).
- **CI**: baca `.github/workflows/*.yml` / `.gitlab-ci.yml`; langkah CI adalah sumber terbaik untuk perintah verifikasi yang "benar".
- **Hooks**: Husky/lefthook/pre-commit; catat apa yang dijalankan agar agent tidak memakai `--no-verify`.
- **Versi runtime**: `.nvmrc`, `.tool-versions`, `.php-version`, `.java-version`, `engines` di package.json.
- **Konvensi commit**: commitlint, Conventional Commits.

## Hosting dan deployment

- **cPanel shared hosting**: biasanya tanpa SSH/CLI penuh; catat cara upload (Git deployment/File Manager/FTP/artefak zip), lokasi document root (`public_html`, `public` Laravel dipetakan), versi PHP via MultiPHP, cron lewat panel, ekstensi PHP yang aktif, batas memori/waktu eksekusi, cara menjalankan migrasi tanpa SSH, `.htaccess`.
- **VPS + aaPanel**: layanan (Nginx/Apache, PHP-FPM, MySQL, Redis), pengelola proses (Supervisor/pm2) untuk queue/worker, SSL (Let's Encrypt), firewall, backup, cron, izin file (www user).
- **Google Cloud Run**: Dockerfile, port `$PORT`, variabel lingkungan & Secret Manager, region, concurrency/min-instances (cold start), perintah `gcloud run deploy`, layanan terkait (Cloud SQL, Artifact Registry), IAM.
- **Vercel/Netlify/Firebase Hosting**: perintah build, output dir, env per lingkungan, preview deploy, rewrites.
- Untuk semua: pisahkan lingkungan, catat rollback, jangan taruh kredensial di dokumen.

## Pengetahuan khusus domain (jika terdeteksi)

- **Aplikasi pendidikan/ujian**: aturan integritas ujian, zona waktu, kuota peserta, data siswa (privasi), format soal & pemeriksaan jawaban, pola offline.
- **Aplikasi anak**: batasan data pribadi, moderasi konten, enkripsi percakapan, kontrol orang tua/guru, ukuran sentuh & bahasa sederhana.
- **Toko produk digital/pembayaran**: idempotensi webhook, status pesanan, pengiriman file/lisensi, rekonsiliasi, pajak/biaya, jangan simpan data kartu.
- **Chat/realtime**: ordering & sinkronisasi pesan, pengiriman ulang, status baca, pagination riwayat, penyimpanan lampiran.
