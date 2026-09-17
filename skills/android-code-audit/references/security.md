# Security — Android Kotlin/Compose

Focused on issues realistic for a typical app team to introduce — not exhaustive pentest-level coverage, but enough to catch the common, costly mistakes.

## 1. Hardcoded secrets

- API keys, tokens, client secrets, or credentials hardcoded directly in Kotlin source, `strings.xml`, or committed `local.properties`/`BuildConfig` fields that end up in the compiled APK (anything in `BuildConfig` is extractable from a release APK — it is **not** a safe place for true secrets, only for non-sensitive build-time config).
- Signing keys, keystore passwords, or `.jks` files committed to the repo.
- Check `build.gradle(.kts)` for keys injected via `buildConfigField` — flag if they look like real secrets vs. genuinely non-sensitive config (e.g., a public base URL is fine; an API secret is not).

## 2. Insecure data storage

- Sensitive data (auth tokens, PII, payment info) stored in plain `SharedPreferences` instead of `EncryptedSharedPreferences` (AndroidX Security library) or the platform `Keystore`.
- Sensitive data written to external storage (`getExternalFilesDir`, or worse, public external storage) without encryption, where it may be readable by other apps or via USB/file managers on older Android versions.
- Sensitive values logged via `Log.d`/`Log.i`/`println` — these persist in logcat and can leak in bug reports or on rooted devices. Flag any logging of tokens, passwords, full PII, or raw API responses containing sensitive fields.
- Room database storing sensitive fields unencrypted with no `SQLCipher`/equivalent, if the data warrants it (evaluate based on what the field actually contains — don't flag every DB as needing encryption).

## 3. Network security

- Cleartext HTTP (`http://`) used for API calls instead of HTTPS, or `usesCleartextTraffic="true"` in the manifest without a narrowly scoped `network_security_config.xml` justifying it.
- Disabled or overly permissive TLS/certificate validation — check for custom `TrustManager`/`HostnameVerifier` implementations that unconditionally trust all certificates (a very common shortcut left in from debugging that's dangerous if it ships to release).
- Missing certificate pinning for apps handling genuinely sensitive data (only flag as worth considering, not a hard requirement for every app).

## 4. Input validation / injection

- Raw SQL string concatenation instead of parameterized queries — check Room usage uses `@Query` with `:param` binding, not string-built queries with interpolated user input.
- `WebView` with `javaScriptEnabled = true` loading untrusted/user-controllable URLs without restriction — potential for JS injection. Check `addJavascriptInterface` usage particularly, since exposed interfaces are a known WebView attack surface pre-API 17 and require care even on modern APIs.
- Deep link / `Intent` handling that trusts extras or URIs from external sources without validation before acting on them (e.g., launching an activity, loading a URL, or executing a command based on unvalidated deep-link data).

## 5. Permissions & exposure

- `exported="true"` on `Activity`/`Service`/`BroadcastReceiver`/`ContentProvider` in the manifest without an `intent-filter` that actually requires it, or without a permission check — unnecessarily exposes components to other apps on the device.
- Requesting overly broad permissions relative to actual feature usage (flag as worth reviewing, since this is often a product decision, not purely a code bug).
- `ContentProvider` exposing more data/URIs than intended, or without proper permission enforcement.

## 6. Authentication & session handling

- Auth tokens with no expiry/refresh handling, or refresh logic that silently fails open (treats an expired/invalid token as valid).
- Biometric/lock-screen authentication implemented in a way that can be bypassed (e.g., the "authenticated" state is a simple boolean settable elsewhere in code, rather than gated properly through the `BiometricPrompt` callback).

## How to search

- Grep for: `http://` (not `https://`), `SharedPreferences`, `Log.d(`, `Log.i(`, `println(`, `TrustManager`, `HostnameVerifier`, `addJavascriptInterface`, `javaScriptEnabled`, `exported="true"`, string-built SQL (`"SELECT.*\$`), any all-caps identifiers assigned literal strings that look like keys/tokens (`API_KEY`, `SECRET`, `TOKEN` followed by `= "..."`).
- Check `AndroidManifest.xml` for every exported component and confirm intentionality.
- Check `network_security_config.xml` existence and contents if cleartext traffic is enabled anywhere.
- Flag findings here as **Critical** by default (per the main severity scale) unless the exposure is clearly low-impact (e.g., a non-sensitive public config value mistakenly called "KEY").
