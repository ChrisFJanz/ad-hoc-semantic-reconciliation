"""Keeping bindings with agents: the episode, the turn-taking and the scoring, with scripted agents."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _paths  # noqa: E402,F401
from _paths import CASES, RESULTS  # noqa: E402
from reconcile.instance import load_instance_case  # noqa: E402

from matching import keeping as D  # noqa: E402
from matching import keeping_agents as G  # noqa: E402

CASE = load_instance_case(CASES / "instance_ipnet_small")
RULES = json.loads((RESULTS / "model-step" / "term_rules.json").read_text())["rules"]
BIND = json.loads((CASES / "config_ipnet" / "data_binding.json").read_text())


class Scripted:
    """An OpenAI-shaped client. ``mode``: 'log' follows its change log exactly; 'idle' does nothing;
    'observe' follows no log and puts every binding of a handle whose facts changed to an observation."""

    def __init__(self, mode, truth=None, rewrite_back=False):
        self.mode, self.calls, self.seen = mode, 0, set()
        self.truth, self.rewrite_back = truth or {}, rewrite_back
        self.chat = self
        self.completions = self

    def parse(self, model, messages, response_format):
        self.calls += 1
        p = json.loads(messages[1]["content"])
        if response_format is G.ReasonerTurn:
            ch, rem = [], []
            for e in p["A_change_log"]:
                if "renamed" in e["event"]:
                    ch.append(G.SideChange(side="A", old_handle=e["old_handle"], new_handle=e["new_handle"], reason="log"))
                elif "re-keyed" in e["event"]:
                    h1, h2 = e["handles"]
                    ch += [G.SideChange(side="A", old_handle=h1, new_handle=h2, reason="log"),
                           G.SideChange(side="A", old_handle=h2, new_handle=h1, reason="log")]
                elif "removed" in e["event"]:
                    rem.append(e["handle"])
            turn = G.ReasonerTurn(handle_changes=ch, removed=rem)
        elif self.mode == "idle":
            turn = G.Turn(done=True)
        elif self.mode == "cross":
            # observes the bindings it is reminded of, or whose handles changed, and for each also the other side's
            # handle that is truly the same component (a test double may know the truth); it rewrites nothing itself,
            # unless rewrite_back, when it then tries to undo every repair the harness made
            mine = {b["my_handle"]: b["their_handle"] for b in p["bindings"]}
            ch = p["my_record_changes"]
            todo = set(p.get("reminder_bindings_still_to_observe_or_leave_open", []))
            todo |= {c["handle"] for c in ch["handles_with_changed_facts"]} | {c["handle"] for c in ch["handles_new"]}
            todo -= self.seen
            self.seen |= todo
            obs = []
            for h in sorted(todo):
                if h in mine:
                    obs.append(G.Observation(my_handle=h, their_handle=mine[h]))
                for o, t in self.truth.items():
                    if t == self.truth.get(h) and o != h and o[0] != h[0] and mine.get(h) != o:
                        obs.append(G.Observation(my_handle=h, their_handle=o))
            changes = []
            if self.rewrite_back and not obs:
                for t in p["transcript_so_far"]:
                    for c in t.get("closed_by_observation", []):
                        if "settled" in c:
                            mine_h = c["settled"][0] if p["bindings"] and p["bindings"][0]["my_handle"].startswith("a.") else c["settled"][1]
                            changes.append(G.HandleChange(old_handle=mine_h, new_handle=mine_h + "-undo", reason="test"))
            gone = [c["handle"] for c in ch["handles_gone"] if c["handle"] in mine]   # its own handles that no longer resolve
            turn = G.Turn(observations=obs, my_handle_changes=changes, my_removed=gone, done=not obs)
        elif self.mode == "observe":
            mine = {b["my_handle"]: b["their_handle"] for b in p["bindings"]}
            asked = bool(p["transcript_so_far"])
            todo = p.get("reminder_bindings_still_to_observe_or_leave_open", [])
            again = [h for h in todo if h in self.seen]          # observed already and still not settled: leave open
            obs = [G.Observation(my_handle=h, their_handle=mine[h]) for h in todo if h not in self.seen] if asked else \
                [G.Observation(my_handle=c["handle"], their_handle=mine[c["handle"]])
                 for c in p["my_record_changes"]["handles_with_changed_facts"] if c["handle"] in mine]
            self.seen |= {o.my_handle for o in obs}
            turn = G.Turn(observations=obs, cannot_tell=again, done=asked and not obs)
        else:
            ch, rem = [], []
            for e in p.get("my_change_log", []):
                if "renamed" in e["event"]:
                    ch.append(G.HandleChange(old_handle=e["old_handle"], new_handle=e["new_handle"], reason="log"))
                elif "re-keyed" in e["event"]:
                    h1, h2 = e["handles"]
                    ch += [G.HandleChange(old_handle=h1, new_handle=h2, reason="log"),
                           G.HandleChange(old_handle=h2, new_handle=h1, reason="log")]
                elif "removed" in e["event"]:
                    rem.append(e["handle"])
            turn = G.Turn(my_handle_changes=ch, my_removed=rem, done=True)
        usage = SimpleNamespace(total_tokens=len(messages[0]["content"] + messages[1]["content"]) // 4,
                                completion_tokens_details=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(parsed=turn))], usage=usage)


def _run(condition, mode, trial=0, case=CASE, **kw):
    return G.KeepBindings(case, "stub", condition, RULES, BIND, client=Scripted(mode, **kw)).run(trial)


def test_episode_has_one_change_of_each_kind_and_six_void_bindings():
    for trial in range(3):
        ep = G.build_episode(CASE, trial)
        assert [e["kind"] for e in ep["events"]] == G.KINDS
        assert len(D.void_bindings(ep["after"])) == 6          # 1 renamed, 2 + 2 re-keyed, 1 decommissioned


def test_agents_that_follow_their_logs_end_with_every_binding_right():
    for trial in range(3):
        r = _run("log", "log", trial)
        sc = r["score"]
        assert sc["bindings_right"] == sc["bindings_expected"] == 49 and sc["rows_with_a_dead_handle"] == 0
        assert all(e["outcome"] == "right" for e in sc["per_event"])
        assert len(r["final_bindings"]) == 49


def test_agents_that_do_nothing_leave_the_void_bindings_wrong_and_the_rest_right():
    sc = _run("record", "idle")["score"]
    out = {e["kind"]: e["outcome"] for e in sc["per_event"]}
    assert out == {"rename": "wrong", "rekey_distinct": "wrong", "rekey_lookalike": "wrong", "decommission": "wrong",
                   "readdress": "right", "move_address": "right", "cable_swap": "right"}
    assert sc["bindings_wrong"] == 5 and sc["rows_with_a_dead_handle"] == 2


def test_observations_are_answered_from_the_network_and_counted():
    r = _run("record", "observe")
    results = [o["result"] for t in r["transcript"] for o in t.get("observation_results", [])]
    assert r["effort"]["observations"] == len(results) > 0
    assert any(x.startswith("different") for x in results) and any(x.startswith("same") for x in results)


def test_one_inert_reasoner_with_only_its_own_log_misses_what_the_inert_side_did():
    sc = _run("one_inert", "log", trial=2)["score"]            # trial 2: the rename and both re-keyings are on B
    out = {e["kind"]: e["outcome"] for e in sc["per_event"]}
    assert out["decommission"] == "right" and out["rename"] == "wrong" and out["rekey_lookalike"] == "wrong"


def test_required_check_names_the_handles_a_record_change_touches():
    ep = G.build_episode(CASE, 0)                                  # trial 0: the look-alike re-keying is on B
    rekeyed = next(e for e in ep["events"] if e["kind"] == "rekey_lookalike")["handles_before"]
    swapped = set(next(e for e in ep["events"] if e["kind"] == "cable_swap")["handles_before"]["b"])
    touched = G.touched_handles(ep, "b")
    assert set(rekeyed["b"]) <= touched and swapped <= touched
    assert not G.touched_handles(ep, "a") & set(rekeyed["a"])       # nothing changed in A's record there
    k = G.KeepBindings(CASE, "stub", "record_check", RULES, BIND, client=Scripted("idle"))
    in_b_lookalikes = {h for g in k._lookalikes(ep, "b") for h in g}
    assert not set(rekeyed["b"]) & in_b_lookalikes                 # B's own record tells the two apart, and yet ...
    swap = D.apply(CASE, "cable_swap", tuple(next(e for e in ep["events"] if e["kind"] == "rekey_lookalike")["components"]))
    rekey = D.apply(CASE, "rekey_lookalike", ("b",) + tuple(next(e for e in ep["events"] if e["kind"] == "rekey_lookalike")["components"]))
    assert D.published(swap.b) == D.published(rekey.b)             # ... a re-keying reads there exactly as a cable move


def test_agents_that_ignore_the_required_check_are_reminded_and_never_declared_done():
    r = _run("record_check", "idle")
    reminded = [t["was_reminded_of"] for t in r["transcript"] if t.get("was_reminded_of")]
    rekeyed = set(next(e for e in r["events"] if e["kind"] == "rekey_lookalike")["handles_before"]["b"])
    assert reminded and any(rekeyed <= set(x) for x in reminded)
    assert r["effort"]["turns"] == 12                              # six rounds, never accepted as done


def test_required_check_is_met_by_observing_or_leaving_open_and_then_agents_are_done():
    r = _run("record_check", "observe")                            # observes what it is reminded of, repairs nothing
    assert r["effort"]["turns"] < 12
    sc = r["score"]
    out = {e["kind"]: e["outcome"] for e in sc["per_event"]}
    assert out["rekey_lookalike"] == "left_open" and out["rekey_distinct"] == "left_open"   # found void, left open: not wrong
    assert out["cable_swap"] == out["move_address"] == out["readdress"] == "right"


def _truth(trial):
    return G.build_episode(CASE, trial)["after"].truth()


def test_an_observation_closes_the_binding_with_no_rewrite_by_either_agent():
    for trial in range(3):
        r = _run("record_check", "cross", trial, truth=_truth(trial))
        sc = r["score"]
        assert sc["bindings_right"] == sc["bindings_expected"] and sc["bindings_left_open"] == 0, (trial, sc)
        assert all(e["outcome"] == "right" for e in sc["per_event"]) and sc["rows_with_a_dead_handle"] == 0
        assert not any(t["my_handle_changes"] for t in r["transcript"])          # no agent rewrote anything
        assert any(t.get("closed_by_observation") for t in r["transcript"])


def test_a_rewrite_of_a_settled_binding_is_ignored():
    r = _run("record_check", "cross", 0, truth=_truth(0), rewrite_back=True)
    assert any(t.get("rewrites_ignored_settled") for t in r["transcript"])
    assert r["score"]["bindings_right"] == r["score"]["bindings_expected"]


def test_record_only_condition_does_not_close_bindings_mechanically():
    r = _run("record", "cross", 0, truth=_truth(0))
    assert not any(t.get("closed_by_observation") for t in r["transcript"])
    assert r["score"]["bindings_wrong"] > 0                                   # nobody rewrote, nothing closed them
