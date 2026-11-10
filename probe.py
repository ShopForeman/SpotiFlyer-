import re, json, urllib.request, urllib.error
UA={"User-Agent":"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130 Mobile Safari/537.36"}
def get(u,h={}):
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers={**UA,**h}),timeout=30); return r.status,r.read().decode()
    except urllib.error.HTTPError as e: return e.code,e.read().decode()[:300]
pid="37i9dQZF1DX4UtSsGT1Sbe"
s,h=get(f"https://open.spotify.com/embed/playlist/{pid}")
d=json.loads(re.search(r'__NEXT_DATA__" type="application/json">(.*?)</script>',h,re.S).group(1))
ses=d["props"]["pageProps"]["state"]["settings"]["session"]
tok=ses["accessToken"]; print("anon",ses["isAnonymous"],"tok len",len(tok or ""))
A={"Authorization":"Bearer "+tok}
for u in [f"https://api.spotify.com/v1/playlists/{pid}?fields=name,tracks.total,items.total",
          f"https://api.spotify.com/v1/playlists/{pid}/tracks?offset=100&limit=5",
          f"https://api.spotify.com/v1/playlists/{pid}/items?offset=100&limit=5",
          "https://api.spotify.com/v1/playlists/77svwHNhW9x3ezazzBAcFd/tracks?limit=2"]:
    s,b=get(u,A); print(u,s,b[:400].replace("\n"," "))
# pathfinder graphql
for pl in [pid]:
    q={"operationName":"fetchPlaylist","variables":json.dumps({"uri":f"spotify:playlist:{pl}","offset":100,"limit":100}),
       "extensions":json.dumps({"persistedQuery":{"version":1,"sha256Hash":"19ff1327c29e99c208c86d7a9d8f1929cfdf3d3202a0ff4253c821f1901aa94d"}})}
    import urllib.parse
    s,b=get("https://api-partner.spotify.com/pathfinder/v1/query?"+urllib.parse.urlencode(q),A); print("pathfinder",s)
    j=json.loads(b); c=j["data"]["playlistV2"]["content"]; print("total",c.get("totalCount"),"n",len(c["items"]),"pagingInfo",c.get("pagingInfo")); print(json.dumps(c["items"][0]["itemV2"],indent=1)[:3000])
