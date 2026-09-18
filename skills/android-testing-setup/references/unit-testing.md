# Unit Testing — Detail & Contoh

## 1. Struktur test — Arrange-Act-Assert / Given-When-Then

```kotlin
@Test
fun `emits error state when repository throws`() = runTest {
    // Arrange (Given)
    val repository = mockk<UserRepository>()
    coEvery { repository.getUser(any()) } throws IOException("network error")
    val viewModel = ProfileViewModel(repository)

    // Act (When)
    viewModel.loadUser("123")

    // Assert (Then)
    assertEquals(ProfileUiState.Error("network error"), viewModel.uiState.value)
}
```

## 2. Testing StateFlow dengan Turbine

```kotlin
@Test
fun `emits loading then success when fetching user`() = runTest {
    val repository = mockk<UserRepository>()
    coEvery { repository.getUser("123") } returns sampleUser
    val viewModel = ProfileViewModel(repository)

    viewModel.uiState.test {
        assertEquals(ProfileUiState.Idle, awaitItem())
        viewModel.loadUser("123")
        assertEquals(ProfileUiState.Loading, awaitItem())
        assertEquals(ProfileUiState.Success(sampleUser), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

Turbine jauh lebih andal daripada `first()`/`toList()` manual untuk Flow, karena eksplisit soal urutan emission dan langsung fail kalau ada emission tak terduga.

## 3. MockK — pola umum

```kotlin
// Mock suspend function
coEvery { repository.getUser("123") } returns sampleUser

// Mock yang throw
coEvery { repository.getUser(any()) } throws IOException()

// Verify pemanggilan
coVerify(exactly = 1) { repository.getUser("123") }

// Relaxed mock (semua fungsi return default value, hindari boilerplate stubbing)
val analytics = mockk<AnalyticsLogger>(relaxed = true)

// Slot untuk capture argument
val slot = slot<User>()
coEvery { repository.saveUser(capture(slot)) } returns Unit
viewModel.save()
assertEquals("123", slot.captured.id)
```

## 4. Fake vs Mock

Untuk dependency dengan logic sederhana (misal in-memory repository), **fake** sering lebih baik daripada mock — lebih mirip perilaku asli dan test tidak terlalu coupled ke detail implementasi pemanggilan.

```kotlin
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<String, User>()
    fun addUser(user: User) { users[user.id] = user }
    override suspend fun getUser(id: String): User =
        users[id] ?: throw NoSuchElementException()
}
```

Gunakan mock (MockK) untuk dependency yang berat/berefek samping (network, database nyata); gunakan fake untuk dependency dengan logic yang bisa disimulasikan sederhana.

## 5. Testing Repository (offline-first pattern)

Untuk repository yang menggabungkan remote + local (misal pattern Class Chatting: Firestore → Room → UI), test yang penting:
- Data lokal (Room) ditampilkan dulu sebagai source of truth sebelum sync
- Data remote yang baru masuk ter-update ke local storage dengan benar
- Error dari remote tidak menghapus data lokal yang sudah ada (graceful degradation)

```kotlin
@Test
fun `returns cached data when remote fetch fails`() = runTest {
    val localDataSource = FakeLocalDataSource().apply { insert(cachedUser) }
    val remoteDataSource = mockk<RemoteDataSource>()
    coEvery { remoteDataSource.fetchUser(any()) } throws IOException()

    val repository = UserRepositoryImpl(localDataSource, remoteDataSource)
    val result = repository.getUser("123")

    assertEquals(cachedUser, result) // fallback ke cache, bukan crash
}
```

## 6. Anti-pattern yang perlu dicek saat review

- 🔴 **Over-mocking**: mock dependency yang sebenarnya value object sederhana (data class) — harusnya langsung dibuat instance-nya, bukan di-mock
- 🔴 **Testing implementation, bukan behavior**: assert bahwa suatu private method dipanggil, alih-alih assert hasil akhirnya (state/output)
- 🔴 **`Thread.sleep()` atau delay manual** untuk "menunggu" coroutine — harus pakai `runTest`/`TestDispatcher`, bukan sleep
- 🟡 **Satu test menguji banyak hal sekaligus** — sulit tahu bagian mana yang gagal; pecah jadi beberapa test dengan nama jelas
- 🟡 **Tidak ada test untuk error/edge case**, hanya happy path
- 🟢 **Nama test tidak deskriptif** (`test1`, `testViewModel`) — sebaiknya menjelaskan skenario & hasil yang diharapkan

## 7. Checklist cepat

- [ ] Setiap state (loading/success/error) di ViewModel punya test?
- [ ] Coroutine di-test dengan `runTest` + `TestDispatcher`, bukan sleep/delay?
- [ ] Flow/StateFlow di-test pakai Turbine, bukan `.value` snapshot tunggal yang bisa miss emission?
- [ ] Dependency berat di-mock, dependency sederhana di-fake?
- [ ] Ada test untuk error case, bukan cuma happy path?
