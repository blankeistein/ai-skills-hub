# Struktur & Reusability — Detail & Contoh

## 1. Pisahkan UI dari business logic

```kotlin
// Buruk: composable langsung fetch data
@Composable
fun ProfileScreen(userId: String) {
    var user by remember { mutableStateOf<User?>(null) }
    LaunchedEffect(userId) {
        user = api.getUser(userId) // logic data langsung di UI layer
    }
    ...
}
```
```kotlin
// Baik: ViewModel yang urus data, composable cuma render state
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = hiltViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    ProfileContent(state)
}

@Composable
fun ProfileContent(state: ProfileUiState) { /* stateless, mudah di-preview & test */ }
```

## 2. Parameterisasi komponen agar reusable

```kotlin
// Buruk: hardcoded, tidak bisa dipakai ulang
@Composable
fun SubmitButton() {
    Button(onClick = { /* ... */ }) { Text("Kirim") }
}
```
```kotlin
// Baik
@Composable
fun AppButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
) {
    Button(onClick = onClick, modifier = modifier, enabled = enabled) { Text(text) }
}
```

## 3. Selalu sediakan parameter `Modifier = Modifier`

Komponen reusable yang tidak punya parameter `Modifier` tidak bisa diatur layout-nya oleh pemanggil — ini melanggar konvensi resmi Compose API guidelines.

```kotlin
@Composable
fun Card(content: @Composable () -> Unit, modifier: Modifier = Modifier) {
    Surface(modifier = modifier) { content() }
}
```

## 4. Pecah composable besar

Screen function yang isinya ratusan baris dan banyak tanggung jawab (header, list, dialog, bottom sheet semua dalam satu fungsi) sulit dibaca, di-test, dan di-preview sebagian. Pecah jadi composable kecil dengan nama jelas per bagian UI (`ScreenHeader`, `ScreenContent`, `ScreenErrorState`, dst).

## 5. Preview yang mewakili semua state penting

```kotlin
@Preview
@Composable
fun ProfileContentPreview_Loading() { ProfileContent(ProfileUiState.Loading) }

@Preview
@Composable
fun ProfileContentPreview_Error() { ProfileContent(ProfileUiState.Error("...")) }

@Preview
@Composable
fun ProfileContentPreview_Success() { ProfileContent(ProfileUiState.Success(sampleUser)) }
```
Kalau komponen hanya punya satu preview default (atau tidak ada sama sekali) padahal punya banyak state (loading/error/empty/filled), ini layak dicatat sebagai temuan medium/low.

## 6. Checklist cepat saat review struktur

- [ ] Apakah composable stateless (menerima state & callback lewat parameter) sebisa mungkin, dengan stateful wrapper terpisah?
- [ ] Apakah komponen reusable punya parameter `modifier: Modifier = Modifier`?
- [ ] Apakah ada string/warna/ukuran hardcoded yang seharusnya jadi parameter atau diambil dari theme?
- [ ] Apakah fungsi composable terlalu panjang/banyak tanggung jawab dan perlu dipecah?
- [ ] Apakah preview mencakup state-state penting (loading/error/empty/filled)?
