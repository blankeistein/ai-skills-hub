# Panduan menulis AGENTS.md

Daftar isi: [Tujuan](#tujuan) · [Struktur](#struktur-yang-direkomendasikan) · [Detail tiap bagian](#detail-tiap-bagian) · [Monorepo](#monorepo-dan-agentsmd-bersarang) · [Anti-pola](#anti-pola) · [Contoh sebelum/sesudah](#contoh-sebelumsesudah) · [Pemeliharaan](#pemeliharaan)

## Tujuan

AGENTS.md adalah "README untuk agent". README menjelaskan projek ke manusia (apa, kenapa, demo); AGENTS.md memberi agent hal operasional yang terlalu detail atau terlalu spesifik untuk README: perintah yang tepat, konvensi, batasan, dan jebakan. Agent membaca file terdekat dengan file yang sedang diedit, sehingga file bersarang bersifat "menimpa" yang lebih umum.

Dua pembaca, dua kebutuhan:
- **Agent**: butuh perintah eksak, aturan yang bisa dicek, dan alasan di balik aturan agar bisa menggeneralisasi.
- **Manusia (reviewer)**: butuh bisa membaca file ini dalam 3 menit dan setuju bahwa itu aturan tim.

## Struktur yang direkomendasikan

Urutan penting: yang paling sering dibutuhkan ada di atas.

```
# <Nama Projek>                      ← 1 kalimat: apa ini, untuk siapa
## Commands                          ← install, dev, test, lint, build, migrate
## Tech stack                        ← versi utama, hanya yang memengaruhi cara menulis kode
## Project structure                 ← peta folder, hanya yang non-obvious
## Conventions                       ← penamaan, pola, dengan contoh file nyata
## Testing                           ← framework, lokasi, cara menjalankan satu test, ekspektasi
## Git & PR workflow                 ← branch, commit format, checklist PR
## Boundaries                        ← Always / Ask first / Never
## Gotchas                           ← jebakan, quirk lingkungan, bug yang berulang
## Docs lanjutan                     ← tautan + kapan membacanya
```

Hapus bagian yang tidak berlaku. Tambahkan bagian khusus bila perlu (Environment variables, Deployment, i18n, Feature flags).

## Detail tiap bagian

### Commands
- Gunakan code block; satu baris per perintah dengan komentar singkat (durasi, prasyarat).
- Sertakan cara menjalankan **satu** test/file (agent sering butuh ini): `npx vitest run path/to/file.test.ts`, `php artisan test --filter=NamaTest`, `./gradlew :app:testDebugUnitTest --tests "*.NamaTest"`.
- Sertakan perintah verifikasi gabungan jika ada ("sebelum selesai, jalankan: `npm run lint && npm run typecheck && npm test`").
- Catat prasyarat lingkungan: versi Node/PHP/JDK, service yang harus hidup (MySQL, Redis, emulator Firebase), file `.env` yang harus disalin.
- Tandai perintah yang **berbahaya/lambat/berbayar** (reset DB, deploy, panggil API berbayar).

### Tech stack
Cukup daftar yang memengaruhi keputusan kode: framework + versi mayor, bahasa/strictness, ORM, library state/UI, test runner. Contoh: "React 18 + TypeScript strict, TanStack Query untuk server state (bukan Redux), Tailwind 3". Jangan menyalin seluruh dependency.

### Project structure
Peta singkat hanya untuk folder yang artinya tidak jelas atau punya aturan khusus:
```
app/Services/      # logika bisnis; controller tipis
app/Actions/       # satu use-case per kelas, method handle()
resources/js/      # React SPA (Inertia); komponen di components/, halaman di Pages/
functions/         # Cloud Functions (Node 20); deploy terpisah
```
Tandai folder **generated/vendored** yang tidak boleh diedit: `# GENERATED - jangan edit tangan`.

### Conventions
Tulis sebagai aturan yang bisa dicek, dengan contoh rujukan:
- Penamaan: file, komponen, tabel DB, route, key i18n.
- Pola arsitektur: di mana logika bisnis tinggal, bagaimana error ditangani, bagaimana data di-fetch.
- Gaya yang tidak ditegakkan linter (lihat contoh yang disukai dengan path).
- Sertakan **alasan** untuk aturan yang tidak intuitif ("jangan pakai `useEffect` untuk fetch; kita pakai TanStack Query agar cache dan retry konsisten").

### Testing
- Framework, lokasi file test, pola penamaan.
- Ekspektasi: test baru untuk bug fix? Mock apa yang boleh/tidak? Apakah test menyentuh DB nyata?
- Jika test bergantung pada layanan eksternal, katakan cara men-stub atau menjalankannya.

### Git & PR workflow
Format commit (Conventional Commits?), pola nama branch, apakah rebase atau merge, checklist PR, siapa review. Satu-dua baris saja bila tim kecil.

### Boundaries (tiga tingkat)
```
### Always
- Jalankan lint + test sebelum menyatakan tugas selesai
- Ikuti pola Form Request untuk validasi input

### Ask first
- Menambah dependency baru
- Mengubah skema DB / membuat migrasi
- Mengubah file CI/CD atau konfigurasi deploy

### Never
- Commit secret / file .env
- Mengedit migrasi yang sudah ter-merge atau file di dist/ dan generated/
- Menjalankan perintah destruktif di database (migrate:fresh, DROP) di luar lingkungan lokal
```
Pilih batasan berdasarkan kesalahan nyata atau risiko tinggi, bukan daftar umum.

### Gotchas
Bagian paling bernilai dan paling sering terlewat. Contoh bentuk:
- "Firestore rules diuji dengan emulator; ubah `firestore.rules` tanpa menjalankan `npm run test:rules` akan lolos CI tapi gagal di produksi."
- "cPanel shared hosting tidak punya akses SSH untuk `composer install`; vendor/ di-commit lewat artefak build."
- "Timezone server UTC, tampilan Asia/Jakarta; jangan format tanggal di backend."

Kumpulkan dari: riwayat bug, review PR berulang, pertanyaan anggota baru, dan "kenapa ini aneh?" saat membaca kode.

### Docs lanjutan
Tabel "baca X kalau Y" supaya agent memuat dokumen panjang hanya saat perlu:
```
| Dokumen | Baca saat |
|---|---|
| docs/DATABASE.md | mengubah skema / menulis query kompleks |
| DESIGN.md | membuat atau mengubah UI |
```

## Monorepo dan AGENTS.md bersarang

- Root: aturan lintas-paket (perintah workspace, konvensi commit, tool bersama).
- Tiap paket/app: `AGENTS.md` sendiri dengan perintah dan konvensi lokal. File terdekat menang bila bertentangan.
- Jangan ulangi isi root di paket; cukup "Lihat `/AGENTS.md` untuk aturan umum".
- Tulis perintah dengan filter workspace: `pnpm --filter web test`, `./gradlew :feature:chat:test`.

## Anti-pola

| Anti-pola | Kenapa buruk | Perbaikan |
|---|---|---|
| Menyalin README | Duplikasi, cepat usang | Tautkan README |
| "Tulis kode bersih, ikuti SOLID" | Tidak bisa diverifikasi, tidak mengubah perilaku | Hapus atau ganti aturan spesifik |
| Daftar dependency penuh | Boros konteks | Hanya yang memengaruhi gaya kode |
| Aturan gaya yang sudah ada di linter | Dua sumber kebenaran | Tunjuk config linter |
| Perintah yang belum pernah dijalankan | Agent mengeksekusi perintah rusak | Verifikasi atau `TODO` |
| Instruksi dengan nada kapital berlebihan (JANGAN!!! SELALU!!!) | Menurunkan kalibrasi prioritas | Satu penjelasan alasan |
| Menyimpan secret/IP internal | Bocor ke riwayat git | Rujuk nama env var saja |
| Changelog/to-do di dalamnya | Cepat usang, bukan panduan | Pindahkan ke issue tracker |
| Persona ("kamu adalah senior engineer 20 tahun") | Hampir tidak berpengaruh | Aturan konkret |

## Contoh sebelum/sesudah

**Sebelum** (nyata-nyata terlalu umum):
```
# Projek Sekolah
Ini aplikasi untuk sekolah. Gunakan React dan Firebase.
Tulis kode yang rapi dan jangan lupa test.
```

**Sesudah**:
```
# Projek Sekolah - portal ujian online (React SPA + Firebase)

## Commands
npm run dev            # Vite :5173, otomatis konek ke emulator Firebase
npm run emulators      # firebase emulators:start (Auth, Firestore, Functions)
npm test               # Vitest; satu file: npx vitest run src/features/exam/timer.test.ts
npm run lint && npm run typecheck   # wajib hijau sebelum PR

## Conventions
- Data Firestore diakses hanya lewat `src/data/*Repo.ts`; komponen tidak memanggil SDK langsung.
- State server pakai TanStack Query; state UI lokal pakai useState. Jangan tambah Redux/Zustand.

## Boundaries
- Ask first: ubah `firestore.rules`, tambah koleksi, tambah dependency.
- Never: simpan jawaban siswa di localStorage; hardcode UID admin.

## Gotchas
- Timestamp ujian disimpan UTC (`serverTimestamp()`); format ke Asia/Jakarta hanya di layer tampilan.
```

## Pemeliharaan

- Perlakukan AGENTS.md seperti kode: diubah lewat PR, di-review, dan diperbarui saat perintah/struktur berubah.
- Saat agent melakukan kesalahan berulang, tambahkan satu baris di Gotchas atau Boundaries, bukan paragraf.
- Tinjau tiap beberapa bulan: hapus baris yang sudah tidak mencegah kesalahan apa pun.
- Pertimbangkan langkah CI yang memverifikasi perintah di AGENTS.md masih valid (lihat `scripts/lint_guides.py`).
