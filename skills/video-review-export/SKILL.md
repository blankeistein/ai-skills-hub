---
name: video-review-export
description: Tahap 4 pipeline video (pasca-produksi). Memeriksa dan memperbaiki video setelah dibuat - checklist review (hook, ritme, keterbacaan teks, audio), cara render dan export dengan setting yang tepat per platform (Reels/TikTok/Shorts/YouTube), kompres ukuran, thumbnail, caption dan hashtag posting. Gunakan skill ini ketika user bilang videonya sudah jadi, minta review/feedback video, bingung cara render atau export MP4, file terlalu besar, kualitas jelek, audio terlalu pelan/keras, atau mau mempublikasikan ke sosmed. Jalankan setelah remotion-video-builder.
---

# Video Review & Export

Bagian dari pipeline: script → storyboard → remotion build → **review/export**.
Banyak video bagus gagal karena audio buruk atau export salah, bukan karena idenya. Skill ini menutup siklus: periksa, revisi, render final, siapkan publikasi.

Balas dalam bahasa user.

## Langkah

### 1. Review (minta materi yang bisa dinilai)
AI model atau coding assistant tidak dapat menonton video secara langsung. Minta salah satu: deskripsi hasil, screenshot beberapa frame (`npx remotion still ... --frame=N`), atau scenes.json/naskah terbaru. Nyatakan bahwa review berdasarkan materi itu, bukan tontonan penuh.

Periksa dengan `references/review-checklist.md`. Laporkan temuan dalam urutan dampak: **Kritis** (membuat orang berhenti nonton) → **Penting** → **Opsional**. Untuk tiap temuan beri perbaikan konkret (mis. "scene 3 teks 14 kata, pecah jadi 2 scene" atau "ubah `musicVolume` dari 0.4 ke 0.15").

### 2. Revisi
Terjemahkan temuan ke perubahan nyata: edit scenes.json, ubah timing di komponen, atau ganti aset. Jangan menulis ulang semuanya; ubah yang perlu saja, lalu minta user render ulang dan lapor.

### 3. Export
Gunakan tabel di `references/export-presets.md`. Perintah dasar:
```bash
npx remotion render Main out/video.mp4
npx remotion render Main out/video.mp4 --crf=18 --codec=h264
```
Untuk ukuran file besar, jelaskan trade-off: CRF lebih tinggi = file lebih kecil, kualitas turun. Jika Remotion tidak ditemukan atau render gagal, minta pesan error lengkap sebelum menebak penyebabnya.

### 4. Paket publikasi
Siapkan: judul/caption (hook di kalimat pertama), 3-5 hashtag relevan, ide thumbnail (frame mana yang dipakai dan teks overlay), dan jam posting hanya sebagai saran umum, bukan klaim pasti. Jangan menjanjikan hasil viral.

### 5. Retrospeksi singkat
Tanyakan satu hal: bagian mana dari proses (script, storyboard, build) yang paling memakan waktu? Gunakan jawabannya untuk menyarankan perbaikan template atau scenes.json agar video berikutnya lebih cepat.
