package com.rakshak.phone.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import java.time.LocalDate

data class SentEvent(val kind: String, val atMillis: Long, val delivered: Boolean)

/** Shared state between the service and the UI, plus the single path for sending events. */
object PhoneStatus {
    private const val FILE = "status"

    private val _serviceRunning = MutableStateFlow(false)
    val serviceRunning: StateFlow<Boolean> = _serviceRunning.asStateFlow()

    private val _lastEvent = MutableStateFlow<SentEvent?>(null)
    val lastEvent: StateFlow<SentEvent?> = _lastEvent.asStateFlow()

    @Volatile
    private var loaded = false

    fun load(context: Context) {
        if (loaded) return
        val p = context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
        val kind = p.getString("last_kind", null)
        if (kind != null) {
            _lastEvent.value = SentEvent(kind, p.getLong("last_at", 0L), p.getBoolean("last_ok", false))
        }
        loaded = true
    }

    fun setServiceRunning(running: Boolean) {
        _serviceRunning.value = running
    }

    /**
     * True the first time it is called on a given local day. Shared by the motion detector and
     * the unlock receiver so the phone sends at most one wake per day.
     */
    @Synchronized
    fun claimWakeToday(context: Context): Boolean {
        val p = context.getSharedPreferences(FILE, Context.MODE_PRIVATE)
        val today = LocalDate.now().toString()
        if (p.getString("wake_date", null) == today) return false
        p.edit().putString("wake_date", today).apply()
        return true
    }

    /** Undo [claimWakeToday] when the wake could not be delivered, so the next trigger retries. */
    @Synchronized
    fun releaseWake(context: Context) {
        context.getSharedPreferences(FILE, Context.MODE_PRIVATE).edit().remove("wake_date").apply()
    }

    /** POST one event to `/ally/watch` with the saved settings and record the outcome. */
    suspend fun send(context: Context, kind: String, steps: Int? = null): Boolean =
        withContext(Dispatchers.IO) {
            val s = Settings.load(context)
            val ok = AllyHttp(s.apiUrl, s.deviceKey).postWatch(kind, steps)
            val event = SentEvent(kind, System.currentTimeMillis(), ok)
            _lastEvent.value = event
            context.getSharedPreferences(FILE, Context.MODE_PRIVATE).edit()
                .putString("last_kind", event.kind)
                .putLong("last_at", event.atMillis)
                .putBoolean("last_ok", event.delivered)
                .apply()
            ok
        }
}
