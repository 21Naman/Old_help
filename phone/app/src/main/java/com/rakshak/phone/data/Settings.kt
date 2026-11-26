package com.rakshak.phone.data

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

data class PhoneSettings(
    val apiUrl: String = "",
    val webUrl: String = "",
    val deviceKey: String = "",
) {
    val isComplete: Boolean
        get() = apiUrl.isNotBlank() && deviceKey.isNotBlank()
}

/** API URL, web URL and device key, encrypted at rest. Nothing is compiled into the APK. */
object Settings {
    private const val FILE = "suraksha_secure"
    private const val KEY_API = "api_url"
    private const val KEY_WEB = "web_url"
    private const val KEY_DEVICE = "device_key"

    @Volatile
    private var prefs: SharedPreferences? = null

    private fun prefs(context: Context): SharedPreferences =
        prefs ?: synchronized(this) {
            prefs ?: open(context.applicationContext).also { prefs = it }
        }

    private fun open(context: Context): SharedPreferences {
        fun create(): SharedPreferences {
            val key = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            return EncryptedSharedPreferences.create(
                context,
                FILE,
                key,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
            )
        }
        return try {
            create()
        } catch (e: Exception) {
            // Keystore key lost (e.g. restored backup): start over rather than crash.
            Log.w("Settings", "Encrypted prefs unreadable, resetting", e)
            context.deleteSharedPreferences(FILE)
            create()
        }
    }

    fun load(context: Context): PhoneSettings {
        val p = prefs(context)
        return PhoneSettings(
            apiUrl = p.getString(KEY_API, "").orEmpty(),
            webUrl = p.getString(KEY_WEB, "").orEmpty(),
            deviceKey = p.getString(KEY_DEVICE, "").orEmpty(),
        )
    }

    fun save(context: Context, settings: PhoneSettings) {
        prefs(context).edit()
            .putString(KEY_API, settings.apiUrl.trim().trimEnd('/'))
            .putString(KEY_WEB, settings.webUrl.trim().trimEnd('/'))
            .putString(KEY_DEVICE, settings.deviceKey.trim())
            .apply()
    }
}
