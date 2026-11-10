package com.shabinder.common.providers.spotify

import com.shabinder.common.providers.utils.CommonUtils
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertEquals

/** FlyerPlus: live check that YouTube Music search still parses and matches (run in CI). */
class YoutubeMusicSearchTest {
    private fun best(title: String, artist: String, durationSec: Int) = runBlocking {
        val tracks = CommonUtils.youtubeMusic.getYTTracks("$title - $artist").component1().orEmpty()
        println("YTM '$title' -> ${tracks.size} results: ${tracks.take(3)}")
        CommonUtils.youtubeMusic.sortByBestMatch(tracks, title, listOf(artist), durationSec).keys.firstOrNull()
    }

    @Test fun oops() = assertEquals("wsHbHR3Os6U", best("Oops!...I Did It Again", "Britney Spears", 211))
    @Test fun psychoKiller() = assertEquals(true, best("Psycho Killer", "Talking Heads", 260) in setOf("NyaOYfpq9Fc", "lX1AjZSYpeM"))

    @Test fun playerInfo() = runBlocking {
        // YouTube blocks GitHub's servers as bots, so this only reports; phones aren't affected.
        val r = runCatching { CommonUtils.youtubeProvider.fetchPlayerAudioLink("wsHbHR3Os6U") }
        println("YT player from CI: " + r.fold({ "OK ${it.second}" }, { it.message }))
    }
}
