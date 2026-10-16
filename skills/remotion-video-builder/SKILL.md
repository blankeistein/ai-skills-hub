---
name: remotion-video-builder
description: Tahap 3 pipeline video (produksi). Membuat video dengan Remotion (React + TypeScript) dari scenes.json atau storyboard - menulis komponen scene, animasi spring/interpolate, transisi, teks, audio, lalu menjelaskan cara preview dan render ke MP4. Gunakan skill ini setiap kali user menyebut Remotion, ingin video dari kode React, motion graphics, kinetic typography, video otomatis/massal dari data, explainer animasi, atau minta "buatkan videonya" setelah ada storyboard. Jalankan setelah video-storyboard; jika belum ada storyboard, minta atau buat dulu secara ringkas.
---

# Remotion Video Builder

Bagian dari pipeline: script → storyboard → **remotion build** → review/export.
Remotion merender video dari komponen React: setiap frame adalah hasil fungsi dari nomor frame. Karena itu semua animasi harus digerakkan oleh `useCurrentFrame()`, bukan CSS transition/animation atau `setTimeout`, yang tidak akan ikut ter-render.

Balas dalam bahasa user. Kode dan nama variabel dalam bahasa Inggris.

## Prasyarat
Masukan ideal: `scenes.json` dari skill `video-storyboard` (skema di `../video-storyboard/references/scenes-schema.md`). Jika user hanya memberi naskah, buat scenes.json ringkas dulu dan tunjukkan.

## Alur kerja

1. **Setup proyek** (user menjalankan di komputernya; lingkungan chat tidak bisa menampilkan preview):
   ```bash
   npx create-video@latest
   cd nama-proyek && npm run dev   # membuka Remotion Studio
   ```
   Tanyakan atau asumsikan template Blank + TypeScript. Jangan menebak nomor versi paket; biarkan `create-video` memilihnya.

2. **Struktur file yang dihasilkan** (lihat `references/patterns.md` untuk kode lengkap):
   ```
   src/
     Root.tsx            # daftar <Composition>, hitung durasi total dari scenes.json
     data/scenes.json
     Video.tsx           # menyusun semua scene dengan <Series> / <TransitionSeries>
     scenes/             # satu komponen per layout (Title, List, Stat, ...)
     lib/theme.ts        # warna, font, helper animasi
   public/               # gambar, audio
   ```

3. **Tulis komponen** dengan aturan di bawah, satu layout per file, dipakai ulang oleh banyak scene. Mengulang beberapa layout dengan konsisten lebih baik daripada membuat komponen unik per scene.

4. **Berikan perintah preview dan render**:
   ```bash
   npx remotion studio
   npx remotion render NamaComposition out/video.mp4
   npx remotion still NamaComposition --frame=30 out/cek.png   # cek satu frame
   ```

5. Akhiri dengan ringkasan: file apa yang dibuat, cara menjalankan, dan "Setelah render, lanjut ke review & export?"

## Aturan teknis (alasannya penting)

- **Animasi hanya dari frame.** Pakai `useCurrentFrame`, `useVideoConfig`, `interpolate`, `spring`. Gunakan `extrapolateRight: 'clamp'` agar nilai tidak melewati batas.
- **Durasi dalam detik dikonversi ke frame**: `Math.round(sec * fps)`. Jangan hardcode frame tanpa fps.
- **Komposisi**: `<Composition id width height fps durationInFrames component />`. Total durasi dihitung dari jumlah scene (dan dikurangi overlap transisi bila memakai TransitionSeries).
- **Susunan scene**: `<Series>` untuk berurutan tanpa transisi; `@remotion/transitions` (`TransitionSeries`, `fade()`, `slide()`) bila ada transisi. Di dalam `<Series.Sequence>` frame dimulai lagi dari 0, jadi animasi per scene ditulis relatif terhadap awal scene.
- **Aset**: letakkan di `public/` dan panggil dengan `staticFile('nama.png')`; pakai `<Img>` dan `<Audio>` dari `remotion`, bukan `<img>`/`<audio>`, agar Remotion menunggu aset termuat sebelum render.
- **Font**: gunakan `@remotion/google-fonts/NamaFont` (`loadFont()`), agar font siap sebelum frame dirender.
- **Layout aman untuk 9:16**: sisakan margin ±8% atas-bawah dari UI platform (caption, tombol). Teks heading minimal ±72px di 1080 lebar.
- **Hindari** `Math.random()` tanpa seed (hasil beda tiap render); pakai `random('seed')` dari Remotion.
- **Props dari data**: definisikan tipe TypeScript untuk scene, dan baca scenes.json lewat import, supaya mengubah isi video cukup dengan mengedit JSON.
- **Kode jalan, bukan sketsa**: jangan tinggalkan placeholder `...`. Jika aset belum ada, pakai blok warna atau teks pengganti agar video tetap bisa dirender.

## Batasan yang harus disampaikan jujur
Claude tidak bisa menjalankan Remotion Studio atau melihat hasil video di chat ini. Katakan bahwa kode belum diuji render, minta user menjalankan `npm run dev`, dan minta pesan error atau deskripsi/screenshot bila ada yang janggal.
Jika user minta pembuatan voice over, jelaskan bahwa itu dibuat terpisah (rekam sendiri atau TTS) lalu file audionya ditaruh di `public/`.
