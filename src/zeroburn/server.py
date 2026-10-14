"""Local-only HTTP API and static dashboard; no third-party runtime dependencies."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json
from urllib.parse import urlparse
from .core import EvidenceLedger, Task, run_local_task, env_config
from .providers import generate, ProviderError

ROOT=Path(__file__).resolve().parents[2]
WEB=ROOT/"web"
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        self.ledger=EvidenceLedger(env_config()["db"])
        super().__init__(*args,directory=str(WEB),**kwargs)
    def log_message(self,fmt,*args):
        print("%s - %s"%(self.address_string(),fmt%args))
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/health": return self.send_json({"ok":True,"service":"zero-burn-ai"})
        if path=="/api/stats": return self.send_json(self.ledger.stats())
        if path=="/api/config":
            import os
            provider=os.getenv("ZERO_BURN_PROVIDER","").strip().lower()
            return self.send_json({"mode":"local-first","provider":provider or None,
                "provider_calls_enabled":provider in ("ollama","openai-compatible"),
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
            result=run_local_task(task,self.ledger)
            if result.get("ok") or result.get("route")!="local_plan":
                return self.send_json(result)
            # Explicit opt-in only. Local deterministic routes always run before model inference.
            import os
            if not os.getenv("ZERO_BURN_PROVIDER","").strip():
                return self.send_json(result)
            try:
                answer=generate("Solve the user's task. Be concise, state uncertainty, and do not claim tests or actions you did not perform.\n\nTask:\n"+task.goal)
                self.ledger.record_run(task.goal,answer["provider"],"provider_response",0,
                    "Model response returned; not independently verified; cost not available")
                return self.send_json({"ok":True,"route":answer["provider"],"result":answer["text"],
                    "verified":False,"evidence":{"passed":False,"reason":"Model output requires independent verification"},
                    "provider_usage":answer["usage"],"cost_usd":answer["cost_usd"],"notice":answer["notice"]})
            except ProviderError as exc:
                return self.send_json({"ok":False,"route":"provider_error","message":str(exc),
                    "no_result":True,"next_step":"Check provider configuration and service availability."},502)
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
