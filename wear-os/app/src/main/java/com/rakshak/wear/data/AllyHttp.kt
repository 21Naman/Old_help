package com.rakshak.wear.data

import android.util.Log
import com.rakshak.wear.BuildConfig
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * HTTP client for the Ally API (`POST /ally/watch`). The watch authenticates with a device key
 * (stored in SSM on the server, `ally.deviceKey` in local.properties here).
 */
class AllyHttp(
    private val origin: String = BuildConfig.ALLY_API,
    private val deviceKey: String = BuildConfig.ALLY_DEVICE_KEY,
) {
    private val tag = "AllyHttp"
    private val http = OkHttpClient.Builder()
        .connectTimeout(8, TimeUnit.SECONDS)
        .readTimeout(20, TimeUnit.SECONDS)
        .build()

    /** kind: wake | activity | im_okay. Null readings are omitted rather than sent as zero. */
    fun postWatch(kind: String, steps: Int? = null, heartRate: Int? = null): Boolean {
        val json = JSONObject().put("kind", kind)
        steps?.takeIf { it > 0 }?.let { json.put("steps", it) }
        heartRate?.takeIf { it in 20..250 }?.let { json.put("heart_rate", it) }
        return post("/ally/watch", json.toString())
    }

    fun imOkay(): Boolean = postWatch("im_okay")

    /** Any device event with extra fields (getup_ref, getup_sample, drop). Null values are left out. */
    fun postEvent(kind: String, fields: Map<String, Any?>): Boolean {
        val json = JSONObject().put("kind", kind)
        for ((k, v) in fields) if (v != null) json.put(k, v)
        return post("/ally/watch", json.toString())
    }

    // ---- the fall conversation on the watch (device key) -------------------------------------

    /** Report a fall; the reply carries the spoken question (`say` + `audio_base64`). */
    fun deviceFall(): JSONObject? = call("POST", "/ally/device/fall", "{}")

    /** Her recorded answer (16 kHz PCM16 WAV, base64). Reply: `say`, `audio_base64`, `fall_tier`, `stt_empty`. */
    fun deviceAnswer(wavBase64: String): JSONObject? =
        call("POST", "/ally/device/answer", JSONObject().put("audio_base64", wavBase64).put("mime_type", "audio/wav").toString())

    /** Pending lines for her (stay updates, who is coming), each with audio. */
    fun devicePending(): org.json.JSONArray? = call("GET", "/ally/device/pending", null)?.optJSONArray("messages")

    private fun call(method: String, path: String, json: String?): JSONObject? {
        return try {
            val builder = Request.Builder()
                .url(origin.trimEnd('/') + path)
                .header("X-Ally-Device-Key", deviceKey)
            if (method == "GET") builder.get()
            else builder.post((json ?: "{}").toRequestBody("application/json".toMediaType()))
            http.newCall(builder.build()).execute().use { res ->
                val text = res.body?.string().orEmpty()
                if (!res.isSuccessful) {
                    Log.w(tag, "$method $path failed: HTTP ${res.code}")
                    null
                } else JSONObject(text.ifEmpty { "{}" })
            }
        } catch (e: Exception) {
            Log.w(tag, "$method $path failed", e)
            null
        }
    }

    private fun post(path: String, json: String): Boolean {
        repeat(2) { attempt ->
            try {
                val req = Request.Builder()
                    .url(origin.trimEnd('/') + path)
                    .header("X-Ally-Device-Key", deviceKey)
                    .post(json.toRequestBody("application/json".toMediaType()))
                    .build()
                http.newCall(req).execute().use { res ->
                    if (res.isSuccessful) return true
                    Log.w(tag, "POST $path failed: HTTP ${res.code}")
                    if (res.code in 400..499) return false
                }
            } catch (e: Exception) {
                Log.w(tag, "POST $path attempt ${attempt + 1} failed", e)
            }
        }
        return false
    }
}
