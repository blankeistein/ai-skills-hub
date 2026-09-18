# UI Testing (Compose) — Detail & Contoh

## 1. Setup dasar

```kotlin
class ProfileScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun displaysUserName_whenStateIsSuccess() {
        composeTestRule.setContent {
            ProfileContent(state = ProfileUiState.Success(sampleUser))
        }
        composeTestRule.onNodeWithText(sampleUser.name).assertIsDisplayed()
    }
}
```

Pakai `createComposeRule()` untuk test composable stateless secara terisolasi (paling umum & cepat). Pakai `createAndroidComposeRule<MainActivity>()` hanya kalau butuh Activity/Context asli (misal ada dependency ke `LocalContext` yang tidak bisa di-fake).

## 2. Semantics-based finders — jangan bergantung ke struktur visual

```kotlin
// Baik: cari berdasarkan text atau testTag, tahan terhadap perubahan layout
composeTestRule.onNodeWithText("Kirim").performClick()
composeTestRule.onNodeWithTag("search_field").performTextInput("budi")
composeTestRule.onNodeWithContentDescription("Hapus user").performClick()
```

Tambahkan `Modifier.testTag("search_field")` di composable untuk elemen yang tidak punya text/contentDescription unik.

## 3. Testing user interaction → callback

```kotlin
@Test
fun clickingDeleteButton_invokesOnDeleteCallback() {
    var deletedId: String? = null
    composeTestRule.setContent {
        UserRow(user = sampleUser, onDelete = { deletedId = it })
    }
    composeTestRule.onNodeWithContentDescription("Hapus user").performClick()
    assertEquals(sampleUser.id, deletedId)
}
```

## 4. Testing conditional visibility (loading/error/empty state)

```kotlin
@Test
fun showsLoadingIndicator_whenStateIsLoading() {
    composeTestRule.setContent { ProfileContent(ProfileUiState.Loading) }
    composeTestRule.onNodeWithTag("loading_indicator").assertIsDisplayed()
    composeTestRule.onNodeWithText(sampleUser.name).assertDoesNotExist()
}
```

## 5. Menunggu async/animasi

```kotlin
// Kalau ada delay/animasi, jangan Thread.sleep — gunakan waitUntil
composeTestRule.waitUntil(timeoutMillis = 2_000) {
    composeTestRule.onAllNodesWithText("Berhasil").fetchSemanticsNodes().isNotEmpty()
}
```

`composeTestRule` secara default sudah synchronize dengan Compose's idle state (recomposition, animasi standar) — `waitUntil` hanya dibutuhkan untuk async eksternal (network call asli, delay custom) yang tidak terhubung ke Compose clock.

## 6. LazyColumn — scroll & cek item

```kotlin
composeTestRule.onNodeWithTag("user_list")
    .performScrollToNode(hasText("User ke-50"))
composeTestRule.onNodeWithText("User ke-50").assertIsDisplayed()
```

## 7. Apa yang TIDAK perlu di-UI-test

- Recomposition count / performance — itu ranah `compose-optimizer` skill, bukan correctness test
- Detail visual pixel-perfect (warna exact, padding exact) — lebih cocok pakai Screenshot Testing (Paparazzi/Compose Preview Screenshot Testing) kalau memang dibutuhkan, bukan `ui-test-junit4`
- Logic murni tanpa UI (itu unit test biasa)

## 8. Anti-pattern yang perlu dicek saat review

- 🔴 **Finder berdasarkan index/posisi** (`onAllNodes()[2]`) — rapuh, patah kalau urutan UI berubah. Pakai testTag/text/contentDescription.
- 🔴 **`Thread.sleep()`** untuk menunggu UI update — pakai `waitUntil` atau andalkan auto-sync Compose test rule.
- 🟡 **Test UI mencakup logic bisnis** (misal assert kalkulasi total harga di dalam UI test) — logic itu seharusnya sudah dicover unit test terpisah; UI test cukup pastikan angka yang benar ditampilkan.
- 🟡 **`testTag` dipakai berlebihan** padahal text/contentDescription sudah cukup unik dan lebih dekat ke pengalaman user asli.
- 🟢 **Tidak ada test untuk state kosong/error di layar list** (hanya test state terisi).

## 9. Checklist cepat

- [ ] Test pakai semantics finder (text/testTag/contentDescription), bukan index posisi?
- [ ] Ada test untuk tiap state penting (loading, error, empty, filled)?
- [ ] Interaksi (click, input, scroll) di-test sampai ke efeknya (callback terpanggil / UI berubah), bukan cuma "elemen ada"?
- [ ] `ui-test-manifest` sudah `debugImplementation` (bukan androidTestImplementation)?
