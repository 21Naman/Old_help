package com.rakshak.phone.service

import android.Manifest
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.rakshak.phone.MainActivity
import com.rakshak.phone.R
import com.rakshak.phone.data.PhoneStatus
import com.rakshak.phone.detect.FallDetector
import com.rakshak.phone.detect.StepTracker
import com.rakshak.phone.detect.WakeDetector
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

/**
 * Foreground service that keeps the phone's sensors running: fall detection, first movement /
 * first unlock of the day (wake), and today's steps (activity, every [ACTIVITY_INTERVAL_MS]).
 */
class SensorService : Service() {

    private val tag = "SensorService"
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    private var wakeLock: PowerManager.WakeLock? = null
    private lateinit var fallDetector: FallDetector
    private lateinit var wakeDetector: WakeDetector
    private lateinit var stepTracker: StepTracker

    private val unlockReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == Intent.ACTION_USER_PRESENT) onWake("unlock")
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        PhoneStatus.load(this)
        createChannels()

        try {
            ServiceCompat.startForeground(
                this,
                ONGOING_ID,
                ongoingNotification(),
                ServiceInfo.FOREGROUND_SERVICE_TYPE_HEALTH,
            )
        } catch (e: Exception) {
            // Missing ACTIVITY_RECOGNITION on Android 14+, or started from a disallowed state.
            Log.e(tag, "Cannot start in foreground", e)
            stopSelf()
            return
        }

        wakeLock = (getSystemService(POWER_SERVICE) as PowerManager)
            .newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "Suraksha::sensors")
            .apply {
                setReferenceCounted(false)
                acquire()
            }

        fallDetector = FallDetector(this) { onFall() }
        wakeDetector = WakeDetector(this) { onWake("first movement") }
        stepTracker = StepTracker(this)
        fallDetector.start()
        wakeDetector.start()
        val hasSteps = stepTracker.start()

        ContextCompat.registerReceiver(
            this,
            unlockReceiver,
            IntentFilter(Intent.ACTION_USER_PRESENT),
            ContextCompat.RECEIVER_NOT_EXPORTED,
        )

        if (hasSteps) {
            scope.launch {
                while (isActive) {
                    delay(ACTIVITY_INTERVAL_MS)
                    stepTracker.stepsToday()?.takeIf { it > 0 }?.let {
                        PhoneStatus.send(this@SensorService, "activity", steps = it)
                    }
                }
            }
        }

        PhoneStatus.setServiceRunning(true)
        Log.i(tag, "Sensors running")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int = START_STICKY

    override fun onDestroy() {
        if (::fallDetector.isInitialized) {
            fallDetector.stop()
            wakeDetector.stop()
            stepTracker.stop()
            runCatching { unregisterReceiver(unlockReceiver) }
        }
        scope.cancel()
        wakeLock?.takeIf { it.isHeld }?.release()
        PhoneStatus.setServiceRunning(false)
        super.onDestroy()
    }

    private fun onFall() {
        Log.i(tag, "Fall detected")
        notifyAlert("Fall detected", "Suraksha has been told. Open the app and tap I'm okay if you are fine.")
        scope.launch {
            PhoneStatus.send(this@SensorService, "fall")
            // FallDetector disarms itself after firing; its own 20 s cooldown still applies.
            delay(REARM_AFTER_MS)
            fallDetector.rearm()
        }
    }

    private fun onWake(reason: String) {
        if (!PhoneStatus.claimWakeToday(this)) return
        Log.i(tag, "Wake ($reason)")
        scope.launch {
            val ok = PhoneStatus.send(this@SensorService, "wake")
            if (!ok) PhoneStatus.releaseWake(this@SensorService)
        }
    }

    private fun createChannels() {
        val nm = getSystemService(NotificationManager::class.java)
        nm.createNotificationChannel(
            NotificationChannel(CHANNEL_ONGOING, "Protection running", NotificationManager.IMPORTANCE_LOW),
        )
        nm.createNotificationChannel(
            NotificationChannel(CHANNEL_ALERTS, "Fall alerts", NotificationManager.IMPORTANCE_HIGH),
        )
    }

    private fun openAppIntent(): PendingIntent = PendingIntent.getActivity(
        this,
        0,
        Intent(this, MainActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP),
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT,
    )

    private fun ongoingNotification(): Notification =
        NotificationCompat.Builder(this, CHANNEL_ONGOING)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("Suraksha is looking after you")
            .setContentText("Fall and morning check are on")
            .setContentIntent(openAppIntent())
            .setOngoing(true)
            .setForegroundServiceBehavior(NotificationCompat.FOREGROUND_SERVICE_IMMEDIATE)
            .build()

    private fun notifyAlert(title: String, text: String) {
        val notification = NotificationCompat.Builder(this, CHANNEL_ALERTS)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(text))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setContentIntent(openAppIntent())
            .setAutoCancel(true)
            .build()
        try {
            getSystemService(NotificationManager::class.java).notify(ALERT_ID, notification)
        } catch (e: SecurityException) {
            Log.w(tag, "Notifications not permitted", e)
        }
    }

    companion object {
        private const val CHANNEL_ONGOING = "ongoing"
        private const val CHANNEL_ALERTS = "alerts"
        private const val ONGOING_ID = 1
        private const val ALERT_ID = 2
        private const val ACTIVITY_INTERVAL_MS = 30 * 60_000L
        private const val REARM_AFTER_MS = 20_000L

        /** A health-type foreground service needs ACTIVITY_RECOGNITION first (Android 10+). */
        fun canStart(context: Context): Boolean =
            Build.VERSION.SDK_INT < Build.VERSION_CODES.Q ||
                ContextCompat.checkSelfPermission(context, Manifest.permission.ACTIVITY_RECOGNITION) ==
                PackageManager.PERMISSION_GRANTED

        fun start(context: Context): Boolean {
            if (!canStart(context)) return false
            ContextCompat.startForegroundService(context, Intent(context, SensorService::class.java))
            return true
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, SensorService::class.java))
        }
    }
}
