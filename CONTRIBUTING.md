# Contributing to AI Skills Hub

Terima kasih atas minat Anda untuk berkontribusi pada repositori AI Skills ini! Panduan ini menjelaskan standar dan konvensi pembuatan skill agar kompatibel dan optimal digunakan oleh berbagai AI Coding Assistant (Antigravity CLI, Claude Code, Cursor, Copilot, dsb.).

---

## 📁 Anatomi Direktori Skill

Setiap skill ditempatkan di folder `skills/<skill-name>/` dengan struktur standar:

```text
skills/<skill-name>/
├── SKILL.md            # [Wajib] Instruksi utama dengan YAML frontmatter
├── references/         # [Opsional] Dokumentasi detail, pola kode, checklist
│   ├── bugs.md
│   └── performance.md
├── scripts/            # [Opsional] Skrip otomasi/helper (bash/python)
└── examples/           # [Opsional] Contoh implementasi atau input/output
```

---

## 📝 Format `SKILL.md`

File `SKILL.md` wajib diawali dengan **YAML Frontmatter** yang memuat field `name` dan `description`.

```markdown
---
name: nama-skill-anda
description: >-
  Penjelasan spesifik mengenai apa yang dilakukan skill ini dan kapan AI harus
  mengaktifkannya. Sebutkan trigger keyword atau kondisi penggunaan yang jelas.
---

# Judul Skill

Penjelasan singkat tentang skill dan domain masalah yang ditangani.

## Ground Rules
1. Aturan 1...
2. Aturan 2...

## Workflow
### Step 1 — ...
### Step 2 — ...

## References
- [Panduan Detail](./references/panduan.md)
```

### Aturan Frontmatter:
1. **`name`**: Harus berformat *kebab-case* (huruf kecil, angka, tanda hubung). Contoh: `android-code-audit`, `react-perf-optimizer`.
2. **`description`**: Sangat krusial! AI membaca deskripsi ini untuk memutuskan apakah skill perlu diaktifkan (*progressive disclosure*). Gunakan sudut pandang orang ketiga dan sebutkan skenario pemanggilan yang jelas.

---

## ⚡ Prinsip & Best Practices

1. **Progressive Disclosure (Konteks Efisien)**:
   - Jaga `SKILL.md` tetap ringkas dan fokus pada workflow tingkat tinggi.
   - Pindahkan detail teknis yang panjang ke folder `references/` dan buat tautan relatif ke file tersebut. AI hanya akan membaca file referensi saat benar-benar dibutuhkan.
2. **Path & Link Valid**:
   - Semua tautan relatif seperti `[Bugs](./references/bugs.md)` harus valid dan menunjuk ke file yang benar-benar ada di repositori.
3. **Tool Agnostic**:
   - Tulis instruksi agar dapat dijalankan oleh asisten AI apa pun yang memiliki akses baca file / terminal workspace.
4. **Instruksi Actionable**:
   - Sertakan aturan main (*ground rules*), langkah sistematis (*step-by-step*), dan metode verifikasi (*verification*).

---

## 🛠️ Membuat & Memvalidasi Skill Baru

### 1. Scaffold Skill Baru Menggunakan Skrip
Gunakan skrip generator otomatis untuk membuat template skill baru:

```bash
python scripts/create_skill.py nama-skill-baru --description "Deskripsi kapan skill digunakan..."
```

### 2. Tulis Instruksi & Referensi
Edit `skills/nama-skill-baru/SKILL.md` dan tambahkan panduan terkait di folder `references/`.

### 3. Validasi dengan Skrip Linter
Jalankan skrip validasi lokal sebelum membuat commit:

```bash
python scripts/validate_skills.py
```

Skrip ini akan memeriksa:
- Integritas frontmatter (`name`, `description`).
- Broken relative markdown links.
- Memperbarui manifest katalog `catalog.json`.

---

## 🚀 Alur Pull Request

1. Fork repositori ini.
2. Buat branch fitur baru (`git checkout -b feature/nama-skill`).
3. Buat dan lengkapi skill Anda di `skills/<nama-skill>/`.
4. Jalankan `python scripts/validate_skills.py` dan pastikan berstatus `[PASS]`.
5. Commit perubahan Anda (`git commit -m "feat: add <nama-skill>"`).
6. Push ke branch Anda dan buka Pull Request.
