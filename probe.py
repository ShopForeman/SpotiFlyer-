import json, urllib.request, urllib.error, time
def post(url, body, headers={}):
    h={"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36",**headers}
    try:
        r=urllib.request.urlopen(urllib.request.Request(url,json.dumps(body).encode(),h),timeout=30); return r.status,json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code,e.read()[:300]
q="Oops!...I Did It Again - Britney Spears"
for ver in ["1.20251103.01.00","1.20240101.01.00"]:
    s,j=post("https://music.youtube.com/youtubei/v1/search?prettyPrint=false",{"context":{"client":{"clientName":"WEB_REMIX","clientVersion":ver,"hl":"en","gl":"US"}},"query":q},{"Origin":"https://music.youtube.com","Referer":"https://music.youtube.com/"})
    print("SEARCH",ver,s)
    if s!=200: print(j); continue
    tabs=j["contents"]["tabbedSearchResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
    print(" block types",[list(b.keys())[0] for b in tabs])
    for b in tabs:
        for c in b.get("musicShelfRenderer",{}).get("contents",[])[:4]:
            r=c["musicResponsiveListItemRenderer"]
            det=[]
            for col in r.get("flexColumns",[]):
                fc=col.get("musicResponsiveListItemFlexColumnRenderer",{})
                if len(fc)<2: continue
                det+=[x["text"] for x in fc.get("text",{}).get("runs",[]) if x["text"]!=" • "]
            vid=r.get("overlay",{}).get("musicItemThumbnailOverlayRenderer",{}).get("content",{}).get("musicPlayButtonRenderer",{}).get("playNavigationEndpoint",{}).get("watchEndpoint",{}).get("videoId")
            print("  ",vid,det)
    break
VID="CduA0TULnow"
clients={
 "ANDROID_VR":({"clientName":"ANDROID_VR","clientVersion":"1.65.10","deviceMake":"Oculus","deviceModel":"Quest 3","androidSdkVersion":32,"osName":"Android","osVersion":"12L","hl":"en","gl":"US"},"com.google.android.apps.youtube.vr.oculus/1.65.10 (Linux; U; Android 12L; eureka-user Build/SQ3A.220605.009.A1) gzip","28"),
 "IOS":({"clientName":"IOS","clientVersion":"20.10.4","deviceMake":"Apple","deviceModel":"iPhone16,2","osName":"iPhone","osVersion":"18.3.2.22D82","hl":"en","gl":"US"},"com.google.ios.youtube/20.10.4 (iPhone16,2; U; CPU iOS 18_3_2 like Mac OS X;)","5"),
 "ANDROID":({"clientName":"ANDROID","clientVersion":"20.10.38","androidSdkVersion":30,"osName":"Android","osVersion":"11","hl":"en","gl":"US"},"com.google.android.youtube/20.10.38 (Linux; U; Android 11) gzip","3"),
}
for name,(ctx,ua,cid) in clients.items():
    s,j=post("https://www.youtube.com/youtubei/v1/player?prettyPrint=false",{"context":{"client":ctx},"videoId":VID,"contentCheckOk":True,"racyCheckOk":True},{"User-Agent":ua,"X-YouTube-Client-Name":cid,"X-YouTube-Client-Version":ctx["clientVersion"]})
    if s!=200: print("PLAYER",name,s,j); continue
    ps=j.get("playabilityStatus",{}); fm=j.get("streamingData",{}).get("adaptiveFormats",[])
    aud=[f for f in fm if f.get("mimeType","").startswith("audio/")]
    print("PLAYER",name,ps.get("status"),ps.get("reason"),"audio",[(f["itag"],f["mimeType"][:24],f.get("bitrate"),"url" in f) for f in aud])
    a=next((f for f in aud if "url" in f and "mp4" in f["mimeType"]),None)
    if a:
        t=time.time()
        try:
            r=urllib.request.urlopen(urllib.request.Request(a["url"],headers={"User-Agent":ua}),timeout=60); n=len(r.read())
            print("   full GET",r.status,n,"bytes of",a.get("contentLength"),"in %.1fs"%(time.time()-t))
        except Exception as e: print("   GET fail",e)
