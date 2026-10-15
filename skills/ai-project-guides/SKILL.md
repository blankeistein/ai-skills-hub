---
name: ai-project-guides
description: Create, audit, and update AI-agent guidance files for software projects - AGENTS.md, CLAUDE.md, GEMINI.md, DESIGN.md, ARCHITECTURE.md, CONTRIBUTING.md, TESTING.md, SECURITY.md, DATABASE.md, API.md, DEPLOYMENT.md, .cursor/rules, .github/copilot-instructions.md, and similar docs that tell coding agents (Claude Code, Codex, Cursor, Copilot, Gemini CLI, Jules) how a repo works. Use this skill whenever the user mentions AGENTS.md, CLAUDE.md, DESIGN.md, "panduan AI", "instruksi untuk AI agent", "context file", "rules file", "onboarding doc for AI", "dokumentasi untuk coding agent", "buatkan panduan projek", design system doc, or wants an AI to understand/follow their codebase conventions, stack, commands, or UI style - even if they do not name the exact file. Also use when a project has a bloated, outdated, or contradictory agent instruction file that needs cleanup, or when a repo should be made "AI-ready".
---

# AI Project Guides

Buat dokumen panduan yang membuat coding agent (dan manusia baru) langsung produktif di sebuah repo: **AGENTS.md** sebagai file utama, **DESIGN.md** untuk bahasa visual/UI, dan dokumen pendukung lain bila memang dibutuhkan.

## Prinsip inti (baca dulu, ini yang membedakan panduan bagus vs sampah)

1. **Agent membaca file ini di awal setiap sesi, jadi setiap baris memakan konteks.** Tulis hanya hal yang agent *tidak bisa simpulkan sendiri* dari membaca kode: perintah build/test yang tepat, konvensi non-obvious, jebakan (gotchas), batasan, dan keputusan arsitektur beserta alasannya. Jangan menjelaskan hal yang sudah jelas dari nama folder atau konfigurasi linter.
2. **Verifikasi, jangan mengarang.** Setiap perintah, path, dan versi yang ditulis harus berasal dari repo (package.json, composer.json, Makefile, CI workflow, build.gradle, dll.). Kalau tidak bisa diverifikasi, tulis `TODO: konfirmasi` dan tanyakan ke user. Perintah yang salah lebih buruk daripada tidak ada perintah, karena agent akan menjalankannya dengan percaya diri.
3. **Perintah dulu, prosa belakangan.** Agent paling sering butuh: cara install, run, test, lint, build. Taruh di bagian atas dalam code block yang bisa langsung dijalankan.
4. **Konkret mengalahkan abstrak.** "Gunakan Form Request untuk validasi, lihat `app/Http/Requests/StorePostRequest.php`" lebih berguna daripada "ikuti best practice validasi". Satu contoh file nyata bernilai lebih dari satu paragraf aturan.
5. **Batasan eksplisit.** Pisahkan tiga tingkat: *Selalu lakukan*, *Tanya dulu*, *Jangan pernah*. Ini mencegah kesalahan mahal (hapus migrasi, edit file generated, commit secret).
6. **Satu sumber kebenaran.** Isi utama ditulis sekali di `AGENTS.md`; file lain (CLAUDE.md, GEMINI.md, copilot-instructions) hanya menunjuk ke sana. Duplikasi membuat file saling bertentangan seiring waktu.
7. **Pendek itu fitur.** Target AGENTS.md 80-250 baris. Kalau lebih panjang, pecah ke `docs/` dan tautkan dengan kapan harus dibaca ("baca `docs/DATABASE.md` sebelum mengubah skema").
8. **Jangan duplikasi aturan yang ditegakkan tool.** Kalau ESLint/Prettier/Pint/ktlint sudah menegakkan gaya, tulis "format dengan `npm run format`" dan tunjuk file konfigurasinya, jangan salin aturannya.

## Alur kerja

### Langkah 1 - Tentukan cakupan

