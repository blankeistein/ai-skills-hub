---
name: video-script-writer
description: Tahap 1 pipeline video (pra-produksi). Menulis ide, tujuan, hook, dan naskah/script video pendek atau explainer sebelum dibuat visualnya. Gunakan skill ini setiap kali user ingin bikin konten video, minta ide video, naskah, script, voice over, caption, hook TikTok/Reels/Shorts/YouTube, atau bilang "aku mau bikin video tentang X", meskipun mereka tidak menyebut kata "script". Jalankan SEBELUM video-storyboard dan remotion-video-builder.
---

# Video Script Writer

Bagian dari pipeline 4 skill: **script → storyboard → remotion build → review/export**.
Tugas skill ini: mengubah ide mentah jadi naskah yang siap di-storyboard. Pra-produksi adalah fase yang paling menentukan; video yang bertele-tele hampir selalu gagal di sini, bukan di animasinya.

Balas dalam bahasa yang dipakai user (default Bahasa Indonesia santai).

## Langkah

### 1. Kunci brief (tanya hanya yang belum jelas, maksimal 3 pertanyaan sekaligus)
- **Penonton**: siapa, level pengetahuannya apa
- **Tujuan**: setelah nonton, penonton harus paham/merasa/melakukan apa (satu saja)
- **Platform & durasi**: 9:16 (Reels/TikTok/Shorts, 15-60 dtk) atau 16:9 (YouTube, lebih panjang)
- **Nada**: santai, serius, lucu, edukatif
- **Sumber suara**: voice over, teks saja, atau musik saja (ini menentukan gaya naskah)

Kalau user sudah memberi cukup info, jangan interogasi; tulis asumsi dalam satu baris lalu lanjut.

### 2. Satu pesan inti
Rumuskan dalam satu kalimat: "Video ini bilang bahwa ___". Semua yang tidak mendukung kalimat ini dipotong. Alasannya: video pendek tidak punya ruang untuk dua pesan.

### 3. Tulis hook dulu
Berikan 3 opsi hook (3 detik pertama) dengan pendekatan berbeda, misalnya pertanyaan, klaim mengejutkan, atau masalah yang dikenali penonton. Biarkan user memilih, atau pilih yang terbaik dan jelaskan alasannya singkat. Lihat `references/hook-patterns.md`.

### 4. Tulis naskah
Struktur default: **Hook → Masalah/konteks → Isi (maks 3 poin) → Payoff → CTA**.
Aturan ritme:
- Satu kalimat = satu ide; kalimat dibuat untuk diucapkan, bukan dibaca
- Perkiraan kecepatan bicara: ±2,5 kata/detik (Indonesia). 30 dtk ≈ 70-75 kata
- Setiap 3-5 detik harus ada perubahan visual atau informasi baru (catat sebagai penanda `[VISUAL: ...]`)
- Hindari pembuka basa-basi ("Halo guys, di video kali ini...")

### 5. Format output
```
# Judul kerja
Pesan inti: ...
Platform/durasi: ... | Penonton: ... | Nada: ...

## Naskah
[00:00-00:03] HOOK
Narasi: "..."
[VISUAL: ide tampilan singkat]

[00:03-00:10] ...
```
Akhiri dengan hitungan kata, estimasi durasi, dan satu kalimat: "Lanjut ke storyboard?"

## Catatan kualitas
Baca ulang naskah dengan suara. Bagian yang membuat napas tersengal atau lidah kelu perlu dipendekkan. Jangan mengarang fakta atau angka; kalau perlu data, tandai `[CEK FAKTA]` atau cari dulu.
