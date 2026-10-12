"""Run every sample N times (reset per pass; 08 alone after its own reset) and report score spread / flag-set variance."""
import glob, json, os, sys, requests
A = "http://localhost:8080"; D = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
out = sys.argv[2] if len(sys.argv) > 2 else "/tmp/stability.json"
files = sorted(os.path.basename(p) for p in glob.glob(D + "/[0-9][0-9]-*.*"))
res = {f: [] for f in files}
def run(f):
    try:
        _run(f)
    except Exception as e:  # noqa: BLE001
        res[f].append({"err": type(e).__name__})
    json.dump(res, open(out, "w"), indent=1)
def _run(f):
    r = requests.post(A + "/api/analyze", files={"file": (f, open(os.path.join(D, f), "rb"))}, timeout=300)
    if r.status_code != 200: res[f].append({"err": r.status_code}); return
    c = r.json()["case"]; res[f].append({"score": c["overall_risk_score"], "flags": sorted(f"{x['code']}:{x['severity']}" for x in c["risk_flags"])})
for i in range(N):
    requests.post(A + "/api/reset-demo")
    for f in files:
        if not f.startswith("08"): run(f)
    requests.post(A + "/api/reset-demo"); run([f for f in files if f.startswith("08")][0])
    print("pass", i + 1, flush=True)
json.dump(res, open(out, "w"), indent=1)
print(f"{'sample':32} {'scores':16} spread  flagsets")
for f, rs in res.items():
    sc = [r.get("score") for r in rs]; fs = {tuple(r.get("flags", [])) for r in rs}
    ok = [s for s in sc if s is not None]
    print(f"{f[:32]:32} {str(sc):16} {max(ok)-min(ok) if ok else '-':>5}  {len(fs)}  {' / '.join(','.join(x) for x in fs)[:200]}")
requests.post(A + "/api/reset-demo")
