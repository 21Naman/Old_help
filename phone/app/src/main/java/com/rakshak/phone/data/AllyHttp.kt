package com.rakshak.phone.data

import android.util.Log
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * HTTP client for the Ally API (`POST /ally/watch`), ported from the watch app. The phone posts
 * the same events as the watch, tagged `"source": "phone"` so the server can dedupe them.
 */
class AllyHttp(
    private val origin: String,
    private val deviceKey: String,
) {
    private val tag = "AllyHttp"

    /** kind: wake | fall | im_okay | activity. Null readings are omitted rather than sent as zero. */
    fun postWatch(kind: String, steps: Int? = null): Boolean {
        val json = JSONObject()
            .put("kind", kind)
            .put("source", "phone")
        steps?.takeIf { it > 0 }?.let { json.put("steps", it) }
        return post("/ally/watch", json.toString())
    }

    private fun post(path: String, json: String): Boolean {
        if (origin.isBlank()) {
            Log.w(tag, "No API URL set; dropping POST $path")
            return false
        }
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

    companion object {
        private val http = OkHttpClient.Builder()
            .connectTimeout(8, TimeUnit.SECONDS)
            .readTimeout(20, TimeUnit.SECONDS)
            .build()
    }
}
