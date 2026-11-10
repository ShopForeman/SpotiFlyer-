import json, urllib.request
def post(url, body, headers={}):
    h={"Content-Type":"application/json","User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36",**headers}
    return json.loads(urllib.request.urlopen(urllib.request.Request(url,json.dumps(body).encode(),h),timeout=30).read())
q="Oops!...I Did It Again - Britney Spears"
for params in [None,"EgWKAQIIAWoKEAkQBRAKEAMQBA%3D%3D"]:  # second = Songs filter
    b={"context":{"client":{"clientName":"WEB_REMIX","clientVersion":"1.20251103.01.00","hl":"en","gl":"US"}},"query":q}
    if params: b["params"]=params.replace("%3D","=")
    j=post("https://music.youtube.com/youtubei/v1/search?prettyPrint=false",b,{"Origin":"https://music.youtube.com","Referer":"https://music.youtube.com/"})
    print("=== params",params)
    sec=j["contents"]["tabbedSearchResultsRenderer"]["tabs"][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"]
    print(json.dumps(sec[0])[:2500])
    print("...")
    print(json.dumps(sec[1])[:2500])
    print("TYPES",[ (k, list(v.keys())) for b2 in sec[:3] for k,v in b2.items()])