Dari permintaan user, tentukan file apa yang dibutuhkan. Jika ambigu, default-nya:

| Situasi user | Hasilkan |
|---|---|
| "Buat AGENTS.md / panduan AI untuk projek ini" | `AGENTS.md` (+ pointer `CLAUDE.md`) |
| "Lengkap" / "semua panduan" / "AI-ready" | `AGENTS.md`, `CLAUDE.md`, `DESIGN.md` (jika ada UI), `ARCHITECTURE.md`, `TESTING.md`, plus pointer file tool lain yang dipakai tim |
| Projek punya UI (web/mobile) | Tambahkan `DESIGN.md` |
| Ada DB / API publik / deployment non-trivial | Pertimbangkan `DATABASE.md`, `API.md`, `DEPLOYMENT.md` |
| Monorepo | `AGENTS.md` di root + `AGENTS.md` bersarang per paket |
| Sudah ada file, user minta "rapikan/update" | Mode audit (Langkah 5) |

Jangan membuat dokumen yang isinya hanya akan berupa tebakan. Lebih baik 2 dokumen akurat daripada 8 dokumen setengah karangan.

### Langkah 2 - Kumpulkan fakta dari repo

Jika repo tersedia di filesystem (upload, clone, atau path lokal), jalankan pemindai:

```bash
python scripts/scan_project.py <path-repo>            # stack, perintah, struktur, file panduan yang ada
python scripts/extract_design_tokens.py <path-repo>   # warna, font, spacing, tema (untuk DESIGN.md)
```

Keluaran keduanya adalah JSON/teks ringkas; gunakan sebagai *bahan mentah*, lalu baca file kunci sendiri (README, CI workflow, 2-3 file contoh dari tiap lapisan) untuk memahami konvensi yang sebenarnya. Pemindai mendeteksi, tidak memahami.

Jika repo **tidak** tersedia (user hanya mendeskripsikan), ajukan pertanyaan singkat sekaligus (bukan satu per satu):
- Stack dan versi utama, cara menjalankan dev server, test, build
- Struktur folder penting dan konvensi penamaan
- Hal yang sering salah dilakukan AI/anggota baru di projek ini
- Area terlarang (migrasi, file generated, secret, produksi)
- Untuk DESIGN.md: warna brand, font, library komponen, referensi gaya yang disukai

Lalu tulis draf dengan penanda `TODO` pada bagian yang belum pasti.

### Langkah 3 - Tulis dokumen

Baca referensi sesuai kebutuhan (jangan baca semuanya):

- `references/agents-md.md` - struktur, bagian wajib, contoh baik vs buruk, pola monorepo. **Selalu baca untuk AGENTS.md.**
- `references/design-md.md` - struktur design system untuk agent, cara menerjemahkan token ke kode, checklist aksesibilitas. **Baca untuk DESIGN.md.**
- `references/other-guides.md` - CLAUDE.md, GEMINI.md, `.cursor/rules`, copilot-instructions, ARCHITECTURE/TESTING/SECURITY/DATABASE/API/DEPLOYMENT/CONTRIBUTING. **Baca untuk dokumen selain dua di atas.**
- `references/stack-notes.md` - perintah, konvensi, dan jebakan khas per stack (Laravel, React/TypeScript/Vite, Next.js, Kotlin/Jetpack Compose, Firebase, Node/Express, Python/Django/FastAPI, Go, dll.). Baca bagian stack yang relevan saja.

Template siap pakai ada di `assets/templates/` (`AGENTS.template.md`, `DESIGN.template.md`, `ARCHITECTURE.template.md`, `TESTING.template.md`, `CLAUDE.pointer.md`, `cursor-rule.template.mdc`). Salin lalu **isi dengan fakta repo dan hapus bagian yang tidak relevan**; template bukan formulir yang harus terisi penuh.

