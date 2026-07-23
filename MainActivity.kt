package com.example.festomotorremote

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

private const val GIST_ID = "f7892579389e55fdedac6544fccf2751"
private const val GITHUB_TOKEN = "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"

private val EpicBlue = Color(0xFF0078F2)
private val EpicDark = Color(0xFF0E0E11)
private val EpicCard = Color(0xFF17181C)
private val EpicBorder = Color(0xFF2A2D33)
private val EpicText = Color(0xFFFFFFFF)
private val EpicDim = Color(0xFFA0A0A8)
private val EpicSuccess = Color(0xFF4FBF67)
private val EpicWarning = Color(0xFFF8B133)
private val EpicError = Color(0xFFE63946)

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            MaterialTheme(
                colorScheme = MaterialTheme.colorScheme.copy(
                    primary = EpicBlue,
                    background = EpicDark,
                    surface = EpicCard,
                    onBackground = EpicText,
                    onSurface = EpicText
                )
            ) {
                FestoRemoteScreen()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FestoRemoteScreen() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val api = remember { GistApi.create() }

    var degreesText by remember { mutableStateOf("360") }
    var speed by remember { mutableIntStateOf(30) }
    var direction by remember { mutableStateOf("CW") }

    var status by remember { mutableStateOf<MotorStatus?>(null) }
    var loadingStatus by remember { mutableStateOf(true) }
    var requestInProgress by remember { mutableStateOf(false) }
    var lastError by remember { mutableStateOf<String?>(null) }

    suspend fun refreshStatus(showError: Boolean = false) {
        try {
            val gist = api.getGist(
                gistId = GIST_ID,
                authorization = "Bearer $GITHUB_TOKEN"
            )

            val rawStatus = gist.files["status.json"]?.content
            status = rawStatus?.let { GistApi.gson.fromJson(it, MotorStatus::class.java) }
            loadingStatus = false
            lastError = null
        } catch (error: Exception) {
            loadingStatus = false

            if (showError) {
                lastError = error.message ?: "Unable to read PC status"
            }
        }
    }

    fun sendCommand(command: String, value: Any? = null) {
        if (GIST_ID.startsWith("PUT_") || GITHUB_TOKEN.startsWith("PUT_")) {
            Toast.makeText(
                context,
                "First add your Gist ID and GitHub token in MainActivity.kt",
                Toast.LENGTH_LONG
            ).show()
            return
        }

        scope.launch {
            requestInProgress = true
            lastError = null

            try {
                val commandData = RemoteCommand(
                    commandId = System.currentTimeMillis().toString(),
                    cmd = command,
                    value = value
                )

                val commandJson = GistApi.gson.toJson(commandData)

                api.updateGist(
                    gistId = GIST_ID,
                    authorization = "Bearer $GITHUB_TOKEN",
                    body = GistUpdateRequest(
                        files = mapOf(
                            "command.json" to GistFileUpdate(commandJson)
                        )
                    )
                )

                delay(500)
                refreshStatus()

                Toast.makeText(
                    context,
                    "Command sent: $command",
                    Toast.LENGTH_SHORT
                ).show()
            } catch (error: Exception) {
                lastError = error.message ?: "Command failed"

                Toast.makeText(
                    context,
                    "Error sending $command",
                    Toast.LENGTH_LONG
                ).show()
            } finally {
                requestInProgress = false
            }
        }
    }

    LaunchedEffect(Unit) {
        while (true) {
            if (!GIST_ID.startsWith("PUT_") && !GITHUB_TOKEN.startsWith("PUT_")) {
                refreshStatus()
            }

            delay(2000)
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(EpicDark)
    ) {
        TopAppBar(
            title = {
                Column {
                    Text(
                        text = "MOTOR CONTROL",
                        fontWeight = FontWeight.Bold,
                        fontSize = 19.sp,
                        color = EpicText
                    )

                    Text(
                        text = "Festo Remote Interface",
                        fontSize = 12.sp,
                        color = EpicDim
                    )
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = EpicDark
            )
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            StatusCard(
                status = status,
                isLoading = loadingStatus
            )

            if (lastError != null) {
                ErrorCard(lastError!!)
            }

            SectionCard(title = "Connection") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    ActionButton(
                        text = "CONNECT",
                        color = EpicBlue,
                        modifier = Modifier.weight(1f),
                        enabled = !requestInProgress
                    ) {
                        sendCommand("CONNECT")
                    }

                    ActionButton(
                        text = "DISCONNECT",
                        color = EpicError,
                        modifier = Modifier.weight(1f),
                        enabled = !requestInProgress
                    ) {
                        sendCommand("DISCONNECT")
                    }
                }

                Spacer(Modifier.height(10.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    ActionButton(
                        text = "HOME",
                        color = EpicBlue,
                        modifier = Modifier.weight(1f),
                        enabled = !requestInProgress
                    ) {
                        sendCommand("HOME")
                    }

                    ActionButton(
                        text = "RESET",
                        color = EpicWarning,
                        modifier = Modifier.weight(1f),
                        enabled = !requestInProgress
                    ) {
                        sendCommand("RESET")
                    }
                }
            }

            SectionCard(title = "Rotation Control") {
                Text(
                    text = "Degrees",
                    color = EpicDim,
                    fontSize = 13.sp
                )

                Spacer(Modifier.height(6.dp))

                OutlinedTextField(
                    value = degreesText,
                    onValueChange = {
                        degreesText = it.filter(Char::isDigit)
                    },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Number
                    ),
                    label = {
                        Text("Example: 360")
                    }
                )

                Spacer(Modifier.height(10.dp))

                ActionButton(
                    text = "SET DEGREES",
                    color = EpicBlue,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !requestInProgress && degreesText.isNotBlank()
                ) {
                    sendCommand("SET_DEGREES", degreesText)
                }

                Spacer(Modifier.height(18.dp))

                Text(
                    text = "Direction",
                    color = EpicDim,
                    fontSize = 13.sp
                )

                Spacer(Modifier.height(8.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    DirectionButton(
                        text = "CW",
                        selected = direction == "CW",
                        modifier = Modifier.weight(1f)
                    ) {
                        direction = "CW"
                        sendCommand("SET_DIRECTION", "CW")
                    }

                    DirectionButton(
                        text = "CCW",
                        selected = direction == "CCW",
                        modifier = Modifier.weight(1f)
                    ) {
                        direction = "CCW"
                        sendCommand("SET_DIRECTION", "CCW")
                    }
                }

                Spacer(Modifier.height(18.dp))

                Text(
                    text = "Speed: $speed RPM",
                    color = if (speed > 30) EpicWarning else EpicBlue,
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp
                )

                Slider(
                    value = speed.toFloat(),
                    onValueChange = {
                        speed = it.roundToInt()
                    },
                    valueRange = 1f..1100f,
                    steps = 1098,
                    colors = SliderDefaults.colors(
                        thumbColor = EpicBlue,
                        activeTrackColor = EpicBlue,
                        inactiveTrackColor = EpicBorder
                    )
                )

                ActionButton(
                    text = "SET SPEED: $speed RPM",
                    color = EpicBlue,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !requestInProgress
                ) {
                    sendCommand("SET_SPEED", speed)
                }

                Spacer(Modifier.height(16.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    ActionButton(
                        text = "START ROTATION",
                        color = EpicSuccess,
                        modifier = Modifier.weight(1f),
                        enabled = !requestInProgress
                    ) {
                        sendCommand("ROTATE")
                    }

                    ActionButton(
                        text = "EMERGENCY STOP",
                        color = EpicError,
                        modifier = Modifier.weight(1f),
                        enabled = !requestInProgress
                    ) {
                        sendCommand("STOP")
                    }
                }
            }

            SectionCard(title = "Quick Presets") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    PresetButton("90°", Modifier.weight(1f)) {
                        degreesText = "90"
                        sendCommand("SET_DEGREES", "90")
                    }

                    PresetButton("180°", Modifier.weight(1f)) {
                        degreesText = "180"
                        sendCommand("SET_DEGREES", "180")
                    }

                    PresetButton("360°", Modifier.weight(1f)) {
                        degreesText = "360"
                        sendCommand("SET_DEGREES", "360")
                    }
                }

                Spacer(Modifier.height(8.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    PresetButton("720°", Modifier.weight(1f)) {
                        degreesText = "720"
                        sendCommand("SET_DEGREES", "720")
                    }

                    PresetButton("1800°", Modifier.weight(1f)) {
                        degreesText = "1800"
                        sendCommand("SET_DEGREES", "1800")
                    }
                }
            }

            if (requestInProgress) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center
                ) {
                    CircularProgressIndicator(
                        color = EpicBlue,
                        modifier = Modifier.width(26.dp)
                    )
                }
            }

            Text(
                text = "Status refresh: every 2 seconds",
                color = EpicDim,
                fontSize = 12.sp,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp)
            )
        }
    }
}

