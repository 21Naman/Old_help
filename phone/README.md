# Suraksha phone app

An Android phone app that works as a second sensor next to the Galaxy Watch app (`../wear-os`).
It sends the same events to the same endpoint, `POST {API}/ally/watch`, with
`"source": "phone"`, so it works for parents who don't have a watch. If someone has both, the
server dedupes wake and fall events.

| Event      | When                                                                 |
|------------|----------------------------------------------------------------------|
| `wake`     | First movement after stillness, or the first unlock of the day. Sent once per local day; if it can't be delivered, the next trigger tries again |
| `fall`     | Accelerometer fall/hard-drop pattern (same thresholds as the watch), or the **Help** button |
| `im_okay`  | The **I'm okay** button                                              |
| `activity` | Every 30 min with today's steps (`TYPE_STEP_COUNTER`), when there are any |

Body: `{"kind": "...", "steps"?: 1234, "source": "phone"}`. Header: `X-Ally-Device-Key`.
Each event gets 2 attempts, with no retry on a 4xx. There's no heart rate or SpO2 on the phone.

Detection runs in a foreground service (`health` type) that keeps a persistent notification and
holds a partial wake lock. The service starts again after a reboot or an app update.

## Build prerequisites

- **JDK 17** (AGP 8.7 won't run on JDK 8). On Ubuntu: `sudo apt install openjdk-17-jdk`, then
  `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`.
- **Android SDK** with `platforms;android-35` and `build-tools;35.0.0`. The easiest way is to
  install Android Studio and open `phone/`. With command-line tools only:
  `sdkmanager "platform-tools" "platforms;android-35" "build-tools;35.0.0"`.
- Tell Gradle where the SDK is: `export ANDROID_HOME=$HOME/Android/Sdk`, or copy
  `local.properties.example` to `local.properties` and set `sdk.dir`.

```bash
cd phone
./gradlew :app:assembleDebug
# -> app/build/outputs/apk/debug/app-debug.apk
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

The first build downloads Gradle 8.9 and the dependencies, so it needs internet.

## Pointing it at the API

Nothing is compiled into the APK. On first launch the app opens **Settings**:

- **API URL**: the FastAPI origin, without a path. Examples: `https://<your-render-app>.onrender.com`,
  or `http://192.168.1.20:8002` for a laptop on the same Wi-Fi. Cleartext HTTP is allowed so LAN
  testing works.
- **Web URL**: the Next.js site. **Talk to Suraksha** opens `{WEB_URL}/parent` in the browser.
- **Device key**: the same key the watch uses (the server's device key for this parent).

All three are stored in `EncryptedSharedPreferences`. Settings (gear icon) lets you change them later.

Quick check from a laptop that the server accepts a phone event:

```bash
curl -i -X POST "$API/ally/watch" -H "X-Ally-Device-Key: $KEY" -H 'Content-Type: application/json' -d '{"kind":"im_okay","source":"phone"}'
```

## Permissions

| Permission | Why |
|------------|-----|
| Physical activity (`ACTIVITY_RECOGNITION`, asked at runtime) | Step counter. Android 14+ also requires it before a `health` foreground service can start |
| Notifications (`POST_NOTIFICATIONS`, Android 13+, asked at runtime) | Persistent "looking after you" notification and fall alerts |
| `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_HEALTH`, `WAKE_LOCK` | Keep sensors running with the screen off |
| `RECEIVE_BOOT_COMPLETED` | Restart after reboot (only once settings are saved) |
| `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` | The **Keep running in the background** button in Settings |
| `INTERNET` | Posting events |

On Xiaomi, Oppo, Vivo, Realme and Samsung phones, also turn on **Autostart** and set battery to
**No restrictions** for Suraksha. These phones kill background apps aggressively.

## Layout

```
app/src/main/java/com/rakshak/phone/
  detect/FallDetector.kt   ported verbatim from wear-os
  detect/WakeDetector.kt   ported from wear-os (one Int/Long literal fix)
  detect/StepTracker.kt    TYPE_STEP_COUNTER, persisted daily baseline (survives reboots)
  data/AllyHttp.kt         POST /ally/watch, adds "source": "phone"
  data/Settings.kt         EncryptedSharedPreferences
  data/PhoneStatus.kt      service/UI shared state, once-per-day wake gate, send()
  service/SensorService.kt foreground service: detectors, unlock receiver, 30-min activity
  service/BootReceiver.kt  BOOT_COMPLETED / MY_PACKAGE_REPLACED
  ui/                      Compose Material 3: home + settings
```
