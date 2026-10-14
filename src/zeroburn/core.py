"""Core routing, budgets, and verified-solution memory. Standard-library only."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from hashlib import sha256
import json, os, sqlite3, time
from pathlib import Path
from typing import Any

@dataclass
class Task:
    goal: str
    budget_units: int = 100
    max_attempts: int = 3
    category: str = "general"

@dataclass
class Decision:
    route: str
    reason: str
    estimated_units: int
    cache_key: str

def normalize_goal(goal: str) -> str:
    return " ".join(goal.casefold().strip().split())

def task_key(goal: str, category: str = "general") -> str:
    return sha256(f"{category}:{normalize_goal(goal)}".encode()).hexdigest()

class EvidenceLedger:
    """SQLite ledger. A solution is reusable only after explicit verification."""
    def __init__(self, path: str | Path = "data/zero_burn.sqlite3"):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS solutions (
                cache_key TEXT PRIMARY KEY, goal TEXT NOT NULL, result TEXT NOT NULL,
                evidence TEXT NOT NULL, verified INTEGER NOT NULL, created_at REAL NOT NULL,
                hits INTEGER NOT NULL DEFAULT 0)""")
            db.execute("""CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, goal TEXT NOT NULL, route TEXT NOT NULL,
                status TEXT NOT NULL, units INTEGER NOT NULL, detail TEXT NOT NULL,
                created_at REAL NOT NULL)""")
    def _connect(self):
        db=sqlite3.connect(self.path)
        db.row_factory=sqlite3.Row
        return db
    def get_verified(self, key: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row=db.execute("SELECT * FROM solutions WHERE cache_key=? AND verified=1",(key,)).fetchone()
            if not row: return None
            db.execute("UPDATE solutions SET hits=hits+1 WHERE cache_key=?",(key,))
            return dict(row)
    def save(self, goal: str, result: str, evidence: dict[str, Any], verified: bool,
             category: str = "general") -> None:
        key=task_key(goal,category)
        with self._connect() as db:
            db.execute("""INSERT INTO solutions(cache_key,goal,result,evidence,verified,created_at)
            VALUES(?,?,?,?,?,?) ON CONFLICT(cache_key) DO UPDATE SET result=excluded.result,
            evidence=excluded.evidence,verified=excluded.verified,created_at=excluded.created_at""",
            (key,goal,result,json.dumps(evidence),int(verified),time.time()))
    def record_run(self, goal: str, route: str, status: str, units: int, detail: str="") -> None:
        with self._connect() as db:
            db.execute("INSERT INTO runs(goal,route,status,units,detail,created_at) VALUES(?,?,?,?,?,?)",
                       (goal,route,status,units,detail[:2000],time.time()))
    def stats(self) -> dict[str, int]:
        with self._connect() as db:
            runs=db.execute("SELECT COUNT(*) n, COALESCE(SUM(units),0) units FROM runs").fetchone()
            cached=db.execute("SELECT COUNT(*) n, COALESCE(SUM(hits),0) hits FROM solutions WHERE verified=1").fetchone()
            return {"runs":runs["n"],"units_used":runs["units"],"verified_solutions":cached["n"],"cache_hits":cached["hits"]}

def choose_route(task: Task, ledger: EvidenceLedger) -> Decision:
    if not normalize_goal(task.goal):
        raise ValueError("Task goal cannot be empty")
    key=task_key(task.goal,task.category)
    if ledger.get_verified(key):
        return Decision("verified_memory","Exact verified solution found",0,key)
    # Safe local-first default. Model calls require a configured adapter and explicit opt-in.
    goal=normalize_goal(task.goal)
    deterministic_hints=("format json","count words","uppercase","lowercase","sort alphabetically")
    if any(hint in goal for hint in deterministic_hints):
        return Decision("local_tool","Task appears deterministic; use a local operation first",0,key)
    return Decision("local_plan","No verified solution; start with local diagnosis and escalate only with evidence",0,key)

def run_local_task(task: Task, ledger: EvidenceLedger) -> dict[str, Any]:
    decision=choose_route(task,ledger)
    cached=ledger.get_verified(decision.cache_key) if decision.route=="verified_memory" else None
    if cached:
        ledger.record_run(task.goal,decision.route,"cache_hit",0,"Verified prior result reused")
        return {"ok":True,"route":decision.route,"result":cached["result"],"evidence":json.loads(cached["evidence"]),"units":0}
    goal=task.goal.strip()
    low=goal.casefold()
    result=None
    if low.startswith("uppercase:"):
        result=goal.split(":",1)[1].strip().upper()
    elif low.startswith("lowercase:"):
        result=goal.split(":",1)[1].strip().lower()
    elif low.startswith("count words:"):
        result=str(len(goal.split(":",1)[1].split()))
    elif low.startswith("sort alphabetically:"):
        result=", ".join(sorted((x.strip() for x in goal.split(":",1)[1].split(",")),key=str.casefold))
    if result is not None:
        evidence={"verifier":"deterministic local operation","passed":True}
        ledger.save(task.goal,result,evidence,True,task.category)
        ledger.record_run(task.goal,"local_tool","success",0,"Deterministic operation verified")
        return {"ok":True,"route":"local_tool","result":result,"evidence":evidence,"units":0}
    ledger.record_run(task.goal,decision.route,"needs_model","0","No provider adapter configured; no paid call was made")
    return {"ok":False,"route":decision.route,"result":None,
            "message":"This task needs a model or a custom tool. No paid API was called.",
            "next_step":"Configure an adapter or break the task into verifiable local steps.",
            "budget_units":max(0,int(task.budget_units))}

def env_config():
    return {"host":os.getenv("ZERO_BURN_HOST","127.0.0.1"),
            "port":int(os.getenv("ZERO_BURN_PORT","8787")),
            "db":os.getenv("ZERO_BURN_DB","./data/zero_burn.sqlite3"),
            "max_attempts":int(os.getenv("ZERO_BURN_MAX_ATTEMPTS","3")),
            "budget_units":int(os.getenv("ZERO_BURN_BUDGET_UNITS","100"))}
