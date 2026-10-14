"""Local-only HTTP API and static dashboard; no third-party runtime dependencies."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, mimetypes
from urllib.parse import urlparse
from .core import EvidenceLedger, Task, run_local_task, env_config

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/"web"
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        self.ledger=EvidenceLedger(env_config()["db"])
        super().__init__(*args,directory=str(WEB),**kwargs)
    def log_message(self,fmt,*args):
        # Keep local logs useful without echoing request bodies or secrets.
        print("%s - %s"%(self.address_string(),fmt%args))
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/health": return self.send_json({"ok":True,"service":"zero-burn-ai"})
        if path=="/api/stats": return self.send_json(self.ledger.stats())
        if path=="/api/config": return self.send_json({"mode":"local-first","provider_calls_enabled":False,
            "default_budget_units":env_config()["budget_units"],"max_attempts":env_config()["max_attempts"]})
        if path=="/": self.path="/index.html"
        return super().do_GET()
    def do_POST(self):
        if urlparse(self.path).path!="/api/tasks":
            return self.send_json({"error":"Not found"},404)
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length<1 or length>100_000: return self.send_json({"error":"Body must be 1..100000 bytes"},413)
            body=json.loads(self.rfile.read(length))
            task=Task(goal=str(body.get("goal",""))[:4000],
                      budget_units=max(0,min(int(body.get("budget_units",100)),100000)),
                      max_attempts=max(1,min(int(body.get("max_attempts",3)),10)),
                      category=str(body.get("category","general"))[:80])
            return self.send_json(run_local_task(task,self.ledger))
        except (ValueError,TypeError,json.JSONDecodeError) as exc:
            return self.send_json({"error":str(exc)},400)
    def send_json(self,data,status=200):
        raw=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store")
        self.end_headers(); self.wfile.write(raw)

def main():
    cfg=env_config()
    if cfg["host"] not in ("127.0.0.1","localhost","::1"):
        raise SystemExit("Refusing non-local bind without a hardened authenticated deployment.")
    server=ThreadingHTTPServer((cfg["host"],cfg["port"]),Handler)
    print(f"ZERO-BURN AI running at http://{cfg['host']}:{cfg['port']}")
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()
