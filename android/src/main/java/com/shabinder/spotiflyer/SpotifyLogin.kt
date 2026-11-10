package com.shabinder.spotiflyer

import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.util.Base64
import com.shabinder.common.core_components.preference_manager.PreferenceManager
import com.shabinder.common.models.Actions
import com.shabinder.common.models.spotify.SPOTIFY_REDIRECT_URI
import com.shabinder.common.models.spotify.SpotifyCredentials
import com.shabinder.common.providers.spotify.requests.exchangeSpotifyCode
import java.security.MessageDigest
import java.security.SecureRandom

/** FlyerPlus: Spotify sign-in with Authorization Code + PKCE (no client secret on the phone). */
object SpotifyLogin {
    private const val FLAGS = Base64.URL_SAFE or Base64.NO_PADDING or Base64.NO_WRAP

    fun start(activity: Activity) {
        val clientId = PreferenceManager.instance.spotifyCredentials.clientID
        if (clientId == SpotifyCredentials().clientID) {
            Actions.instance.showPopUpMessage("Enter your own Spotify Client ID first", true)
            return
        }
        val verifier = Base64.encodeToString(ByteArray(48).also { SecureRandom().nextBytes(it) }, FLAGS)
        PreferenceManager.instance.spotifyPkceVerifier = verifier
        val challenge = Base64.encodeToString(
            MessageDigest.getInstance("SHA-256").digest(verifier.toByteArray()), FLAGS
        )
        val url = Uri.parse("https://accounts.spotify.com/authorize").buildUpon()
            .appendQueryParameter("client_id", clientId)
            .appendQueryParameter("response_type", "code")
            .appendQueryParameter("redirect_uri", SPOTIFY_REDIRECT_URI)
            .appendQueryParameter("code_challenge_method", "S256")
            .appendQueryParameter("code_challenge", challenge)
            .appendQueryParameter("scope", "playlist-read-private playlist-read-collaborative")
            .build()
        activity.startActivity(Intent(Intent.ACTION_VIEW, url))
    }

    /** Returns true if [intent] was a Spotify sign-in redirect (handled either way). */
    suspend fun handleRedirect(intent: Intent?): Boolean {
        val data = intent?.data ?: return false
        if (!data.toString().startsWith(SPOTIFY_REDIRECT_URI)) return false
        val code = data.getQueryParameter("code")
        val message = if (code == null) {
            "Spotify sign-in cancelled: ${data.getQueryParameter("error")}"
        } else runCatching { exchangeSpotifyCode(code) }.fold(
            onSuccess = { "Signed in to Spotify" },
            onFailure = { "Spotify sign-in failed: ${it.message}" }
        )
        Actions.instance.showPopUpMessage(message, true)
        return true
    }
}
