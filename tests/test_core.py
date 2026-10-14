import pytest
from zeroburn.core import EvidenceLedger, Task, choose_route, run_local_task, task_key

def test_normalized_task_key_is_stable():
    assert task_key("  Hello   WORLD ") == task_key("hello world")

def test_category_is_part_of_key():
    assert task_key("hello","coding") != task_key("hello","research")

def test_empty_goal_rejected(tmp_path):
    ledger=EvidenceLedger(tmp_path/"db.sqlite")
    with pytest.raises(ValueError): choose_route(Task(" "),ledger)
    with pytest.raises(ValueError): run_local_task(Task(" "),ledger)

def test_local_uppercase_is_verified_and_free(tmp_path):
    ledger=EvidenceLedger(tmp_path/"db.sqlite")
    out=run_local_task(Task("UPPERCASE: hello world"),ledger)
    assert out["ok"] and out["result"]=="HELLO WORLD" and out["units"]==0
    assert ledger.stats()["verified_solutions"]==1

def test_verified_result_reused(tmp_path):
    ledger=EvidenceLedger(tmp_path/"db.sqlite")
    task=Task("LOWERCASE: MIXED")
    first=run_local_task(task,ledger); second=run_local_task(task,ledger)
    assert first["result"]==second["result"]=="mixed"
    assert second["route"]=="verified_memory"
    assert ledger.stats()["cache_hits"]==1

def test_unverified_solution_never_reused(tmp_path):
    ledger=EvidenceLedger(tmp_path/"db.sqlite")
    ledger.save("mystery","untrusted",{"passed":False},False)
    assert ledger.get_verified(task_key("mystery")) is None

def test_unknown_task_does_not_call_provider(tmp_path):
    ledger=EvidenceLedger(tmp_path/"db.sqlite")
    out=run_local_task(Task("Design an entire distributed compiler"),ledger)
    assert not out["ok"] and "No paid API was called" in out["message"]
    assert ledger.stats()["units_used"]==0

def test_word_count(tmp_path):
    out=run_local_task(Task("COUNT WORDS: one two three"),EvidenceLedger(tmp_path/"db.sqlite"))
    assert out["result"]=="3"

def test_sort(tmp_path):
    out=run_local_task(Task("SORT ALPHABETICALLY: pear, Apple, banana"),EvidenceLedger(tmp_path/"db.sqlite"))
    assert out["result"]=="Apple, banana, pear"

def test_empty_sort(tmp_path):
    out=run_local_task(Task("SORT ALPHABETICALLY: , ,"),EvidenceLedger(tmp_path/"db.sqlite"))
    assert out["result"]==""

def test_route_unknown_is_local_plan(tmp_path):
    decision=choose_route(Task("Build a compiler"),EvidenceLedger(tmp_path/"db.sqlite"))
    assert decision.route=="local_plan"
