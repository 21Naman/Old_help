package com.rakshak.phone

import android.Manifest
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.rakshak.phone.data.PhoneStatus
import com.rakshak.phone.ui.SurakshaApp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        PhoneStatus.load(this)
        enableEdgeToEdge()
        setContent { SurakshaApp() }
    }

    companion object {
        /** Runtime permissions the service needs; older Android versions grant these at install. */
        val runtimePermissions: Array<String> = buildList {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) add(Manifest.permission.ACTIVITY_RECOGNITION)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) add(Manifest.permission.POST_NOTIFICATIONS)
        }.toTypedArray()
    }
}
