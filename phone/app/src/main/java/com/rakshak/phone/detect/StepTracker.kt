package com.rakshak.phone.detect

import android.content.Context
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.util.Log
import java.time.LocalDate

/**
 * Today's step count from [Sensor.TYPE_STEP_COUNTER], which only reports steps since boot.
 * A per-day baseline is persisted so the count survives service restarts and reboots.
 * Requires ACTIVITY_RECOGNITION (API 29+).
 */
class StepTracker(context: Context) : SensorEventListener {

    private val sensorManager =
        context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private val stepCounter: Sensor? =
        sensorManager.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
    private val prefs = context.getSharedPreferences("steps", Context.MODE_PRIVATE)

    private val tag = "PhoneSteps"

    fun start(): Boolean {
        val sensor = stepCounter
        if (sensor == null) {
            Log.w(tag, "No step counter on this phone")
            return false
        }
        sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
        return true
    }

    fun stop() {
        sensorManager.unregisterListener(this)
    }

    /** Steps taken today, or null when nothing has been counted yet today. */
    fun stepsToday(): Int? {
        if (prefs.getString(KEY_DATE, null) != LocalDate.now().toString()) return null
        val last = prefs.getLong(KEY_LAST, -1L)
        if (last < 0) return null
        val total = prefs.getLong(KEY_ACC, 0L) + (last - prefs.getLong(KEY_BASE, last))
        return total.coerceIn(0L, Int.MAX_VALUE.toLong()).toInt()
    }

    override fun onSensorChanged(event: SensorEvent?) {
        val value = event?.values?.firstOrNull()?.toLong() ?: return
        record(value)
    }

    @Synchronized
    private fun record(value: Long) {
        val today = LocalDate.now().toString()
        val last = prefs.getLong(KEY_LAST, -1L)
        var base = prefs.getLong(KEY_BASE, value)
        var acc = prefs.getLong(KEY_ACC, 0L)

        if (prefs.getString(KEY_DATE, null) != today) {
            // New day: count from the previous reading (or from zero after a reboot).
            base = when {
                last < 0 -> value
                value >= last -> last
                else -> 0L
            }
            acc = 0L
        } else if (last >= 0 && value < last) {
            // Counter reset by a reboot mid-day: bank what we had and restart from zero.
            acc += last - base
            base = 0L
        }

        prefs.edit()
            .putString(KEY_DATE, today)
            .putLong(KEY_BASE, base)
            .putLong(KEY_ACC, acc)
            .putLong(KEY_LAST, value)
            .apply()
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) = Unit

    companion object {
        private const val KEY_DATE = "date"
        private const val KEY_BASE = "base"
        private const val KEY_ACC = "acc"
        private const val KEY_LAST = "last"
    }
}
