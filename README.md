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

> 💡 *Katalog otomatis tersinkronisasi dalam [`catalog.json`](./catalog.json).*

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
