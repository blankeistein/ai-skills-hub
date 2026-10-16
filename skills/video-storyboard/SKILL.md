---
name: video-storyboard
description: Tahap 2 pipeline video (pra-produksi). Mengubah naskah menjadi storyboard per-scene dan file scenes.json terstruktur (durasi, teks layar, visual, animasi, audio, aset) yang menjadi masukan langsung untuk Remotion. Gunakan skill ini ketika user punya naskah/script dan ingin dibagi per adegan, minta storyboard, shot list, rencana visual, daftar scene, palet warna/font untuk video, atau sebelum membuat video dengan Remotion. Jalankan setelah video-script-writer dan sebelum remotion-video-builder.
---

# Video Storyboard

Bagian dari pipeline: script → **storyboard** → remotion build → review/export.
Storyboard memaksa semua keputusan visual dibuat sebelum menulis kode, sehingga fase produksi tinggal mengeksekusi. Mengubah scene di JSON jauh lebih murah daripada mengubah komponen React.

Balas dalam bahasa user.

## Langkah

### 1. Ambil naskah
Pakai naskah dari percakapan atau yang ditempel user. Jika belum ada, sarankan memakai `video-script-writer` dulu; jangan mengarang naskah sendiri tanpa konfirmasi.

### 2. Tetapkan design tokens (sekali untuk seluruh video)
Tentukan dan tampilkan: rasio & resolusi, fps (default 30), 2-4 warna (background, teks, aksen), 1-2 font (Google Fonts), gaya animasi (mis. "pop spring cepat" atau "fade/slide halus"), mood musik. Satu gaya konsisten lebih baik daripada banyak efek; video terasa generik kalau tiap scene tampil berbeda.

Ukuran standar: 9:16 = 1080x1920, 16:9 = 1920x1080, 1:1 = 1080x1080.

### 3. Pecah jadi scene
- Satu scene = satu ide visual; durasi umumnya 2-6 detik
- Scene pembuka (hook) paling padat visual dan teksnya paling besar
- Teks layar maksimal ±7 kata per scene dan harus terbaca dalam 2 detik
- Total durasi scene harus pas dengan durasi naskah

### 4. Keluarkan dua hal

**A. Tabel storyboard untuk dibaca manusia**

| # | Waktu | Narasi | Teks layar | Visual | Animasi/transisi |
|---|---|---|---|---|---|

**B. `scenes.json`**: simpan sebagai file di dalam proyek (misalnya `src/data/scenes.json`) bila ada akses file, atau tampilkan di code block. Skema dan contoh ada di `references/scenes-schema.md`; baca file itu sebelum menulis JSON.

### 5. Daftar aset
Cantumkan aset yang dibutuhkan (gambar, logo, musik, SFX, voice over) beserta statusnya: `ada` / `perlu dibuat` / `placeholder`. Remotion bisa jalan dengan placeholder, jadi aset yang kurang tidak boleh memblokir.

Akhiri dengan: "Storyboard siap, lanjut bikin videonya di Remotion?"
