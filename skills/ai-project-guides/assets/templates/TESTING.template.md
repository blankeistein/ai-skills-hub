# Testing - <Nama Projek>

## Menjalankan
```bash
<semua test>
<satu file>
<satu test by name>
<watch / coverage>
```

## Struktur
- Lokasi: `<..>`; penamaan: `<..>`; pola: Arrange-Act-Assert

## Lingkungan
- DB test: <sqlite memory / MySQL / emulator>; fixture/factory: `<..>`
- Layanan eksternal: <stub/emulator/cara>

## Aturan
- Mock: <yang di-mock> ; tidak di-mock: <..>
- Bug fix -> test regresi; fitur baru -> jalur sukses + satu kasus gagal
- Test flaky: <kebijakan>
- Coverage: <ambang bila ada>
