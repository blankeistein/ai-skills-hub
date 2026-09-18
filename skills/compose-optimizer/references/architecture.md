# Arsitektur — Detail & Contoh

## 1. State hoisting

Aturan dasar: state sebaiknya "dinaikkan" (hoisted) ke level serendah mungkin yang masih menjadi *common ancestor* dari semua composable yang membutuhkannya — tidak lebih tinggi, tidak lebih rendah dari itu.

```kotlin
// Buruk: state dimiliki komponen leaf, sulit dikontrol dari luar / di-test
@Composable
fun SearchBar() {
    var query by remember { mutableStateOf("") }
    TextField(value = query, onValueChange = { query = it })
}
```
```kotlin
// Baik: stateless, state dimiliki oleh pemanggil (screen/ViewModel)
@Composable
fun SearchBar(query: String, onQueryChange: (String) -> Unit) {
    TextField(value = query, onValueChange = onQueryChange)
}
```

Tanda state hoisting kurang tepat: sebuah komponen kecil menyimpan `remember { mutableStateOf(...) }` untuk data yang ternyata juga dibutuhkan komponen sibling atau parent-nya — biasanya berujung workaround aneh (callback berantai, event bus) padahal solusinya cukup naikkan state satu level.

## 2. ViewModel — tanggung jawab yang tepat

- ViewModel **tidak boleh** memegang referensi ke `Context` yang bisa leak (`Activity`, `View`), termasuk lewat composable `LocalContext` yang diteruskan ke ViewModel.
- ViewModel mengeluarkan UI state via `StateFlow`/`State`, bukan tipe data-layer mentah.
- UI (composable) tidak boleh memanggil repository/data source langsung — semua lewat ViewModel.

```kotlin
// Buruk
@Composable
fun Screen() {
    val repo = remember { UserRepository() } // UI layer instantiate data layer langsung
}
```
```kotlin
// Baik
@Composable
fun Screen(viewModel: ScreenViewModel = hiltViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
}
```

## 3. Side-effect API yang tepat

| API | Kapan dipakai |
|---|---|
| `LaunchedEffect(key)` | Menjalankan suspend function saat masuk komposisi / saat `key` berubah |
| `DisposableEffect(key)` | Perlu cleanup eksplisit saat composable keluar dari komposisi (listener, observer) |
| `SideEffect` | Publish state Compose ke objek non-Compose setiap recomposition sukses |
| `rememberCoroutineScope` | Meluncurkan coroutine dari event handler (bukan langsung di body composable) |
| `derivedStateOf` | State turunan dari state lain, bukan side effect sebenarnya |

**Kesalahan umum:** `LaunchedEffect(Unit)` dipakai padahal seharusnya bereaksi ke perubahan parameter tertentu (key salah → efek tidak jalan ulang saat data berubah), atau sebaliknya key terlalu sering berubah sehingga efek re-run berlebihan.

```kotlin
// Buruk: efek tidak akan re-run saat userId berubah
LaunchedEffect(Unit) {
    viewModel.loadUser(userId)
}
```
```kotlin
// Baik
LaunchedEffect(userId) {
    viewModel.loadUser(userId)
}
```

## 4. Single source of truth

Hindari duplikasi state — misal ViewModel punya `StateFlow<String> query` tapi composable juga punya `remember { mutableStateOf("") }` terpisah untuk hal yang sama. Ini menyebabkan dua sumber kebenaran yang bisa out-of-sync.

## 5. Navigasi

Logic navigasi (memutuskan layar mana yang dituju) sebaiknya tidak ditulis langsung di dalam composable UI — lebih baik composable memanggil callback (`onNavigateToDetail: (String) -> Unit`) yang diteruskan dari level yang memegang `NavController`.

## 6. Checklist cepat saat review arsitektur

- [ ] Apakah state berada di level yang tepat (tidak terlalu rendah/tinggi dari yang membutuhkannya)?
- [ ] Apakah ViewModel bebas dari referensi UI (Context/View) dan composable bebas dari akses data layer langsung?
- [ ] Apakah `LaunchedEffect`/`DisposableEffect` pakai key yang benar?
- [ ] Apakah ada duplikasi state antara ViewModel dan local `remember`?
- [ ] Apakah navigasi di-hoist lewat callback, bukan ditulis langsung di composable?
