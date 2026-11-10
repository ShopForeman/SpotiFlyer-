package com.shabinder.common.providers.spotify

import com.shabinder.common.core_components.utils.buildHttpClient
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertTrue

/** FlyerPlus: live check that Spotify's public page still parses (run in CI). */
class SpotifyEmbedTest {
    private val client = buildHttpClient {}

    private fun check(type: String, id: String, minTracks: Int) = runBlocking {
        val r = client.spotifyEmbed(type, id)
        println("$type $id -> '${r.title}', ${r.tracks.size} tracks, first: ${r.tracks.firstOrNull()?.name} / ${r.tracks.firstOrNull()?.artists?.map { it?.name }}")
        assertTrue(r.title.isNotBlank() && r.tracks.size >= minTracks && r.tracks.all { !it.name.isNullOrBlank() && it.duration_ms > 0 })
    }

    @Test fun playlist() = check("playlist", "77svwHNhW9x3ezazzBAcFd", 1)
    @Test fun longPlaylist() = check("playlist", "37i9dQZF1DX4UtSsGT1Sbe", 101)
    @Test fun album() = check("album", "4aawyAB9vmqN3uQ7FjRGTy", 2)
    @Test fun track() = check("track", "11dFghVXANMlKmJXsNCbNl", 1)
}
