# Skema scenes.json

Kontrak antara storyboard dan Remotion. Jaga tetap sederhana.

```json
{
  "meta": { "title": "Kenapa Gaji Cepat Habis", "width": 1080, "height": 1920, "fps": 30 },
  "theme": {
    "bg": "#0F172A", "text": "#F8FAFC", "accent": "#38BDF8",
    "fontHeading": "Poppins", "fontBody": "Inter", "motion": "spring-pop"
  },
  "audio": { "voiceover": "vo.mp3", "music": "bgm.mp3", "musicVolume": 0.15 },
  "scenes": [
    {
      "id": "hook",
      "durationSec": 3,
      "layout": "title",
      "text": "Gajian selalu habis tanggal 15?",
      "subtext": null,
      "image": null,
      "animation": "pop-in",
      "transition": "none",
      "narration": "Kenapa gajian selalu habis tanggal lima belas?"
    }
  ]
}
```

## `layout`
`title` (teks besar tengah), `list` (poin bertahap), `image-caption` (gambar + teks), `stat` (angka besar + label), `quote`, `outro` (CTA).

## `animation`
`pop-in` (spring scale), `fade-up`, `slide-left`, `typewriter`, `word-by-word`.

## `transition`
`none`, `fade`, `slide`, `wipe`.

Aturan: `durasiFrame = durationSec * fps`. Total semua scene harus mendekati durasi naskah. Aset gambar/audio dirujuk lewat nama file di folder `public/`. Field audio dan image boleh null/dihilangkan.
