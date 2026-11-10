package com.shabinder.common.providers.spotify

import com.shabinder.common.models.spotify.Album
import com.shabinder.common.models.spotify.Artist
import com.shabinder.common.models.spotify.Image
import com.shabinder.common.models.spotify.Track
import com.shabinder.common.utils.globalJson
import io.ktor.client.*
import io.ktor.client.request.*
import io.ktor.http.*
import kotlinx.serialization.json.*

/*
 * FlyerPlus: reads Spotify's public embed page, so no API key or quota is needed.
 * The embed page lists up to 100 playlist tracks; longer playlists are paged with the
 * page's own anonymous token. If that paging ever stops working, the first 100 are kept.
 */

internal class EmbedResult(val title: String, val coverUrl: String, val tracks: List<Track>)

private const val UA =
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Mobile Safari/537.36"
private const val FETCH_PLAYLIST_HASH = "19ff1327c29e99c208c86d7a9d8f1929cfdf3d3202a0ff4253c821f1901aa94d"
private val NEXT_DATA = Regex("""<script id="__NEXT_DATA__" type="application/json">(.*?)</script>""", RegexOption.DOT_MATCHES_ALL)

private operator fun JsonElement?.get(key: String): JsonElement? = (this as? JsonObject)?.get(key)
private val JsonElement?.list get() = (this as? JsonArray).orEmpty()
private val JsonElement?.str get() = (this as? JsonPrimitive)?.contentOrNull
private val JsonElement?.num get() = (this as? JsonPrimitive)?.longOrNull ?: 0L

private fun JsonElement?.bestImage(): String =
    list.maxByOrNull { maxOf(it["width"].num, it["maxWidth"].num) }?.get("url").str ?: ""

private fun idOf(uri: String?) = uri?.substringAfterLast(':')

private fun track(
    name: String?, artists: List<String>, durationMs: Long, uri: String?,
    albumName: String?, cover: String, trackNumber: Int = 0, releaseDate: String? = null
) = Track(
    name = name,
    artists = artists.map { Artist(name = it) },
    duration_ms = durationMs,
    uri = uri,
    href = idOf(uri)?.let { "https://open.spotify.com/track/$it" },
    track_number = trackNumber,
    album = Album(name = albumName, images = listOf(Image(url = cover)), release_date = releaseDate)
)

internal suspend fun HttpClient.spotifyEmbed(type: String, id: String): EmbedResult {
    val html = get<String>("https://open.spotify.com/embed/$type/$id") {
        header(HttpHeaders.UserAgent, UA)
        header(HttpHeaders.Accept, "text/html")
    }
    val json = NEXT_DATA.find(html)?.groupValues?.get(1)
        ?: throw IllegalStateException("Couldn't read this Spotify link (page format changed)")
    val state = globalJson.parseToJsonElement(json)["props"]["pageProps"]["state"]
    val entity = state["data"]["entity"] ?: throw IllegalStateException("Spotify link not found or private")

    val title = entity["name"].str ?: entity["title"].str ?: ""
    val cover = entity["coverArt"]["sources"].bestImage().ifEmpty { entity["visualIdentity"]["image"].bestImage() }
    val releaseDate = entity["releaseDate"]["isoString"].str?.take(10)

    val tracks = when (type) {
        "track" -> listOf(
            track(title, entity["artists"].list.mapNotNull { it["name"].str }, entity["duration"].num,
                entity["uri"].str, null, cover, releaseDate = releaseDate)
        )
        else -> {
            val albumName = if (type == "album") title else null
            val fromEmbed = entity["trackList"].list.mapIndexed { i, t ->
                track(t["title"].str, t["subtitle"].str.orEmpty().split(',').map { it.trim() }.filter { it.isNotEmpty() },
                    t["duration"].num, t["uri"].str, albumName, cover, i + 1, releaseDate)
            }
            if (type == "playlist" && fromEmbed.size >= 100) {
                val token = state["settings"]["session"]["accessToken"].str
                runCatching { fullPlaylist(id, token!!) }.getOrNull()?.takeIf { it.size > fromEmbed.size } ?: fromEmbed
            } else fromEmbed
        }
    }
    return EmbedResult(title, cover, tracks)
}

private suspend fun HttpClient.fullPlaylist(id: String, token: String): List<Track> {
    val all = mutableListOf<Track>()
    var offset = 0
    while (true) {
        val body = get<String>("https://api-partner.spotify.com/pathfinder/v1/query") {
            header(HttpHeaders.Authorization, "Bearer $token")
            header(HttpHeaders.UserAgent, UA)
            parameter("operationName", "fetchPlaylist")
            parameter("variables", """{"uri":"spotify:playlist:$id","offset":$offset,"limit":100}""")
            parameter("extensions", """{"persistedQuery":{"version":1,"sha256Hash":"$FETCH_PLAYLIST_HASH"}}""")
        }
        val content = globalJson.parseToJsonElement(body)["data"]["playlistV2"]["content"]
        val page = content["items"].list
        page.forEach { item ->
            val t = item["itemV2"]["data"]
            if (t["__typename"].str == "Track") all += track(
                t["name"].str, t["artists"]["items"].list.mapNotNull { it["profile"]["name"].str },
                t["trackDuration"]["totalMilliseconds"].num, t["uri"].str,
                t["albumOfTrack"]["name"].str, t["albumOfTrack"]["coverArt"]["sources"].bestImage(),
                t["trackNumber"].num.toInt()
            )
        }
        offset += page.size
        if (page.size < 100 || offset >= content["totalCount"].num) return all
    }
}
