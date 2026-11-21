"""The sequence at the inert placements: anchors first, one reasoner over the records, look-alikes left open."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.instance import load_instance_case                                   # noqa: E402
from matching.anchor import anchor_join, lookalike_classes, withhold       # noqa: E402
from matching.single_reasoner import (SequencedReasonerStack, ReplyInert, ReplyOneLive,   # noqa: E402
                                                       Match, Open, Ask, Verdicts, Verdict)
from test_two_agent import _Completion                                               # noqa: E402

RULES = [{"a_id": "a.rid", "b_id": "b.rid", "value_rule": "identity"}, {"a_id": "a.ip", "b_id": "b.ip", "value_rule": "identity"},
         {"a_id": "a.speed", "b_id": "b.rate", "value_rule": "scale"}, {"a_id": "a.if", "b_id": "b.tp", "value_rule": "not-a-value"}]
BINDING = json.loads((CASES / "config_ipnet" / "data_binding.json").read_text())


class ScriptedReasoner:
    """Answers from the payload it is sent. careless: it guesses the look-alikes; forgetful: it leaves two
    open individuals unmentioned until the closing check; curious: it asks A's devices."""

    def __init__(self, case, careless=False, forgetful=False, curious=False, sloppy=False):
        self.truth, self.careless, self.forgetful, self.curious = case.truth, careless, forgetful, curious
        self.sloppy = sloppy         # crosses two topology matches the first time; the verifier is exact
        self.calls = []
        self.chat = self
        self.completions = self

    def parse(self, model, messages, response_format):
        system, user = messages[0]["content"], messages[1]["content"]
        self.calls.append((system, user))
        p = json.loads(user)
        if response_format is Verdicts:      # the independent second reading
            assert "basis" not in user and "your_earlier_replies" not in p
            return _Completion(Verdicts(verdicts=[
                Verdict(a_id=m["a_id"], b_id=m["b_id"], reason="x",
                        verdict="determined" if self.truth[m["a_id"]] == self.truth[m["b_id"]] else "contradicted")
                for m in p["proposed"]]), 10, 1)
        la = {x for g in p["lookalikes_a"] + p["lookalikes_b"] for x in g}
        theirs = {self.truth[i["id"]]: i["id"] for i in p["open_b"]}
        kw = dict(matches=[], left_open=[], no_counterpart=[], done=True)
        if response_format is ReplyOneLive:
            kw["device_questions"] = []
            if self.curious and "device_answers" not in p:
                kw["device_questions"] = [Ask(individual_id=i["id"], attribute="hardware-address")
                                          for i in p["open_a"] if i["id"] in la][:4]
                kw["done"] = False
        skip = set(sorted(i["id"] for i in p["open_a"] if i["id"] not in la)[:2]) if self.forgetful else set()
        if "closing_check" in p:
            skip = set()
        for i in p["open_a"]:
            a = i["id"]
            if a in skip or self.truth[a] not in theirs:
                continue
            if a in la and not self.careless:
                kw["left_open"].append(Open(id=a, reason="look-alike; no check available"))
            else:
                kw["matches"].append(Match(a_id=a, b_id=theirs[self.truth[a]], basis="x", confidence=1.0))
        if self.sloppy and not p.get("verifier_rejections") and len(kw["matches"]) >= 2:
            m0, m1 = kw["matches"][0], kw["matches"][1]
            kw["matches"][0] = Match(a_id=m0.a_id, b_id=m1.b_id, basis="x", confidence=1.0)
            kw["matches"][1] = Match(a_id=m1.a_id, b_id=m0.b_id, basis="x", confidence=1.0)
        a_truths = {self.truth[i["id"]] for i in p["open_a"]}
        a_la_truths = {self.truth[i["id"]] for i in p["open_a"] if i["id"] in la}
        for i in p["open_b"]:
            if self.truth[i["id"]] not in a_truths:
                kw["no_counterpart"].append(i["id"])
            elif (i["id"] in la or self.truth[i["id"]] in a_la_truths) and not self.careless:
                kw["left_open"].append(Open(id=i["id"], reason="look-alike; no check available"))
        return _Completion(response_format(**kw), 10, 1)


def _case(name="instance_ipnet_small", withheld=False):
    case = load_instance_case(CASES / name)
    if withheld:
        case = withhold(case)
    pairs, _ = anchor_join(case, RULES, BINDING)
    return case, pairs


