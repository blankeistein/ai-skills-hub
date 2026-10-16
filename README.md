# 🧠 AI Skills Hub

Koleksi dan repositori standar **AI Agent Skills** yang siap pakai dan modular untuk berbagai AI coding assistant (seperti Google Antigravity, Claude Code, Cursor, Copilot, dan agent LLM lainnya).

Setiap skill dirancang mengikuti prinsip **Progressive Disclosure**, sehingga AI dapat memuat instruksi spesifik hanya saat diperlukan tanpa membebani context window.

---

## 📚 Katalog Skill yang Tersedia

| Skill | Kategori | Deskripsi Singkat | Lokasi |
|---|---|---|---|
| **`ai-project-guides`** | `AI Workflow` / `Guidance` | Pembuatan, audit, dan standardisasi panduan AI agent (`AGENTS.md`, `CLAUDE.md`, `DESIGN.md`, rules) agar coding assistant memahami konvensi dan arsitektur repositori. | [`skills/ai-project-guides`](./skills/ai-project-guides/SKILL.md) |
| **`android-code-audit`** | `Android` / `Quality` | Audit sistematis proyek Kotlin & Jetpack Compose untuk mendeteksi bugs, memory leaks, race conditions, performa (jank/lag), security, dan arsitektur. | [`skills/android-code-audit`](./skills/android-code-audit/SKILL.md) |
| **`android-testing-setup`** | `Android` / `Testing` | Setup, penulisan, dan review unit tests (ViewModel/Repo/UseCase) & Compose UI tests dengan JUnit, MockK, Coroutines-test, dan Turbine. | [`skills/android-testing-setup`](./skills/android-testing-setup/SKILL.md) |
| **`compose-optimizer`** | `Android` / `Compose` | Review dan optimasi komponen & screen Jetpack Compose untuk performa (recomposition), struktur, dan arsitektur (state hoisting). | [`skills/compose-optimizer`](./skills/compose-optimizer/SKILL.md) |
| **`project-docs`** | `Documentation` / `Engineering` | Pembuatan dokumentasi teknis proyek software yang komprehensif dan akurat (README, arsitektur, data model, API reference, deployment, setup) berbasis analisis langsung pada codebase. | [`skills/project-docs`](./skills/project-docs/SKILL.md) |
| **`remotion-video-builder`** | `Video` / `Remotion` | Tahap 3 pipeline video (produksi): pembuatan video berbasis kode React + TypeScript dengan Remotion dari `scenes.json` atau storyboard, lengkap dengan animasi, layout, dan render MP4. | [`skills/remotion-video-builder`](./skills/remotion-video-builder/SKILL.md) |
| **`video-review-export`** | `Video` / `Post-Production` | Tahap 4 pipeline video (pasca-produksi): checklist review kualitas, parameter export/render per platform (TikTok, Reels, Shorts, YouTube), optimasi ukuran bitrate, dan paket publikasi. | [`skills/video-review-export`](./skills/video-review-export/SKILL.md) |
| **`video-script-writer`** | `Video` / `Pre-Production` | Tahap 1 pipeline video (pra-produksi): penulisan ide konsep, brief penonton/tujuan, hook memikat, dan naskah/script video pendek atau explainer siap storyboard. | [`skills/video-script-writer`](./skills/video-script-writer/SKILL.md) |
| **`video-storyboard`** | `Video` / `Pre-Production` | Tahap 2 pipeline video (pra-produksi): pemecahan naskah jadi storyboard per-scene dan struktur data `scenes.json` yang siap dieksekusi langsung di Remotion. | [`skills/video-storyboard`](./skills/video-storyboard/SKILL.md) |

> 💡 *Katalog otomatis tersinkronisasi dalam [`catalog.json`](./catalog.json).*

### 🎬 Pipeline Pembuatan Video (End-to-End)

Keempat skill video dirancang untuk bekerja secara berkesinambungan (*chained pipeline*):
```text
1. video-script-writer      -> Menghasilkan naskah matang, brief, dan variasi hook
        ↓
2. video-storyboard         -> Memecah naskah ke visual scene & file scenes.json
        ↓
3. remotion-video-builder   -> Mengonversi scenes.json ke komponen React + animasi Remotion
        ↓
4. video-review-export      -> Review kualitas, render MP4 per platform & materi publikasi
```

---

## 🏗️ Struktur Standar Repositori

Repositori ini mengikuti best practice struktur modular untuk AI Skills:

```text
my-skill/
├── .github/
│   └── workflows/
│       └── validate-skills.yml     # CI otomatis untuk verifikasi skill
├── skills/                         # Direktori utama seluruh skill
│   └── android-code-audit/
│       ├── SKILL.md                # Entry point instruksi & trigger YAML frontmatter
│       └── references/             # Dokumentasi mendalam yang di-load on-demand
│           ├── bugs.md
│           ├── concurrency.md
│           ├── memory-leaks.md
│           ├── performance.md
│           ├── security.md
│           └── architecture-accessibility.md
├── templates/                      # Template dasar untuk membuat skill baru
│   └── skill-template/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── examples/
├── scripts/                        # Utility CLI untuk developer
│   ├── create_skill.py             # Generator skill baru
│   └── validate_skills.py          # Linter & validator frontmatter + broken links
├── catalog.json                    # Manifest indeks metadata skill (terkompilasi)
├── CONTRIBUTING.md                 # Panduan kontribusi dan standar penulisan skill
├── LICENSE                         # Lisensi MIT
└── README.md                       # Dokumentasi utama proyek
```

---

## 🚀 Cara Menggunakan Skill

### 1. Di Google Antigravity / Gemini CLI
Salin folder skill yang diinginkan ke direktori kustomisasi Antigravity:

* **Level Workspace (Proyek Aktif):**
  ```bash
  # Letakkan di folder .agents/skills/ di root proyek Anda
  mkdir -p your-project/.agents/skills
  cp -r skills/android-code-audit your-project/.agents/skills/
  ```

* **Level Global (Berlaku untuk semua proyek di PC):**
  ```bash
  # Windows (PowerShell)
  cp -r skills/android-code-audit $HOME/.gemini/config/skills/
  
  # Linux/macOS
  cp -r skills/android-code-audit ~/.gemini/config/skills/
  ```

### 2. Di Claude Code / Custom Coding Agents
Salin skill ke folder konfigurasi agen atau cantumkan direktori `SKILL.md` ke dalam konteks instruksi agen Anda.

---

## 🛠️ Panduan Pengembangan Skill Baru

### Membuat Skill Baru dari Template
Gunakan generator otomatis untuk membuat kerangka skill baru yang telah terstandarisasi:

```bash
python scripts/create_skill.py <nama-skill> --description "<deskripsi pemicu skill>"
```

*Contoh:*
```bash
python scripts/create_skill.py flutter-code-audit --description "Audit komprehensif untuk aplikasi Flutter/Dart."
```

### Validasi & Linter Skill
Pastikan semua skill mematuhi format frontmatter, tidak ada broken link, dan struktur direktori sesuai standar:

```bash
python scripts/validate_skills.py
```

Skrip ini akan:
1. Memverifikasi kelengkapan YAML frontmatter (`name`, `description`).
2. Memeriksa broken link relatif antar dokumen markdown.
3. Memperbarui indeks katalog di `catalog.json`.

---

## 🤝 Kontribusi

Tertarik menambahkan skill baru atau meningkatkan skill yang ada? Silakan baca panduan lengkap di [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](./LICENSE).
