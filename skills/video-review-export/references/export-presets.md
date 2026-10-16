# Preset export

| Platform | Rasio | Resolusi | FPS | Catatan |
|---|---|---|---|---|
| TikTok / Reels / Shorts | 9:16 | 1080x1920 | 30 | Durasi dan batas ukuran dapat berubah; cek aturan platform saat ini |
| YouTube | 16:9 | 1920x1080 | 30 (atau 60 untuk gerak cepat) | MP4, H.264, audio AAC |
| Feed Instagram | 1:1 atau 4:5 | 1080x1080 / 1080x1350 | 30 | |

## Flag Remotion yang umum
- `--codec=h264` (default, paling kompatibel)
- `--crf=18` kualitas tinggi, `--crf=23` seimbang, `--crf=28` file kecil
- `--scale=0.5` render cepat untuk draft
- `--frames=0-90` render sebagian untuk uji
- `--props=./props.json` kirim data berbeda per render (video massal)

Selalu verifikasi batasan durasi dan ukuran file di dokumentasi platform terbaru karena sering berubah.
