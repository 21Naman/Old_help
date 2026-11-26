package com.rakshak.phone.ui

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.text.format.DateFormat
import android.widget.Toast
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.rakshak.phone.data.PhoneStatus
import com.rakshak.phone.data.SentEvent
import kotlinx.coroutines.launch
import java.util.Date

@Composable
fun HomeScreen(
    webUrl: String,
    onStartProtection: () -> Unit,
    onOpenSettings: () -> Unit,
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val running by PhoneStatus.serviceRunning.collectAsStateWithLifecycle()
    val lastEvent by PhoneStatus.lastEvent.collectAsStateWithLifecycle()
    var sending by remember { mutableStateOf<String?>(null) }

    fun send(kind: String, sentText: String) {
        if (sending != null) return
        sending = kind
        scope.launch {
            val ok = PhoneStatus.send(context, kind)
            sending = null
            val msg = if (ok) sentText else "Could not reach Suraksha. Check the internet and try again."
            Toast.makeText(context, msg, Toast.LENGTH_LONG).show()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .safeDrawingPadding()
            .verticalScroll(rememberScrollState())
            .padding(horizontal = 16.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(
                "Suraksha",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.weight(1f),
            )
            IconButton(onClick = onOpenSettings) {
                Icon(Icons.Filled.Settings, contentDescription = "Settings")
            }
        }

        StatusCard(running = running, lastEvent = lastEvent, onStartProtection = onStartProtection)

        Button(
            onClick = { send("im_okay", "Sent: you're okay") },
            enabled = sending == null,
            modifier = Modifier.fillMaxWidth().height(140.dp),
            shape = MaterialTheme.shapes.extraLarge,
        ) {
            Text(if (sending == "im_okay") "Sending…" else "I'm okay", fontSize = 36.sp, fontWeight = FontWeight.Bold)
        }

        Button(
            onClick = { send("fall", "Help is on the way. Suraksha has been told.") },
            enabled = sending == null,
            modifier = Modifier.fillMaxWidth().height(96.dp),
            shape = MaterialTheme.shapes.extraLarge,
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.error,
                contentColor = MaterialTheme.colorScheme.onError,
            ),
        ) {
            Text(if (sending == "fall") "Sending…" else "Help", fontSize = 30.sp, fontWeight = FontWeight.Bold)
        }

        OutlinedButton(
            onClick = { openParentPage(context, webUrl) },
            modifier = Modifier.fillMaxWidth().height(72.dp),
            shape = MaterialTheme.shapes.extraLarge,
        ) {
            Text("Talk to Suraksha", fontSize = 22.sp)
        }

        Spacer(Modifier.height(8.dp))
    }
}

@Composable
private fun StatusCard(running: Boolean, lastEvent: SentEvent?, onStartProtection: () -> Unit) {
    val context = LocalContext.current
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                if (running) "Protection is on" else "Protection is off",
                style = MaterialTheme.typography.titleLarge,
                color = if (running) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
            )
            Text(
                lastEvent?.let { e ->
                    val time = DateFormat.getTimeFormat(context).format(Date(e.atMillis))
                    val outcome = if (e.delivered) "sent" else "not delivered"
                    "Last: ${labelFor(e.kind)} at $time, $outcome"
                } ?: "Nothing sent yet",
                style = MaterialTheme.typography.bodyLarge,
            )
            if (!running) {
                TextButton(onClick = onStartProtection) { Text("Turn on", fontSize = 18.sp) }
            }
        }
    }
}

private fun openParentPage(context: Context, webUrl: String) {
    if (webUrl.isBlank()) {
        Toast.makeText(context, "Add the web address in Settings first.", Toast.LENGTH_LONG).show()
        return
    }
    try {
        context.startActivity(
            Intent(Intent.ACTION_VIEW, Uri.parse(webUrl.trimEnd('/') + "/parent"))
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK),
        )
    } catch (e: ActivityNotFoundException) {
        Toast.makeText(context, "No browser found on this phone.", Toast.LENGTH_LONG).show()
    }
}

private fun labelFor(kind: String): String = when (kind) {
    "wake" -> "good morning"
    "fall" -> "help alert"
    "im_okay" -> "I'm okay"
    "activity" -> "steps"
    else -> kind
}
