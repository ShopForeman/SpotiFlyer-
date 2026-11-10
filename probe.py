import re, json, urllib.request, tarfile, io
UA={"User-Agent":"Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130 Mobile Safari/537.36"}
def get(u):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode()
tf=tarfile.open("samples.tgz","w:gz")
for kind,i in [("playlist","77svwHNhW9x3ezazzBAcFd"),("playlist","37i9dQZF1DX4UtSsGT1Sbe"),("album","4aawyAB9vmqN3uQ7FjRGTy"),("track","11dFghVXANMlKmJXsNCbNl")]:
    try:
        h=get(f"https://open.spotify.com/embed/{kind}/{i}")
        b=h.encode(); ti=tarfile.TarInfo(f"{kind}_{i}.html"); ti.size=len(b); tf.addfile(ti,io.BytesIO(b))
        m=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',h,re.S)
        print("==",kind,i,"len",len(h),"nextdata",bool(m))
        if not m: print(h[:1500]); continue
        d=json.loads(m.group(1))
        ent=d["props"]["pageProps"]["state"]["data"]["entity"]
        tl=ent.get("trackList")
        print("entity keys",list(ent.keys()))
        print({k:ent[k] for k in ent if k!="trackList" and k!="visualIdentity"})
        if tl: print("tracks",len(tl)); print(json.dumps(tl[:2],indent=1))
        s=d["props"]["pageProps"]["state"].get("settings",{}).get("session",{})
        print("session keys",list(s.keys()))
    except Exception as e: print("ERR",kind,i,repr(e))
tf.close()
