Exit code: 0
Wall time: 1.1 seconds
Output:
package com.example.festomotorremote

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.core.tween
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import retrofit2.HttpException
import kotlin.math.roundToInt

private const val GIST_PREFERENCES = "gist_connection"
private const val GIST_ID_KEY = "gist_id"
private const val GITHUB_TOKEN_KEY = "github_token"

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
                FestoRemoteApp()
            }
        }
    }
}

@Composable
fun FestoRemoteApp() {
    var showSplash by remember { mutableStateOf(true) }

    LaunchedEffect(Unit) {
        delay(950)
        showSplash = false
    }

    Box(modifier = Modifier.fillMaxSize()) {
        FestoRemoteScreen()

        AnimatedVisibility(
            visible = showSplash,
            enter = fadeIn(animationSpec = tween(durationMillis = 180)),
            exit = fadeOut(animationSpec = tween(durationMillis = 480))
        ) {
            FestoLoadingScreen()
        }
    }
}

@Composable
fun FestoLoadingScreen() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(Color(0xFF111827), EpicDark, Color(0xFF090A0D))
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "FESTO",
                color = EpicText,
                fontWeight = FontWeight.Black,
                fontSize = 32.sp,
                letterSpacing = 4.sp
            )

            Text(
                text = "MOTOR CONTROL",
                color = EpicBlue,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
                letterSpacing = 2.sp
            )

            CircularProgressIndicator(
                color = EpicBlue,
                strokeWidth = 3.dp,
                modifier = Modifier.width(30.dp)
            )

            Text(
                text = "Preparing remote interface",
                color = EpicDim,
                fontSize = 13.sp
            )
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun FestoRemoteScreen() {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val focusManager = LocalFocusManager.current
    val api = remember { GistApi.create() }
    val preferences = remember(context) {
        context.getSharedPreferences(GIST_PREFERENCES, 0)
    }

    var degreesText by remember { mutableStateOf("360") }
    var speed by remember { mutableIntStateOf(30) }
    var direction by remember { mutableStateOf("CW") }
    var gistId by remember {
        mutableStateOf(preferences.getString(GIST_ID_KEY, "").orEmpty())
    }
    var githubToken by remember {
        mutableStateOf(preferences.getString(GITHUB_TOKEN_KEY, "").orEmpty())
    }

    var status by remember { mutableStateOf<MotorStatus?>(null) }
    var loadingStatus by remember { mutableStateOf(true) }
    var requestInProgress by remember { mutableStateOf(false) }
    var lastError by remember { mutableStateOf<String?>(null) }
    var hasLocalDegreesDraft by remember { mutableStateOf(false) }
    var hasLocalSpeedDraft by remember { mutableStateOf(false) }

    fun applyDesktopStatus(desktopStatus: MotorStatus, force: Boolean = false) {
        val desktopDegrees = desktopStatus.degrees
            ?.filter(Char::isDigit)
            ?.takeIf { it.isNotBlank() }

        if (desktopDegrees != null && (force || !hasLocalDegreesDraft)) {
            degreesText = desktopDegrees
            hasLocalDegreesDraft = false
        }

        desktopStatus.speed?.takeIf { force || !hasLocalSpeedDraft }?.let { desktopSpeed ->
            speed = desktopSpeed.coerceIn(1, 1100)
            hasLocalSpeedDraft = false
        }

        desktopStatus.direction
            ?.uppercase()
            ?.takeIf { it == "CW" || it == "CCW" }
            ?.let { direction = it }
    }

    fun friendlyGistError(error: Exception, fallback: String): String {
        if (error is HttpException && error.code() == 403) {
            return "GitHub denied Gist access (403). Check that the token has Gists read/write permission."
        }

        return error.message ?: fallback
    }

    suspend fun refreshStatus(
        showError: Boolean = false,
        syncControlValues: Boolean = false
    ) {
        val configuredGistId = gistId.trim()
        val configuredGithubToken = githubToken.trim()

        if (configuredGistId.isBlank() || configuredGithubToken.isBlank()) {
            status = null
            loadingStatus = false
            return
        }

        try {
            val gist = api.getGist(
                gistId = configuredGistId,
                authorization = "Bearer $configuredGithubToken"
            )

            val rawStatus = gist.files["status.json"]?.content
            val desktopStatus = rawStatus?.let {
                GistApi.gson.fromJson(it, MotorStatus::class.java)
            }

            status = desktopStatus

            // Keep a local edit intact until the user sends it to the desktop app.
            if ((syncControlValues || !requestInProgress) && desktopStatus != null) {
                applyDesktopStatus(desktopStatus, force = syncControlValues)
            }

            loadingStatus = false
            lastError = null
        } catch (error: Exception) {
            loadingStatus = false

            if (showError) {
                lastError = friendlyGistError(error, "Unable to read PC status")
            }
        }
    }

    fun saveGistSettings() {
        gistId = gistId.trim()
        githubToken = githubToken.trim()

        if (gistId.isBlank() || githubToken.isBlank()) {
            Toast.makeText(
                context,
                "Enter both Gist ID and GitHub token",
                Toast.LENGTH_LONG
            ).show()
            return
        }

        preferences.edit()
            .putString(GIST_ID_KEY, gistId)
            .putString(GITHUB_TOKEN_KEY, githubToken)
            .apply()

        loadingStatus = true
        scope.launch {
            refreshStatus(showError = true)
        }

        Toast.makeText(
            context,
            "Gist settings saved",
            Toast.LENGTH_SHORT
        ).show()
    }

    fun sendCommand(command: String, value: Any? = null) {
        val configuredGistId = gistId.trim()
        val configuredGithubToken = githubToken.trim()

        if (configuredGistId.isBlank() || configuredGithubToken.isBlank()) {
            Toast.makeText(
                context,
                "Enter and save your Gist ID and GitHub token first",
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
                    gistId = configuredGistId,
                    authorization = "Bearer $configuredGithubToken",
                    body = GistUpdateRequest(
                        files = mapOf(
                            "command.json" to GistFileUpdate(commandJson)
                        )
                    )
                )

                // The desktop listener polls every two seconds; wait for its status update.
                delay(2300)
                refreshStatus(showError = true, syncControlValues = true)

                Toast.makeText(
                    context,
                    "Command sent: $command",
                    Toast.LENGTH_SHORT
                ).show()
            } catch (error: Exception) {
                lastError = friendlyGistError(error, "Command failed")

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
            if (gistId.isNotBlank() && githubToken.isNotBlank()) {
                refreshStatus()
            } else {
                status = null
                loadingStatus = false
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
            SectionCard(title = "GitHub Gist") {
                Text(
                    text = "Enter the shared Gist credentials used by the desktop app.",
                    color = EpicDim,
                    fontSize = 13.sp
                )

                Spacer(Modifier.height(10.dp))

                OutlinedTextField(
                    value = gistId,
                    onValueChange = { gistId = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text("Gist ID") }
                )

                Spacer(Modifier.height(10.dp))

                OutlinedTextField(
                    value = githubToken,
                    onValueChange = { githubToken = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text("GitHub token") },
                    visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Password
                    )
                )

                Spacer(Modifier.height(10.dp))

                ActionButton(
                    text = "SAVE GIST SETTINGS",
                    color = EpicBlue,
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !requestInProgress
                ) {
                    saveGistSettings()
                }
            }

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
                        hasLocalDegreesDraft = true
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
                    focusManager.clearFocus()
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
                        focusManager.clearFocus()
                        sendCommand("SET_DIRECTION", "CW")
                    }

                    DirectionButton(
                        text = "CCW",
                        selected = direction == "CCW",
                        modifier = Modifier.weight(1f)
                    ) {
                        direction = "CCW"
                        focusManager.clearFocus()
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
                        hasLocalSpeedDraft = true
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
                    focusManager.clearFocus()
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
                    PresetButton("90Â°", Modifier.weight(1f)) {
                        degreesText = "90"
                        hasLocalDegreesDraft = true
                        sendCommand("SET_DEGREES", "90")
                    }

                    PresetButton("180Â°", Modifier.weight(1f)) {
                        degreesText = "180"
                        hasLocalDegreesDraft = true
                        sendCommand("SET_DEGREES", "180")
                    }

                    PresetButton("360Â°", Modifier.weight(1f)) {
                        degreesText = "360"
                        hasLocalDegreesDraft = true
                        sendCommand("SET_DEGREES", "360")
                    }
                }

                Spacer(Modifier.height(8.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    PresetButton("720Â°", Modifier.weight(1f)) {
                        degreesText = "720"
                        hasLocalDegreesDraft = true
                        sendCommand("SET_DEGREES", "720")
                    }

                    PresetButton("1800Â°", Modifier.weight(1f)) {
                        degreesText = "1800"
                        hasLocalDegreesDraft = true
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
                text = "Desktop changes synchronize automatically every 2 seconds",
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
            containerColor = EpicCard.copy(alpha = 0.93f)
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
            containerColor = lerp(EpicCard, color, 0.42f),
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
    val background = if (selected) lerp(EpicDark, EpicBlue, 0.38f) else EpicDark
    val borderColor = if (selected) lerp(EpicBorder, EpicBlue, 0.60f) else EpicBorder

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
            containerColor = Color(0xFF3A151A).copy(alpha = 0.94f)
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