@Composable
fun StatusCard(status: MotorStatus?, isLoading: Boolean) {
    SectionCard(title = "Live PC Status") {
        if (isLoading) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                CircularProgressIndicator(
                    color = EpicBlue,
                    modifier = Modifier.width(18.dp)
                )

                Spacer(Modifier.width(10.dp))

                Text(
                    text = "Reading status.json...",
                    color = EpicDim
                )
            }
            return@SectionCard
        }

        if (status == null) {
            Text(
                text = "No PC status received yet. Start the desktop app first.",
                color = EpicWarning
            )
            return@SectionCard
        }

        StatusRow("Speed", "${status.speed ?: 0} RPM", EpicBlue)
        StatusRow("Degrees", status.degrees ?: "-", EpicText)
        StatusRow("Direction", status.direction ?: "-", EpicText)

        val stateColor = when {
            status.state?.contains("ROTATING", ignoreCase = true) == true -> EpicSuccess
            status.state?.contains("STOPPED", ignoreCase = true) == true -> EpicError
            else -> EpicText
        }

        StatusRow("State", status.state ?: "-", stateColor)

        val powerColor = when (status.power?.uppercase()) {
            "ON" -> EpicSuccess
            "OFF" -> EpicError
            else -> EpicText
        }

        StatusRow("Power", status.power ?: "-", powerColor)
    }
}

