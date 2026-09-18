# Setup — Detail & Contoh

## 1. Dependencies (`libs.versions.toml` / `build.gradle.kts`)

```kotlin
// libs.versions.toml
[versions]
junit = "4.13.2"
mockk = "1.13.13"
coroutinesTest = "1.9.0"
turbine = "1.2.0"
truth = "1.4.4"
androidxTestExt = "1.2.1"
composeUiTest = "1.7.5" // match your Compose BOM version

[libraries]
junit = { group = "junit", name = "junit", version.ref = "junit" }
mockk = { group = "io.mockk", name = "mockk", version.ref = "mockk" }
kotlinx-coroutines-test = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-test", version.ref = "coroutinesTest" }
turbine = { group = "app.cash.turbine", name = "turbine", version.ref = "turbine" }
truth = { group = "com.google.truth", name = "truth", version.ref = "truth" }
androidx-test-ext-junit = { group = "androidx.test.ext", name = "junit", version.ref = "androidxTestExt" }
compose-ui-test-junit4 = { group = "androidx.compose.ui", name = "ui-test-junit4" }
compose-ui-test-manifest = { group = "androidx.compose.ui", name = "ui-test-manifest" }
```

```kotlin
// app/build.gradle.kts
dependencies {
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
    testImplementation(libs.kotlinx.coroutines.test)
    testImplementation(libs.turbine)
    testImplementation(libs.truth)

    androidTestImplementation(libs.androidx.test.ext.junit)
    androidTestImplementation(platform("androidx.compose:compose-bom:2024.12.01")) // match app's BOM
    androidTestImplementation(libs.compose.ui.test.junit4)
    debugImplementation(libs.compose.ui.test.manifest) // debug only, needed for test activity
}
```

**Penting:** `ui-test-manifest` harus `debugImplementation`, bukan `androidTestImplementation` — ini menyediakan `ComponentActivity` untuk host Compose test, dan hanya dibutuhkan saat development/testing, bukan di release.

## 2. Folder structure

```
app/src/
  main/java/com/example/app/...
  test/java/com/example/app/...          # unit tests (JVM, cepat, tanpa device/emulator)
    viewmodel/ProfileViewModelTest.kt
    repository/UserRepositoryTest.kt
    usecase/ValidateEmailUseCaseTest.kt
  androidTest/java/com/example/app/...   # instrumented tests (perlu device/emulator)
    ui/ProfileScreenTest.kt
```

Kesalahan umum: menaruh Compose UI test di `src/test/` — ini akan gagal karena UI test butuh Android runtime, wajib di `src/androidTest/`.

## 3. Base test class untuk coroutines (`MainDispatcherRule`)

ViewModel yang pakai `viewModelScope` (yang berjalan di `Dispatchers.Main`) butuh dispatcher di-swap ke test dispatcher, kalau tidak test akan crash karena `Dispatchers.Main` tidak tersedia di unit test JVM.

```kotlin
// src/test/java/.../MainDispatcherRule.kt
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = StandardTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

Pakai di tiap test class ViewModel:
```kotlin
class ProfileViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
    ...
}
```

## 4. Base test class untuk Compose UI test

```kotlin
class ProfileScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()
    // atau createAndroidComposeRule<MainActivity>() kalau butuh Activity context asli
    ...
}
```

## 5. Checklist setup

- [ ] Dependency test sudah dipisah dengan benar (`testImplementation` vs `androidTestImplementation` vs `debugImplementation`)
- [ ] `MainDispatcherRule` (atau setara) tersedia untuk test yang melibatkan `viewModelScope`/coroutines
- [ ] Folder `src/test/` dan `src/androidTest/` sudah sesuai — unit test tidak nyasar ke androidTest atau sebaliknya
- [ ] Versi Compose BOM di test dependency sama dengan yang dipakai di `main`
