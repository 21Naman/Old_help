package com.rakshak.phone.ui

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.PowerManager
import android.provider.Settings as AndroidSettings
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.rakshak.phone.data.PhoneSettings

@Composable
fun SettingsScreen(
    initial: PhoneSettings,
    canGoBack: Boolean,
    onSave: (PhoneSettings) -> Unit,
    onBack: () -> Unit,
) {
    val context = LocalContext.current
    var api by rememberSaveable { mutableStateOf(initial.apiUrl) }
    var web by rememberSaveable { mutableStateOf(initial.webUrl) }
    var key by rememberSaveable { mutableStateOf(initial.deviceKey) }
    var showKey by rememberSaveable { mutableStateOf(false) }

    val apiOk = isHttpUrl(api)
    val webOk = web.isBlank() || isHttpUrl(web)
    val canSave = apiOk && webOk && key.isNotBlank()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .safeDrawingPadding()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("Settings", style = MaterialTheme.typography.headlineMedium, modifier = Modifier.weight(1f))
            if (canGoBack) TextButton(onClick = onBack) { Text("Back") }
        }
        Text(
            "Ask your family member for these. They are stored encrypted on this phone.",
            style = MaterialTheme.typography.bodyMedium,
        )

        OutlinedTextField(
            value = api,
            onValueChange = { api = it },
            label = { Text("API URL") },
            placeholder = { Text("https://suraksha-api.onrender.com") },
            isError = api.isNotBlank() && !apiOk,
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = web,
            onValueChange = { web = it },
            label = { Text("Web URL (for Talk to Suraksha)") },
            placeholder = { Text("https://suraksha.vercel.app") },
            isError = !webOk,
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Uri),
            modifier = Modifier.fillMaxWidth(),
        )
        OutlinedTextField(
            value = key,
            onValueChange = { key = it },
            label = { Text("Device key") },
            singleLine = true,
            visualTransformation = if (showKey) VisualTransformation.None else PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            trailingIcon = {
                TextButton(onClick = { showKey = !showKey }) { Text(if (showKey) "Hide" else "Show") }
            },
            modifier = Modifier.fillMaxWidth(),
        )

        Button(
            onClick = { onSave(PhoneSettings(api, web, key)) },
            enabled = canSave,
            modifier = Modifier.fillMaxWidth().height(56.dp),
        ) { Text("Save") }

        OutlinedButton(
            onClick = { requestIgnoreBatteryOptimizations(context) },
            modifier = Modifier.fillMaxWidth().height(56.dp),
        ) { Text("Keep running in the background") }
        Text(
            "Stops the phone from pausing fall detection to save battery.",
            style = MaterialTheme.typography.bodySmall,
        )
    }
}

private fun isHttpUrl(s: String): Boolean {
    val t = s.trim()
    return (t.startsWith("http://") || t.startsWith("https://")) && t.length > "https://".length
}

@SuppressLint("BatteryLife")
private fun requestIgnoreBatteryOptimizations(context: android.content.Context) {
    val pm = context.getSystemService(PowerManager::class.java)
    val intent = if (pm.isIgnoringBatteryOptimizations(context.packageName)) {
        Intent(AndroidSettings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS)
    } else {
        Intent(AndroidSettings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:${context.packageName}"))
    }
    runCatching { context.startActivity(intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)) }
}