def test_inert_placements_get_what_the_records_determine_and_no_more():
    # addresses present: the anchors leave only look-alikes, and a guess at them is refused
    case, pairs = _case()
    for careless in (False, True):
        client = ScriptedReasoner(case, careless=careless)
        rec = SequencedReasonerStack(case, "stub", "both_inert", pairs, client=client).reconcile()
        assert len(rec.proposed) == 38 and set(rec.proposed) <= case.correct_pairs
        seq = next(s for s in rec.transcript if s["step"] == "sequence")
        assert seq["by_anchor"] == 38 and seq["by_topology"] == 0 and seq["open_a_lookalikes"] == 12
        assert seq["lookalike_matches_refused"] == (12 if careless else 0)
        assert seq["left_open_lookalikes"] == (0 if careless else 12)
    system = client.calls[0][0]
    assert "BOTH RECORDS ARE STATIC" in system and "device_questions" not in system      # advertises only what it has
    assert "_truth" not in client.calls[0][1]
    # addresses withheld: only the devices anchor, topology settles the rest, look-alikes stay open
    cw, p2 = _case(withheld=True)
    n_la = len({x for g in lookalike_classes(cw.a, set(p2)) for x in g})
    rec = SequencedReasonerStack(cw, "stub", "both_inert", p2, client=ScriptedReasoner(cw, careless=True)).reconcile()
    seq = next(s for s in rec.transcript if s["step"] == "sequence")
    assert len(p2) == 8 and n_la == 16 and seq["by_topology"] == 50 - 8 - 16 and seq["lookalike_matches_refused"] == 16
    assert len(rec.proposed) == 34 and set(rec.proposed) <= cw.correct_pairs
    print("ok test_inert_placements_get_what_the_records_determine_and_no_more")


def test_one_live_side_can_ask_its_devices_but_that_settles_nothing_alone():
    case, pairs = _case()
    client = ScriptedReasoner(case, curious=True)
    rec = SequencedReasonerStack(case, "stub", "one_inert", pairs, client=client).reconcile()
    asked = [s for s in rec.transcript if s["step"] == "interrogate"]
    assert len(asked) == 4 and all(s["result"]["ok"] and s["result"]["answer"] for s in asked)
    assert not [s for s in rec.transcript if s["step"] == "device_identifier_join"]      # nothing on B to join with
    assert len(rec.proposed) == 38 and set(rec.proposed) <= case.correct_pairs
    assert "SYSTEM A IS LIVE" in client.calls[0][0] and "device_answers" in client.calls[1][1]
    print("ok test_one_live_side_can_ask_its_devices_but_that_settles_nothing_alone")


def test_closing_check_for_the_reasoner():
    cw, p2 = _case(withheld=True)
    rec = SequencedReasonerStack(cw, "stub", "both_inert", p2, client=ScriptedReasoner(cw, forgetful=True)).reconcile()
    assert [s for s in rec.transcript if s["step"] == "closing_check"] and len(rec.proposed) == 34
    assert not [s for s in rec.transcript if s["step"] == "left_unaccounted"]
    print("ok test_closing_check_for_the_reasoner")


def test_verification_catches_a_crossed_topology_match():
    """A reasoner that crosses two determined matches. Without verification the two wrong matches stand; with it
    they are rejected by the independent reading, returned, and corrected."""
    cw, p2 = _case(withheld=True)
    rec = SequencedReasonerStack(cw, "stub", "both_inert", p2, client=ScriptedReasoner(cw, sloppy=True), verify=False).reconcile()
    assert len(rec.proposed) == 34 and len(set(rec.proposed) - cw.correct_pairs) == 2
    client = ScriptedReasoner(cw, sloppy=True)
    stack = SequencedReasonerStack(cw, "stub", "both_inert", p2, client=client)
    rec = stack.reconcile()
    assert "+verify" in stack.name and "VERIFICATION:" in client.calls[0][0]
    seq = next(s for s in rec.transcript if s["step"] == "sequence")
    assert seq["verifier_rejections"] == 2 and seq["by_topology"] == 26
    assert len(rec.proposed) == 34 and set(rec.proposed) <= cw.correct_pairs
    assert len([s for s in rec.transcript if s["step"] == "verify"]) == 2
    print("ok test_verification_catches_a_crossed_topology_match")


if __name__ == "__main__":
    test_verification_catches_a_crossed_topology_match()
    test_inert_placements_get_what_the_records_determine_and_no_more()
    test_one_live_side_can_ask_its_devices_but_that_settles_nothing_alone()
    test_closing_check_for_the_reasoner()