Aturan bahasa: tulis dalam bahasa yang dipakai tim/user (jika user menulis Indonesia, tulis Indonesia). Biarkan perintah, path, nama simbol, dan istilah teknis baku dalam bahasa aslinya.

### Langkah 4 - Validasi sebelum menyerahkan

Jalankan pemeriksaan ini (bisa pakai `python scripts/lint_guides.py <file-atau-folder>` untuk bagian otomatis):

- [ ] Setiap perintah di code block benar-benar ada (script di package.json, target Makefile, task Gradle, artisan command)
- [ ] Setiap path yang disebut benar-benar ada di repo
- [ ] Tidak ada secret, token, kredensial, atau URL internal sensitif
- [ ] Tidak ada instruksi yang saling bertentangan antar file
- [ ] Tidak ada bagian generik yang berlaku untuk semua projek ("tulis kode yang bersih")
- [ ] Panjang masuk akal; bagian panjang dipindah ke `docs/`
- [ ] `TODO` yang tersisa dilaporkan ke user secara eksplisit

### Langkah 5 - Mode audit (file sudah ada)

Saat user sudah punya AGENTS.md/CLAUDE.md dan ingin diperbaiki:
1. Jalankan `scripts/lint_guides.py` untuk menemukan perintah/path mati, baris terlalu panjang, duplikasi, dan kata-kata mengambang.
2. Bandingkan klaim dengan repo (script yang hilang, folder yang sudah pindah, versi yang usang).
3. Laporkan temuan dalam daftar singkat (apa salah, kenapa penting, perbaikan), lalu terapkan perbaikan. Pertahankan suara dan keputusan tim; ubah isi hanya bila salah, usang, atau mubazir.
4. Jangan menghapus aturan yang tampak aneh tanpa bertanya; sering ada insiden di baliknya. Tandai dengan `TODO: konfirmasi alasan`.

### Langkah 6 - Serahkan

Tampilkan ringkasan: file apa yang dibuat/diubah, apa yang diverifikasi dari repo, dan daftar `TODO`/asumsi yang butuh konfirmasi user. Simpan file langsung ke repo kerja projek (atau ke direktori output yang diminta user). Untuk beberapa file, sajikan AGENTS.md lebih dulu.

## Pola keputusan cepat

- **AGENTS.md vs CLAUDE.md?** AGENTS.md adalah format lintas-tool (Codex, Cursor, Copilot, Gemini CLI, Jules, Claude Code lewat import). Tulis isi di AGENTS.md; buat `CLAUDE.md` berisi `@AGENTS.md` plus catatan khusus Claude bila ada.
- **DESIGN.md vs AGENTS.md?** AGENTS.md menjawab "bagaimana bekerja di repo ini"; DESIGN.md menjawab "bagaimana tampilan dan rasa produk ini". Aturan UI singkat (misalnya "pakai komponen dari `components/ui`") boleh ada di AGENTS.md dengan tautan ke DESIGN.md.
- **Terlalu banyak aturan?** Pindahkan aturan spesifik-folder ke AGENTS.md bersarang atau `.cursor/rules` dengan glob, supaya hanya dimuat saat relevan.
- **Tidak yakin sebuah baris layak ada?** Tanya: "Kalau baris ini dihapus, apakah agent akan membuat kesalahan nyata?" Jika tidak, hapus.

## Contoh singkat

**Buruk** (generik, tidak bisa diverifikasi):
> Projek ini menggunakan praktik terbaik modern. Pastikan kode bersih dan teruji. Jalankan test sebelum commit.

**Baik** (spesifik, bisa dieksekusi):
> ```bash
> composer test            # Pest, ~40 detik; wajib hijau sebelum PR
> npm run dev              # Vite di :5173, perlu `php artisan serve` jalan bersamaan
> ```
> - Jangan edit `database/migrations/*` yang sudah ter-merge; buat migrasi baru.
> - Validasi selalu lewat Form Request (contoh: `app/Http/Requests/StorePostRequest.php`).
