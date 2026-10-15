# DESIGN.md - <Nama Produk>

> Sumber kebenaran bahasa visual. Token didefinisikan di `<path file token>`; dokumen ini menjelaskan peran dan aturannya.

## 1. Ringkasan & prinsip
- **Pengguna**: <siapa, perangkat, konteks>
- **Kepribadian**: <mis. ramah, tenang, jelas>
- **Prinsip**: 1) <...> 2) <...> 3) <...>

## 2. Warna

| Token | Light | Dark | Peran |
|---|---|---|---|
| `primary` | `#------` | `#------` | Aksi utama, tautan, fokus |
| `on-primary` | `#------` | `#------` | Teks/ikon di atas primary |
| `surface` | `#------` | `#------` | Latar kartu/sheet |
| `background` | `#------` | `#------` | Latar halaman |
| `text` / `text-muted` | `#------` | `#------` | Teks utama / sekunder |
| `border` | `#------` | `#------` | Garis pemisah |
| `success` `warning` `danger` `info` | ... | ... | Status semantik |

Aturan: <maks 1 aksen per layar>; warna bukan satu-satunya penanda status; kontras tervalidasi ≥ 4.5:1.

## 3. Tipografi
- Font: `<Nama>`, fallback `<stack>`; dimuat via `<cara>`

| Peran | Ukuran/line-height | Bobot | Pemakaian |
|---|---|---|---|
| Display | | | |
| Heading | | | |
| Body | | | |
| Caption | | | |

## 4. Spasi & layout
- Skala: `4, 8, 12, 16, 24, 32, 48`; padding halaman `<..>`, padding kartu `<..>`
- Breakpoint / ukuran layar: <...>; lebar konten maks `<..>`
- Safe area & kepadatan: <...>

## 5. Bentuk, elevasi, border
- Radius: `sm <..> / md <..> / lg <..> / full`
- Elevasi: level 0-3 dan kapan dipakai
- z-index: dropdown < sticky < modal < toast

## 6. Komponen

### <Button> - `<path>`
- Varian: primary / secondary / ghost / destructive; ukuran: sm / md / lg
- State: default, hover, focus, active, disabled, loading
- Aturan: maks satu primary per area; label berupa kata kerja
- Jangan: membuat varian baru tanpa persetujuan

(Ulangi untuk Input, Card, Dialog, Tabs, Table, Toast, Badge, Nav - hanya yang ada.)

## 7. Pola & alur
- **Form**: validasi saat blur, pesan di bawah field
- **Empty state**: ilustrasi + 1 kalimat + 1 aksi
- **Loading**: <skeleton/spinner, kapan>
- **Error**: apa yang terjadi + cara memperbaiki + coba lagi
- **Konfirmasi aksi destruktif**: <pola>

## 8. Ikon & gambar
- Library: `<nama>`; ukuran 16/20/24; gaya <outline/filled>
- Ikon dekoratif disembunyikan dari pembaca layar; ikon informatif diberi label

## 9. Gerak
- Durasi 120-150 / 200-250 / 300-400 ms; easing `<..>`
- Hanya animasikan transform/opacity; hormati reduced motion

## 10. Aksesibilitas
- Kontras AA; fokus terlihat; target sentuh ≥ 44pt/48dp; alt/contentDescription; tidak mengandalkan warna saja

## 11. Suara & salinan
- Bahasa: <Indonesia sehari-hari>; kata ganti: <Anda/kamu>
- Istilah baku: <...>; format tanggal/angka: `<contoh>`
- Pola pesan error: <contoh>

## 12. Do & Don't
- Do: <pakai komponen X>. Don't: <nilai mentah / elemen native yang diberi gaya manual>.

## 13. Implementasi
- Token: `<path>`; tambah token baru: <langkah>
- Katalog komponen: `<storybook/preview>`; perintah: `<..>`
