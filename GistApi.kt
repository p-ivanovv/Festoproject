package com.example.festomotorremote

import com.google.gson.Gson
import com.google.gson.annotations.SerializedName
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.PATCH
import retrofit2.http.Path
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

data class GistResponse(
    @SerializedName("files")
    val files: Map<String, GistFile>
)

data class GistFile(
    @SerializedName("content")
    val content: String?
)

data class GistFileUpdate(
    @SerializedName("content")
    val content: String
)

data class GistUpdateRequest(
    @SerializedName("files")
    val files: Map<String, GistFileUpdate>
)

data class RemoteCommand(
    @SerializedName("command_id")
    val commandId: String,

    @SerializedName("cmd")
    val cmd: String,

    @SerializedName("value")
    val value: Any?
)

data class MotorStatus(
    @SerializedName("speed")
    val speed: Int?,

    @SerializedName("degrees")
    val degrees: String?,

    @SerializedName("direction")
    val direction: String?,

    @SerializedName("state")
    val state: String?,

    @SerializedName("power")
    val power: String?
)

interface GistApi {

    @GET("gists/{gistId}")
    suspend fun getGist(
        @Path("gistId") gistId: String,
        @Header("Authorization") authorization: String,
        @Header("Accept") accept: String = "application/vnd.github+json"
    ): GistResponse

    @PATCH("gists/{gistId}")
    suspend fun updateGist(
        @Path("gistId") gistId: String,
        @Header("Authorization") authorization: String,
        @Header("Accept") accept: String = "application/vnd.github+json",
        @Body body: GistUpdateRequest
    ): GistResponse

    companion object {
        val gson = Gson()

        fun create(): GistApi {
            val logger = HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BASIC
            }

            val client = OkHttpClient.Builder()
                .addInterceptor(logger)
                .build()

            return Retrofit.Builder()
                .baseUrl("https://api.github.com/")
                .client(client)
                .addConverterFactory(GsonConverterFactory.create(gson))
                .build()
                .create(GistApi::class.java)
        }
    }
}