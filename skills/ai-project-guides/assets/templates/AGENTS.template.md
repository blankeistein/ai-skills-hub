# <Nama Projek>

<1 kalimat: apa projek ini, untuk siapa, dan bentuknya (web app / Android app / API / library).>

## Commands

```bash
<install>            # prasyarat: <versi runtime, service yang harus hidup>
<dev>                # dev server di <port/URL>
<test>               # semua test (~<durasi>)
<test-satu>          # satu file/test: <contoh perintah>
<lint-format>        # lint + format
<typecheck>          # jika ada
<build>              # build produksi
```

Sebelum menyatakan tugas selesai, jalankan: `<lint> && <typecheck> && <test>`.

## Tech stack

- <Framework + versi mayor>, <bahasa + strictness>
- <Database/ORM>, <state management>, <styling/UI library>
- <Test runner>
- (hanya yang memengaruhi cara menulis kode)

## Project structure

```
<folder>/    # <peran, hanya yang non-obvious>
<folder>/    # GENERATED - jangan edit tangan
```

## Conventions

- <Penamaan file/komponen/tabel>
- <Di mana logika bisnis tinggal; contoh: `path/ke/contoh.ext`>
- <Pola error handling / data fetching + alasan>
- Gaya kode ditegakkan oleh `<config linter>`; jangan diulang di sini.

## Testing

- Framework: <...>; lokasi: `<...>`; penamaan: `<...>`
- Bug fix wajib disertai test regresi; fitur baru: jalur sukses + minimal satu kasus gagal.
- <Aturan mock: apa yang di-mock / tidak>

## Git & PR workflow

- Branch: `<pola>`; commit: <Conventional Commits / lainnya>
- PR: <checklist singkat>; jangan push langsung ke `<main>`.

## Boundaries

### Always
- <mis. jalankan verifikasi sebelum selesai>

### Ask first
- Menambah dependency baru
- Mengubah skema database / aturan keamanan / konfigurasi CI-deploy

### Never
- Commit secret, `.env`, keystore, atau kredensial
- Mengedit file generated / migrasi yang sudah ter-merge
- Menjalankan perintah destruktif atau deploy ke produksi tanpa instruksi eksplisit

## Gotchas

- <jebakan nyata #1 + akibatnya>
- <quirk lingkungan #2>

## Docs lanjutan

| Dokumen | Baca saat |
|---|---|
| `DESIGN.md` | membuat/mengubah UI |
| `docs/ARCHITECTURE.md` | menambah modul atau mengubah alur data |
| `docs/DATABASE.md` | mengubah skema / query kompleks |
