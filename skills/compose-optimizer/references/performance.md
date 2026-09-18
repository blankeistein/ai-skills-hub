# Performance — Detail & Contoh

## 1. Stability & Skippability

Compose bisa skip recomposition sebuah composable kalau semua parameternya stabil dan sama dengan komposisi sebelumnya. Tipe dianggap stabil jika:
- Primitif (`Int`, `String`, `Boolean`, dll)
- `data class` dengan semua properti stabil dan `val` (bukan `var`)
- Collection immutable (`ImmutableList`, `PersistentList` dari `kotlinx.collections.immutable`) — **bukan** `List`/`Map` biasa, yang dianggap unstable oleh compiler karena bisa berupa `MutableList`.

**Masalah umum:**
```kotlin
@Composable
fun UserList(users: List<User>) { ... } // List<User> = unstable, komponen ini akan selalu re-compose
```

**Fix:**
```kotlin
// Gunakan ImmutableList, atau tandai eksplisit
@Composable
fun UserList(users: ImmutableList<User>) { ... }
```

Jika tidak bisa ganti dependency, cek dulu dengan Compose Compiler Metrics (`./gradlew assembleRelease -PcomposeCompilerReports=true`) untuk melihat class mana yang ditandai unstable sebelum menyarankan perubahan besar.

## 2. Lambda & object literal inline

```kotlin
// Buruk: lambda baru dibuat tiap recomposition, merusak stability parameter
Button(onClick = { viewModel.onClick(item.id) }) { Text("Click") }
```
Ini sebenarnya sering tidak masalah untuk lambda sederhana (Compose compiler bisa memoize lambda tanpa capture berubah), tapi jadi masalah ketika lambda meng-capture nilai yang berubah tiap recomposition atau dipakai di dalam list besar. Untuk kasus itu:
```kotlin
val onItemClick = remember(viewModel) { { id: String -> viewModel.onClick(id) } }
```

## 3. `remember` untuk kalkulasi berat

```kotlin
// Buruk: filter dijalankan tiap recomposition
@Composable
fun FilteredList(items: List<Item>, query: String) {
    val filtered = items.filter { it.name.contains(query) }
    ...
}
```
```kotlin
// Baik
val filtered = remember(items, query) {
    items.filter { it.name.contains(query) }
}
```

## 4. `derivedStateOf` untuk state turunan yang sering berubah

Dipakai ketika sebuah state (misal hasil scroll) berubah lebih sering daripada nilai yang benar-benar dibutuhkan UI, untuk menghindari recomposition berlebihan.

```kotlin
val showButton by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }
}
```
Bukan:
```kotlin
val showButton = listState.firstVisibleItemIndex > 0 // recompose tiap scroll pixel
```

## 5. `key` di `LazyColumn`/`LazyRow`

```kotlin
// Buruk: tanpa key, Compose sulit tahu item mana yang berubah/pindah posisi
LazyColumn {
    items(users) { user -> UserRow(user) }
}
```
```kotlin
// Baik
LazyColumn {
    items(users, key = { it.id }) { user -> UserRow(user) }
}
```

## 6. Scope recomposition — pisahkan state ke composable terkecil

```kotlin
// Buruk: seluruh screen recompose tiap ketikan di search box
@Composable
fun Screen() {
    var query by remember { mutableStateOf("") }
    Column {
        SearchBar(query, onQueryChange = { query = it })
        ExpensiveContent() // ikut recompose padahal tidak butuh `query`
    }
}
```
```kotlin
// Baik: pisahkan jadi composable sendiri agar scope recomposition mengecil
@Composable
fun Screen() {
    Column {
        SearchBarSection()
        ExpensiveContent()
    }
}

@Composable
fun SearchBarSection() {
    var query by remember { mutableStateOf("") }
    SearchBar(query, onQueryChange = { query = it })
}
```

## 7. Checklist cepat saat review performance

- [ ] Apakah parameter composable pakai tipe stabil (hindari `List`/`Map` polos di API publik komponen)?
- [ ] Apakah ada kalkulasi berat di body composable tanpa `remember`?
- [ ] Apakah `LazyColumn`/`LazyRow` punya `key`?
- [ ] Apakah ada state yang scope-nya terlalu tinggi sehingga memicu recomposition komponen yang tidak perlu?
- [ ] Apakah `derivedStateOf` dipakai di tempat yang tepat (state turunan berubah lebih sering dari yang dibutuhkan UI)?
- [ ] Apakah ada `Modifier` yang dibangun ulang dengan input tak stabil tiap recomposition?
