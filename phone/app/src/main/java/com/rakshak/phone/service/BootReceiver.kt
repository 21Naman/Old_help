package com.rakshak.phone.service

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import com.rakshak.phone.data.Settings

/** Restarts [SensorService] after a reboot or app update, once the app has been set up. */
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED &&
            intent.action != Intent.ACTION_MY_PACKAGE_REPLACED
        ) return
        if (!Settings.load(context).isComplete) return
        try {
            SensorService.start(context)
        } catch (e: Exception) {
            Log.e("BootReceiver", "Could not start sensor service", e)
        }
    }
}
