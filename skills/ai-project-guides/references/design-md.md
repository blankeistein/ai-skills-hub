# Panduan menulis DESIGN.md

Daftar isi: [Tujuan](#tujuan) · [Sumber data](#sumber-data) · [Struktur](#struktur) · [Detail bagian](#detail-bagian) · [Terjemahan ke kode](#terjemahan-token-ke-kode) · [Aksesibilitas](#checklist-aksesibilitas) · [Anti-pola](#anti-pola) · [Jika belum ada desain](#jika-belum-ada-desain)

## Tujuan

DESIGN.md adalah sumber kebenaran **bahasa visual dan perilaku UI** yang bisa dibaca agent. Tujuannya agar UI yang dihasilkan AI terasa konsisten dengan produk: warna yang benar, spasi yang benar, komponen yang sudah ada dipakai ulang, dan tidak muncul gaya "default AI" yang generik.

Tanpa DESIGN.md, agent cenderung: memakai warna acak, membuat komponen baru padahal sudah ada, mencampur skala spasi, dan melupakan state (loading, kosong, error).

Prinsip:
- **Token dulu, deskripsi kemudian.** Nilai eksak (hex, px/rem/dp, ms) yang bisa disalin lebih berguna daripada kata sifat ("warna biru yang hangat").
- **Beri peran, bukan hanya nilai.** `primary #2563EB - aksi utama, tautan` lebih berguna daripada `blue-600 #2563EB`.
- **Tunjuk kode.** Setiap token dan komponen harus ditautkan ke tempat ia hidup di kode (`tailwind.config.ts`, `theme/Color.kt`, `components/ui/Button.tsx`).
- **Sertakan alasan dan batas.** Kapan dipakai, kapan tidak.
- **Jangan duplikasi Figma/Storybook.** Rujuk, dan catat sumber mana yang menang bila berbeda.

## Sumber data

Urutan pencarian fakta (jalankan `scripts/extract_design_tokens.py` dulu):
1. Konfigurasi tema: `tailwind.config.*`, `theme.ts`, CSS variables di `:root`, `tokens.json`, `Color.kt`/`Type.kt`/`Theme.kt` (Compose), `colors.xml`/`themes.xml`, Flutter `ThemeData`.
2. Komponen dasar yang sudah ada (`components/ui`, `design-system/`, `core/designsystem`).
3. Layar/halaman representatif (ambil 2-3) untuk melihat pola tata letak nyata.
4. Aset: logo, ikon, font yang di-bundle.
5. Tanya user: brand, nada, referensi gaya, hal yang tidak disukai, target perangkat, dukungan dark mode.

Jika kode dan keinginan user berbeda, tulis keduanya: "Saat ini: X (kode). Target: Y (arah desain)" dan tandai migrasi.

## Struktur

```
# DESIGN.md - <Nama Produk>
## 1. Ringkasan & prinsip desain        ← kepribadian produk, 3-5 prinsip, audiens
## 2. Warna                              ← palet, peran semantik, dark mode, kontras
## 3. Tipografi                          ← keluarga font, skala, bobot, line-height
## 4. Spasi, layout & grid               ← skala spasi, breakpoint, kontainer, safe area
## 5. Bentuk, elevasi & border           ← radius, shadow, border, z-index
## 6. Komponen                           ← inventaris + varian + state + aturan pakai
## 7. Pola & alur                        ← form, navigasi, tabel/list, empty/loading/error
## 8. Ikon, ilustrasi & gambar           ← set ikon, ukuran, gaya, aturan aset
## 9. Gerak & interaksi                  ← durasi, easing, kapan dianimasikan, reduced motion
## 10. Aksesibilitas                     ← kontras, fokus, target sentuh, label, bahasa
## 11. Suara & salinan (copywriting)     ← nada, istilah baku, pola pesan error, bahasa
## 12. Do & Don't                        ← kesalahan visual yang sering terjadi
## 13. Implementasi                      ← file token, cara menambah token/komponen, tool
```

Hilangkan bagian yang tidak relevan (backend-only tidak perlu DESIGN.md sama sekali; app mobile tidak perlu breakpoint web).

## Detail bagian

### 1. Ringkasan & prinsip
Sebutkan siapa penggunanya (mis. siswa SD di perangkat Android murah; admin sekolah di desktop), perasaan yang ditargetkan (ramah, tenang, tegas), dan 3-5 prinsip yang bisa dipakai memutuskan sengketa: "Kejelasan di atas dekorasi", "Satu aksi utama per layar", "Semua teks dalam Bahasa Indonesia sehari-hari".

### 2. Warna
Tabel token dengan peran:

| Token | Light | Dark | Peran |
|---|---|---|---|
| `--color-primary` | `#2563EB` | `#60A5FA` | Aksi utama, tautan, fokus |
| `--color-on-primary` | `#FFFFFF` | `#0B1220` | Teks/ikon di atas primary |
| `--color-surface` | `#FFFFFF` | `#0F172A` | Latar kartu/sheet |
| `--color-danger` | `#DC2626` | `#F87171` | Error, aksi destruktif |

Sertakan: warna semantik (success/warning/danger/info), warna netral (abu bertingkat), aturan penggunaan (maks 1 warna aksen per layar, warna tidak boleh jadi satu-satunya penanda status), dan pasangan kontras yang sudah divalidasi (rasio WCAG). Jangan tulis warna di luar daftar langsung di komponen.

### 3. Tipografi
Keluarga font + fallback, cara memuatnya (self-host/Google Fonts/bundle), skala:

| Peran | Ukuran / line-height | Bobot | Pemakaian |
|---|---|---|---|
| Display | 32/40 | 700 | Judul hero |
| Heading | 20/28 | 600 | Judul bagian |
| Body | 16/24 | 400 | Teks utama |
| Caption | 12/16 | 400 | Keterangan, label tabel |

Aturan: panjang baris maksimum (60-75 karakter), unit (rem/sp), cara menangani teks panjang dan angka (tabular figures), dukungan teks yang diperbesar sistem.

### 4. Spasi & layout
Skala tunggal (mis. 4-pt: 4, 8, 12, 16, 24, 32, 48), padding standar kartu/halaman, breakpoint (web), lebar maksimum konten, grid kolom, safe area (mobile), kepadatan (compact vs comfortable).

### 5. Bentuk, elevasi, border
Skala radius (`sm 6 / md 10 / lg 16 / full`), tingkat bayangan (0-3) dan kapan dipakai, ketebalan & warna border, urutan z-index (dropdown < sticky < modal < toast).

### 6. Komponen
Untuk setiap komponen inti (Button, Input, Select, Card, Modal/Dialog, Tabs, Table, Toast, Badge, Avatar, Navbar/BottomBar):
- **Lokasi kode** dan API props singkat
- **Varian** (primary/secondary/ghost/destructive) dan **ukuran**
- **State**: default, hover, focus, active, disabled, loading, error
- **Aturan pakai**: maksimal satu tombol primary per area, label berupa kata kerja, kapan memakai Dialog vs halaman baru
- **Jangan**: membuat varian baru tanpa persetujuan; gunakan komponen yang ada

Format ringkas per komponen cukup 4-8 baris. Inventaris yang tidak dipakai jangan ditulis.

### 7. Pola & alur
Pola berulang yang membuat produk terasa konsisten: validasi form (inline saat blur, pesan di bawah field), konfirmasi aksi destruktif, pola list/pencarian/filter/paginasi, **empty state** (ilustrasi + 1 kalimat + 1 aksi), **loading** (skeleton vs spinner), **error** (apa yang terjadi + cara memperbaiki + coba lagi), offline.

### 8. Ikon & gambar
Library ikon dan ukuran baku (16/20/24), gaya (outline vs filled), warna mengikuti teks, ikon dekoratif vs informatif (`aria-hidden`/`contentDescription`), format gambar, rasio, lazy loading, alt text.

### 9. Gerak
Durasi (cepat 120-150ms, sedang 200-250ms, lambat 300-400ms), easing baku, hal yang boleh dianimasikan (transform/opacity), hormati `prefers-reduced-motion` / pengaturan animasi OS, hindari gerak yang menghambat tugas.

### 10. Aksesibilitas
Lihat checklist di bawah; tulis sebagai standar minimum produk.

### 11. Suara & salinan
Nada (ramah-formal?), kata ganti ("Anda" vs "kamu"), istilah baku produk (selalu "Ujian", bukan "Tes"/"Quiz"), format tanggal/angka/mata uang (`15 Okt 2026`, `Rp1.250.000`), pola pesan error, kapitalisasi tombol.

### 12. Do & Don't
Pasangan singkat yang menangkap kesalahan nyata:
- Do: pakai `Button variant="primary"` dari `components/ui`. Don't: `<button class="bg-blue-500 ...">`.
- Do: spasi dari skala. Don't: `margin: 13px`.

### 13. Implementasi
Di mana token didefinisikan, cara menambah token baru, cara menambah komponen (pakai Storybook? generator?), tool visual regression, dan perintah terkait (`npm run storybook`).

## Terjemahan token ke kode

Tulis token sekali, lalu tunjukkan pemetaannya pada stack yang dipakai:

**CSS variables / Tailwind**
```css
:root { --color-primary: #2563EB; --radius-md: 10px; }
.dark { --color-primary: #60A5FA; }
```
```ts
// tailwind.config.ts
theme: { extend: { colors: { primary: 'var(--color-primary)' }, borderRadius: { md: 'var(--radius-md)' } } }
```

**Jetpack Compose**
```kotlin
// ui/theme/Color.kt
val Primary = Color(0xFF2563EB)
// ui/theme/Theme.kt -> lightColorScheme(primary = Primary, ...)
// Pakai MaterialTheme.colorScheme.primary, bukan Color(0xFF...) langsung di composable.
```

**Android XML**: `res/values/colors.xml` + `themes.xml`, rujuk `?attr/colorPrimary`.

Aturan umum: komponen membaca **token semantik** (`primary`, `surface`), bukan nilai mentah atau nama palet (`blue-600`).

## Checklist aksesibilitas

- Kontras teks normal ≥ 4.5:1, teks besar & ikon penting ≥ 3:1 (WCAG AA)
- Indikator fokus terlihat di semua elemen interaktif; urutan tab logis
- Target sentuh minimal 44x44 pt (iOS) / 48x48 dp (Android); jarak antar target memadai
- Semua gambar informatif punya alt/`contentDescription`; ikon-tombol punya label
- Tidak mengandalkan warna saja untuk makna (tambah ikon/teks)
- Form: label terhubung ke input, error dibacakan, tipe input/keyboard yang tepat
- Mendukung teks diperbesar tanpa kehilangan konten; menghormati reduced motion
- Atribut bahasa (`lang="id"`) benar; teks tidak ditanam di dalam gambar
- Uji dengan keyboard saja dan pembaca layar (TalkBack/VoiceOver) untuk alur utama

## Anti-pola

| Anti-pola | Akibat |
|---|---|
| Hanya kata sifat ("modern, bersih, ramah") | Agent menebak; hasil generik |
| Menyalin seluruh palet Tailwind | Konteks boros, tidak ada panduan pemilihan |
| Token tanpa lokasi kode | Agent membuat token duplikat |
| Tidak mendokumentasikan state | UI tanpa loading/empty/error |
| Mendeskripsikan desain yang tidak ada di kode | Agent membangun ulang alih-alih memakai ulang |
| Aturan estetika subjektif tanpa contoh | Tidak bisa ditegakkan |

## Jika belum ada desain

Jika projek belum punya sistem desain, jangan mengarang identitas brand diam-diam. Pilihan:
1. **Dokumentasikan yang ada** dari kode (hasil `extract_design_tokens.py`) dan tandai inkonsistensi sebagai "Perlu dirapikan".
2. **Usulkan fondasi minimal** (1 warna primer + netral + semantik, 1 font, skala spasi 4-pt, radius, 6 komponen inti) dan label sebagai **Usulan**; minta persetujuan user.
3. Sertakan 2-3 pertanyaan terbuka (warna brand? dark mode? referensi aplikasi yang disukai?).
