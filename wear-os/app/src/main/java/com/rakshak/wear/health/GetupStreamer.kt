package com.rakshak.wear.health

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.BatteryManager
import android.util.Log
import com.rakshak.wear.data.AllyHttp
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.sqrt

/**
 * After a fall, tell the backend what her body is doing so the Get-Up Vote can check her answer
 * (bible v5 §6 L1/L4).
 *
 * - The barometer runs all the time into a short ring buffer, so we know her wrist pressure just
 *   BEFORE the fall (`getup_ref.p_ref_hpa`, median of the last 10 s).
 * - For [STREAM_MS] after a fall it posts `getup_sample` every [SAMPLE_MS]: latest pressure,
 *   arm-movement variance (so a waving arm isn't read as standing), and step-detector events since
 *   the fall.
 * Missing sensors are simply left out; the backend treats a missing voter as "not up".
 */
class GetupStreamer(
    context: Context,
    private val http: AllyHttp,
    private val scope: CoroutineScope,
) : SensorEventListener {

    private val tag = "SurakshaGetup"
    private val appContext = context.applicationContext
    private val sm = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val pressure: Sensor? = sm.getDefaultSensor(Sensor.TYPE_PRESSURE)
    private val stepDetector: Sensor? = sm.getDefaultSensor(Sensor.TYPE_STEP_DETECTOR)
    private val accel: Sensor? = sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

    private val pressureBuf = ArrayDeque<Pair<Long, Float>>() // (time ms, hPa), last ~15 s
    private val accelBuf = ArrayDeque<Pair<Long, Float>>()    // (time ms, |a|), last ~2 s while streaming
    @Volatile private var stepsSinceFall = 0
    @Volatile private var streaming = false
    private var job: Job? = null

    /** Start the always-on pressure buffer. Cheap: ~1 sample per second. */
    fun start() {
        pressure?.let { sm.registerListener(this, it, 1_000_000) }
            ?: Log.w(tag, "No barometer on this device; height vote will abstain")
    }

    fun stop() {
        sm.unregisterListener(this)
        job?.cancel()
        streaming = false
    }

    /** Called once when the fall detector fires. */
    fun onFall() {
        if (streaming) return
        streaming = true
        stepsSinceFall = 0
        synchronized(accelBuf) { accelBuf.clear() }
        stepDetector?.let { sm.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL) }
        accel?.let { sm.registerListener(this, it, SensorManager.SENSOR_DELAY_GAME) }

        val ref = medianPressure(sinceMs = System.currentTimeMillis() - REF_WINDOW_MS)
        job = scope.launch(Dispatchers.IO) {
            http.postEvent(
                "getup_ref",
                mapOf("p_ref_hpa" to ref, "charging" to isCharging()),
            )
            val end = System.currentTimeMillis() + STREAM_MS
            while (System.currentTimeMillis() < end) {
                delay(SAMPLE_MS)
                http.postEvent(
                    "getup_sample",
                    mapOf(
                        "p_hpa" to latestPressure(),
                        "arm_var" to armVariance(),
                        "steps" to if (stepDetector != null) stepsSinceFall else null,
                    ),
                )
            }
            finishStreaming()
        }
    }

    private fun finishStreaming() {
        stepDetector?.let { sm.unregisterListener(this, it) }
        accel?.let { sm.unregisterListener(this, it) }
        streaming = false
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    override fun onSensorChanged(event: SensorEvent?) {
        event ?: return
        val now = System.currentTimeMillis()
        when (event.sensor.type) {
            Sensor.TYPE_PRESSURE -> synchronized(pressureBuf) {
                pressureBuf.addLast(now to event.values[0])
                while (pressureBuf.isNotEmpty() && now - pressureBuf.first().first > BUF_MS) pressureBuf.removeFirst()
            }
            Sensor.TYPE_STEP_DETECTOR -> if (streaming) stepsSinceFall += 1
            Sensor.TYPE_ACCELEROMETER -> if (streaming) synchronized(accelBuf) {
                val (x, y, z) = Triple(event.values[0], event.values[1], event.values[2])
                accelBuf.addLast(now to sqrt(x * x + y * y + z * z))
                while (accelBuf.isNotEmpty() && now - accelBuf.first().first > SAMPLE_MS) accelBuf.removeFirst()
            }
        }
    }

    private fun medianPressure(sinceMs: Long): Float? = synchronized(pressureBuf) {
        val v = pressureBuf.filter { it.first >= sinceMs }.map { it.second }.sorted()
        if (v.isEmpty()) null else v[v.size / 2]
    }

    private fun latestPressure(): Float? = synchronized(pressureBuf) { pressureBuf.lastOrNull()?.second }

    private fun armVariance(): Float? = synchronized(accelBuf) {
        if (accelBuf.size < 5) return@synchronized null
        val vals = accelBuf.map { it.second }
        val mean = vals.average().toFloat()
        vals.map { (it - mean) * (it - mean) }.average().toFloat()
    }

    private fun isCharging(): Boolean? {
        val status = appContext.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
            ?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: return null
        return status == BatteryManager.BATTERY_STATUS_CHARGING || status == BatteryManager.BATTERY_STATUS_FULL
    }

    companion object {
        private const val BUF_MS = 15_000L
        private const val REF_WINDOW_MS = 10_000L
        private const val SAMPLE_MS = 2_000L
        private const val STREAM_MS = 60_000L
    }
}
