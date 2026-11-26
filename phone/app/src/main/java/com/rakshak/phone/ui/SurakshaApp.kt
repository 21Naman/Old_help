package com.rakshak.phone.ui

import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import com.rakshak.phone.MainActivity
import com.rakshak.phone.data.Settings
import com.rakshak.phone.service.SensorService

private val Green = Color(0xFF2E7D5B)
private val Red = Color(0xFFC62828)

@Composable
fun SurakshaApp() {
    val colors = if (isSystemInDarkTheme()) {
        darkColorScheme(primary = Color(0xFF7FD3A8), error = Color(0xFFFF8A80))
    } else {
        lightColorScheme(primary = Green, error = Red)
    }
    MaterialTheme(colorScheme = colors) {
        Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
            val context = LocalContext.current
            var settings by remember { mutableStateOf(Settings.load(context)) }
            var showSettings by rememberSaveable { mutableStateOf(!settings.isComplete) }

            val permissionLauncher = rememberLauncherForActivityResult(
                ActivityResultContracts.RequestMultiplePermissions(),
            ) {
                if (!SensorService.start(context)) {
                    Toast.makeText(
                        context,
                        "Suraksha needs the Physical activity permission. Allow it in the phone's app settings.",
                        Toast.LENGTH_LONG,
                    ).show()
                }
            }

            fun startProtection() {
                if (MainActivity.runtimePermissions.isEmpty()) {
                    SensorService.start(context)
                } else {
                    permissionLauncher.launch(MainActivity.runtimePermissions)
                }
            }

            // Start automatically once set up; asks for permissions the first time.
            LaunchedEffect(settings.isComplete) {
                if (settings.isComplete) startProtection()
            }

            if (showSettings) {
                SettingsScreen(
                    initial = settings,
                    canGoBack = settings.isComplete,
                    onSave = {
                        Settings.save(context, it)
                        settings = Settings.load(context)
                        showSettings = false
                    },
                    onBack = { showSettings = false },
                )
            } else {
                HomeScreen(
                    webUrl = settings.webUrl,
                    onStartProtection = ::startProtection,
                    onOpenSettings = { showSettings = true },
                )
            }
        }
    }
}
