"""Offline checks for the staged two-agent instance stack. A scripted pair of agents that only
uses what is in its own payload stands in for the model: A proposes the true counterpart of
each of its individuals when that counterpart is in B's catalogue, B ratifies. The checks are
on the staging itself: what each dialogue contains, that nothing hidden leaks, and that the
stages add up to the whole alignment."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.instance import load_instance_case                                    # noqa: E402
from matching.two_agent import Proposal, Ratification          # noqa: E402
from matching.two_agent_staged import (                         # noqa: E402
    StagedTwoAgentInstanceStack, _Scope, ANCHOR_TYPE)
from test_two_agent import _Completion                                                # noqa: E402


class ScriptedAgents:
    """An OpenAI-shaped client. It reads the payload it is sent and answers from it alone."""

    def __init__(self, case, careless=False, forgetful=False, deaf=False):
        self.forgetful = forgetful   # A leaves two bundle-member ports out of its proposals
        self.deaf = deaf             # ... and ignores the closing check
        self.careless = careless     # A guesses look-alike bundle members the wrong way round, at first
        self.members = {i["id"] for i in case.a if any(r["rel"] == "higher-layer-if" for r in i["rels"])}
        self.sib = {}
        for i in case.a:
            low = [r["target"] for r in i["rels"] if r["rel"] == "lower-layer-if"]
            if len(low) == 2:
                self.sib[low[0]], self.sib[low[1]] = low[1], low[0]
        self.truth = case.truth
        self.calls = []
        self.chat = self
        self.completions = self

    def parse(self, model, messages, response_format):
        system, user = messages[0]["content"], messages[1]["content"]
        self.calls.append((system, user))
        payload = json.loads(user)
        mine = [i["id"] for i in payload["your_individuals"]]
        cat_key = next(k for k in payload if k.endswith("_catalogue"))
        theirs = {self.truth[c["id"]]: c["id"] for c in payload[cat_key]}
        side = "A" if cat_key == "agent_B_catalogue" else "B"
        said = payload["transcript_so_far"]
        kw = dict(answers=[], questions=[], proposals=[], ratifications=[], no_counterpart=[], done=True)
        if side == "A" and not said:
            def pick(m):
                if self.careless and m in self.sib and self.sib[m] in mine:
                    return theirs[self.truth[self.sib[m]]]
                return theirs[self.truth[m]]
            skip = set(sorted(m for m in mine if m in self.members)[:2]) if self.forgetful else set()
            kw["proposals"] = [Proposal(my_id=m, their_id=pick(m), confidence=1.0, rationale="x")
                               for m in mine if self.truth[m] in theirs and m not in skip]
        elif side == "A":
            refuted = {c["a_id"] for t in said for c in t.get("confirmation_results", [])
                       if c["ok"] and not c["answer"].get("confirmed")}
            already = {p["my_id"] + p["their_id"] for t in said if t["from"] == "A" for p in t["proposals"]}
            kw["proposals"] = [Proposal(my_id=m, their_id=theirs[self.truth[m]], confidence=1.0, rationale="x")
                               for m in sorted(refuted) if m + theirs[self.truth[m]] not in already]
            kw["done"] = not kw["proposals"]
        if side == "B":
            for t in said:
                if t["from"] == "A":
                    kw["ratifications"] += [Ratification(
                        their_id=p["my_id"], my_id=p["their_id"],
                        accept=self.careless or self.truth[p["my_id"]] == self.truth[p["their_id"]],
                        reason="x") for p in t["proposals"]]
        cc = payload.get("closing_check")
        if cc and not self.deaf:       # account for what is still open: propose it, or say it has no counterpart
            assert "CLOSING CHECK" in cc["note"]
            for m in cc["your_unaccounted_individuals"]:
                if self.truth[m] in theirs:
                    if side == "A":
                        kw["proposals"].append(Proposal(my_id=m, their_id=theirs[self.truth[m]], confidence=1.0, rationale="x"))
                        kw["done"] = False
                else:
                    kw["no_counterpart"].append(m)
        return _Completion(response_format(**kw), 10, 1)


def _run(case_name, batch):
    case = load_instance_case(CASES / case_name)
    client = ScriptedAgents(case)
    stack = StagedTwoAgentInstanceStack(case, model="stub", client=client, max_rounds=2, batch_size=batch)
    return case, client, stack, stack.reconcile("both_cognitive")


def test_scope_uses_own_graph_only():
    case = load_instance_case(CASES / "instance_ipnet_small")
    for inds in (case.a, case.b):
        sc = _Scope(inds)
        assert len(sc.anchors) == 8
        owned = set().union(*[set(m) for m in sc.members.values()])
        assert owned == {i["id"] for i in inds if i["type"] != ANCHOR_TYPE}     # everything is placed
        ports = [i for i in inds if i["type"] == "physical-port"]
        assert all(len(sc.owners[p["id"]]) == 1 for p in ports)                  # a port has one device
        assert all(sc.neighbours[a] for a in sc.anchors)
    sb = _Scope(case.b)
    assert all(len(sb.owners[i["id"]]) == 2 for i in case.b if i["type"] == "link")   # a link attaches to two
    print("ok test_scope_uses_own_graph_only")


def test_stages_cover_the_alignment_small():
    case, client, stack, rec = _run("instance_ipnet_small", 16)
    assert stack.name.endswith("+staged16")
    assert set(rec.proposed) == case.correct_pairs, (len(rec.proposed), len(case.correct_pairs))
    stages = [s for s in rec.transcript if s["step"] == "stage"]
    assert stages[0]["kind"] == "devices" and len(stages) >= 4 and all(s["kind"] == "batch" for s in stages[1:])
    assert all(s["n_a"] <= 16 or len(s["devices_a"]) == 1 for s in stages[1:])
    assert all("_truth" not in u and "_truth" not in s for s, u in client.calls)
    first = json.loads(client.calls[0][1])
    assert {i["type"] for i in first["your_individuals"]} == {ANCHOR_TYPE}
    assert "STAGE: devices" in client.calls[0][0] and "your_device_summaries" in first
    # a batch dialogue: only the batch's devices' individuals, plus context and what is settled
    k = next(i for i, (s, u) in enumerate(client.calls) if "STAGE: components" in s)
    pay = json.loads(client.calls[k][1])
    sa = _Scope(case.a)
    assert all(sa.owners[i["id"]] <= set(pay["batch_devices"]) for i in pay["your_individuals"])
    assert len(pay["settled"]) >= 8
    assert all(c["owned_by"] and not (set(c["owned_by"]) <= set(pay["batch_devices"])) or c["owned_by"]
               for c in pay["context"])
    assert not ({c["id"] for c in pay["context"]} & {i["id"] for i in pay["your_individuals"]})
    print("ok test_stages_cover_the_alignment_small")


def test_stages_cover_the_alignment_large_and_bound_the_turn():
    case, client, stack, rec = _run("instance_ipnet_large", 60)
    assert set(rec.proposed) == case.correct_pairs
    batches = [s for s in rec.transcript if s["step"] == "stage" and s["kind"] == "batch"]
    assert sum(len(s["devices_a"]) for s in batches) == 96
    assert all(s["n_a"] <= 60 or len(s["devices_a"]) == 1 for s in batches)   # no dialogue beyond the batch size
    print("ok test_stages_cover_the_alignment_large_and_bound_the_turn", len(batches),
          max(s["n_a"] for s in batches), max(len(u) for _, u in client.calls))


def test_closing_check_accounts_for_every_individual():
    """Two agents that both declare done while two look-alike ports were never proposed: the protocol does not
    close the conversation; it shows each owner what is unaccounted for, and the ports are then matched. If the
    agents ignore the check, the conversation closes after two reminders and records what was left open."""
    from matching.two_agent import TwoAgentInstanceStack
    case = load_instance_case(CASES / "instance_ipnet_small")
    stack = TwoAgentInstanceStack(case, model="stub", client=ScriptedAgents(case, forgetful=True), max_rounds=3)
    rec = stack.reconcile("both_cognitive")
    assert set(rec.proposed) == case.correct_pairs
    checks = [x for x in rec.transcript if x["step"] == "closing_check"]
    assert checks and len(checks[0]["a"]) == 2 and not [x for x in rec.transcript if x["step"] == "left_open"]
    stack = TwoAgentInstanceStack(case, model="stub", client=ScriptedAgents(case, forgetful=True, deaf=True), max_rounds=3)
    rec = stack.reconcile("both_cognitive")
    left = [x for x in rec.transcript if x["step"] == "left_open"]
    assert len(rec.proposed) == len(case.correct_pairs) - 2 and left and len(left[0]["a"]) == 2
    assert len([x for x in rec.transcript if x["step"] == "closing_check"]) == 2
    print("ok test_closing_check_accounts_for_every_individual")


def test_agreement_is_not_confirmation():
    """A careless pair of agents binds look-alike bundle members the wrong way round and agrees on it.
    Without protocol confirmation the wrong bindings stand; with it they are refuted, withdrawn and
    replaced, in the unstaged and the staged form alike."""
    from matching.two_agent import TwoAgentInstanceStack, _system
    case = load_instance_case(CASES / "instance_ipnet_small")
    plain = TwoAgentInstanceStack(case, model="stub", client=ScriptedAgents(case, careless=True), max_rounds=3)
    rec = plain.reconcile("both_cognitive")
    wrong = set(rec.proposed) - case.correct_pairs
    assert len(wrong) == 12 and rec.oracle_calls["provision"] == 0          # agreed, wrong, untested
    for cls, kw in ((TwoAgentInstanceStack, {}), (StagedTwoAgentInstanceStack, {"batch_size": 16})):
        client = ScriptedAgents(case, careless=True)
        stack = cls(case, model="stub", client=client, max_rounds=3, confirm=True, **kw)
        assert "+confirm" in stack.name
        rec = stack.reconcile("both_cognitive")
        assert set(rec.proposed) == case.correct_pairs, (cls.__name__, len(set(rec.proposed) - case.correct_pairs))
        ops = [s for s in rec.transcript if s["step"] == "virtual_provision"]
        assert all(o["by"] == "protocol" for o in ops)
        assert sum(1 for o in ops if o["result"]["answer"].get("confirmed") is False) == 12
        assert sum(1 for o in ops if o["result"]["answer"].get("confirmed")) == 42     # every port and bundle
        assert "CONFIRMATION:" in client.calls[0][0]
    assert "CONFIRMATION:" not in _system("A", "B", True, True, False)
    print("ok test_agreement_is_not_confirmation")


if __name__ == "__main__":
    test_agreement_is_not_confirmation()
    test_closing_check_accounts_for_every_individual()
    test_scope_uses_own_graph_only()
    test_stages_cover_the_alignment_small()
    test_stages_cover_the_alignment_large_and_bound_the_turn()