@Composable
fun StatusRow(label: String, value: String, valueColor: Color) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            color = EpicDim,
            fontSize = 14.sp
        )

        Text(
            text = value,
            color = valueColor,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun SectionCard(
    title: String,
    content: @Composable () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = EpicCard
        ),
        shape = RoundedCornerShape(6.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = title.uppercase(),
                color = EpicText,
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp
            )

            Spacer(Modifier.height(14.dp))
            content()
        }
    }
}

@Composable
fun ActionButton(
    text: String,
    color: Color,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(48.dp),
        enabled = enabled,
        shape = RoundedCornerShape(4.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = color,
            contentColor = Color.White,
            disabledContainerColor = EpicBorder,
            disabledContentColor = EpicDim
        )
    ) {
        Text(
            text = text,
            fontWeight = FontWeight.Bold,
            fontSize = 11.sp
        )
    }
}

@Composable
fun DirectionButton(
    text: String,
    selected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    val background = if (selected) EpicBlue else EpicDark
    val borderColor = if (selected) EpicBlue else EpicBorder

    Box(
        modifier = modifier
            .height(48.dp)
            .background(background, RoundedCornerShape(4.dp))
            .border(1.dp, borderColor, RoundedCornerShape(4.dp))
            .padding(4.dp),
        contentAlignment = Alignment.Center
    ) {
        Button(
            onClick = onClick,
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.Transparent,
                contentColor = EpicText
            ),
            contentPadding = PaddingValues(0.dp),
            modifier = Modifier.fillMaxSize()
        ) {
            Text(
                text = text,
                fontWeight = FontWeight.Bold
            )
        }
    }
}

@Composable
fun PresetButton(
    text: String,
    modifier: Modifier = Modifier,
    onClick: () -> Unit
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(44.dp),
        shape = RoundedCornerShape(4.dp),
        colors = ButtonDefaults.buttonColors(
            containerColor = EpicDark,
            contentColor = EpicText
        )
    ) {
        Text(
            text = text,
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold
        )
    }
}

@Composable
fun ErrorCard(error: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = Color(0xFF3A151A)
        ),
        shape = RoundedCornerShape(6.dp)
    ) {
        Text(
            text = "Error: $error",
            color = EpicError,
            modifier = Modifier.padding(14.dp),
            fontSize = 13.sp
        )
    }
}