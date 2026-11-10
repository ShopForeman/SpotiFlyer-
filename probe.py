import json, urllib.request
def post(url, body, headers={}):
    h={"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36",**headers}
    return json.loads(urllib.request.urlopen(urllib.request.Request(url,json.dumps(body).encode(),h),timeout=30).read())
def items(sec):
    for b in sec:
        for k in ("musicShelfRenderer","itemSectionRenderer"):
            for c in b.get(k,{}).get("contents",[]):
                if "musicResponsiveListItemRenderer" in c: yield c["musicResponsiveListItemRenderer"]
for q in ["Oops!...I Did It Again - Britney Spears","Psycho Killer - Talking Heads"]:
  for params in [None,"EgWKAQIIAWoKEAkQBRAKEAMQBA==","EgWKAQIQAWoKEAkQBRAKEAMQBA=="]:
    b={"context":{"client":{"clientName":"WEB_REMIX","clientVersion":"1.20251103.01.00","hl":"en","gl":"US"}},"query":q}
    if params: b["params"]=params
    j=post("https://music.youtube.com/youtubei/v1/search?prettyPrint=false",b,{"Origin":"https://music.youtube.com","Referer":"https://music.youtube.com/"})
    sec=j["contents"]["tabbedSearchResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
    print("===",q,params)
    for r in list(items(sec))[:5]:
        det=[]
        for col in r.get("flexColumns",[]):
            fc=col.get("musicResponsiveListItemFlexColumnRenderer",{})
            if len(fc)<2: continue
            det+=[x["text"] for x in fc.get("text",{}).get("runs",[]) if x["text"]!=" • "]
        vid=r.get("overlay",{}).get("musicItemThumbnailOverlayRenderer",{}).get("content",{}).get("musicPlayButtonRenderer",{}).get("playNavigationEndpoint",{}).get("watchEndpoint",{}).get("videoId")
        print("  ",vid,det)
