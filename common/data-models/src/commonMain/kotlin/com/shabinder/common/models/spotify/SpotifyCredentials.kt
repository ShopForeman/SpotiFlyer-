package com.shabinder.common.models.spotify

import kotlinx.serialization.Serializable

@Serializable
data class SpotifyCredentials(
    val clientID: String = "5f573c9620494bae87890c0f08a60293",
    val clientSecret: String = "212476d9b0f3472eaa762d90b19b0ba8",
)
// FlyerPlus: Spotify sign-in (Authorization Code + PKCE)
const val SPOTIFY_LOGIN_ACTION = "flyerplus.spotify.login"
const val SPOTIFY_REDIRECT_URI = "flyerplus://spotify-auth"
