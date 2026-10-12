import json,sys,time,glob,os,requests
D=os.path.dirname(os.path.abspath(__file__)); out=[]
files=sys.argv[1:] or sorted(glob.glob(D+"/0*.*"))
for p in files:
    p=p if os.path.isabs(p) else os.path.join(D,p)
    t=time.time(); r=requests.post("http://localhost:8080/api/analyze",files={"file":(os.path.basename(p),open(p,"rb"))},timeout=180); dt=time.time()-t
    j=r.json(); c=j["case"]; e=c["extraction"]
    print(f"== {os.path.basename(p)} mode={j['mode']} {dt:.1f}s score={c['overall_risk_score']} sev={c['severity']}")
    print("  ", {k:e.get(k) for k in ("vendor","vendor_tin","invoice_number","date","subtotal","tax","total")})
    for f in c["risk_flags"]: print("   -",f["code"],f["severity"],"|",f["title"],"|",f["explanation"][:140])
