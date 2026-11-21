"""Offline checks for the two-agent INSTANCE stack: no API key, a stub client returns scripted
turns. Verifies information asymmetry (each agent's prompt carries only its own individuals in
full, the other side only as a surface catalogue), the propose-then-ratify confirmation, that an
agent may interrogate only its own side and that both see the answer, residual computation, the
virtual-provision override, and that the existing instance scoring applies.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.instance import load_instance_case                                  # noqa: E402
from matching.two_agent import (                             # noqa: E402
    TwoAgentInstanceStack, Turn, Proposal, Ratification, Interrogation, Experiment, Answer, _system)
from test_two_agent import StubClient                                              # noqa: E402
import instance_reconcile as ir                                                    # noqa: E402


def T(**kw):
    base = dict(answers=[], questions=[], proposals=[], ratifications=[], interrogations=[],
                experiments=[], no_counterpart=[], done=False)
    base.update(kw)
    return Turn(**base)


def test_negotiation_on_instance_hard():
    case = load_instance_case(STUDY_CASES / "instance_hard")
    queue = [
        # A: proposes the keyed merge, interrogates its symmetric node, tries to probe B's side
        (T(proposals=[Proposal(my_id="a.r1", their_id="b.roadm1", confidence=0.95, rationale="same key"),
                      Proposal(my_id="a.r1", their_id="b.r1", confidence=0.4, rationale="same name")],
           interrogations=[Interrogation(my_id="a.r2", attribute="serial"),
                           Interrogation(my_id="b.nodeB", attribute="serial")],
           experiments=[Experiment(my_id="a.svc100", their_id="b.svc100"),
                        Experiment(my_id="a.cs_odu2", their_id="b.tunnel1")]), 100, 10),
        # B: ratifies the true merge, rejects the name trap, interrogates its own node, proposes
        (T(ratifications=[Ratification(their_id="a.r1", my_id="b.roadm1", accept=True, reason="key and model agree"),
                          Ratification(their_id="a.r1", my_id="b.r1", accept=False, reason="different device")],
           interrogations=[Interrogation(my_id="b.nodeB", attribute="serial")],
           proposals=[Proposal(my_id="b.nodeB", their_id="a.r2", confidence=0.9, rationale="serial matches")],
           done=True), 120, 12),
        # A: ratifies B's proposal
        (T(ratifications=[Ratification(their_id="b.nodeB", my_id="a.r2", accept=True, reason="serial SN-0022")],
           done=True), 80, 8),
        (T(done=True), 60, 6),
    ]
    client = StubClient(queue)
    stack = TwoAgentInstanceStack(case, model="stub", client=client, max_rounds=4, closing_check=False)
    rec = stack.reconcile("both_cognitive")

    # information asymmetry: A's first prompt holds A's attributes, B's only as a catalogue
    a_user = json.loads(client.calls[0][1]["content"])
    assert {i["id"] for i in a_user["your_individuals"]} == set(case.a_by_id)
    assert all(set(c) <= {"id", "type", "name"} for c in a_user["agent_B_catalogue"])
    assert not any("attrs" in c or "topology" in c for c in a_user["agent_B_catalogue"])
    assert "_truth" not in client.calls[0][1]["content"]

    proposed = set(rec.proposed)
    assert frozenset(("a.r1", "b.roadm1")) in proposed          # proposed by A, ratified by B
    assert frozenset(("a.r2", "b.nodeB")) in proposed           # proposed by B, ratified by A
    assert frozenset(("a.r1", "b.r1")) not in proposed          # rejected by the owner
    assert frozenset(("a.cs_odu2", "b.tunnel1")) in proposed    # confirmed by virtual provision
    assert frozenset(("a.svc100", "b.svc100")) not in proposed  # refuted by virtual provision

    # A could interrogate a.r2 but not b.nodeB; B's own interrogation of b.nodeB succeeded
    probes = [s for s in rec.transcript if s["step"] == "interrogate"]
    assert probes[0]["result"]["answer"] == {"serial": "SN-0022"}
    assert probes[1]["result"]["ok"] is False and "only your own" in probes[1]["result"]["message"]
    assert probes[2]["by"] == "B" and probes[2]["result"]["answer"] == {"serial": "SN-0022"}
    assert rec.oracle_calls == {"interrogate": 2, "provision": 2}
    # the answer A obtained is visible to B on its turn
    assert "SN-0022" in client.calls[1][1]["content"]

    assert rec.effort["turns"] == 4 and rec.effort["total_tokens"] == 360
    row = ir.score_row(case, rec, "stub", None, 0, ir.trap_names(case), ir.FULL_EVIDENCE)
    assert row["precision"] == 1.0 and row["surviving_instance_fc"] == 0
    print("ok test_negotiation_on_instance_hard", {k: row[k] for k in ("proposed", "precision", "recall")})


def test_inert_delegates_to_single_agent():
    case = load_instance_case(STUDY_CASES / "instance_hard")
    from test_instance_loop import FakeClient, _completion, _tool_call
    script = [_completion([_tool_call("c1", "submit_alignment", json.dumps(
        {"correspondences": [{"a_id": "a.r1", "b_id": "b.roadm1", "confidence": 0.9}],
         "residual_a": [], "residual_b": []}))])]
    rec = TwoAgentInstanceStack(case, model="stub", client=FakeClient(script)).reconcile("both_inert")
    assert rec.placement == "both_inert" and frozenset(("a.r1", "b.roadm1")) in set(rec.proposed)
    print("ok test_inert_delegates_to_single_agent")


def test_virtual_operation_on_ports():
    case = load_instance_case(CASES / "instance_ipnet_small")
    truth = case.truth
    # two member ports of one bundle on side A, and their true partners on side B
    members = [i for i in case.a if any(r["rel"] == "higher-layer-if" for r in i["rels"])]
    bundle = next(r["target"] for r in members[0]["rels"] if r["rel"] == "higher-layer-if")
    m1, m2 = [i["id"] for i in members if any(r["target"] == bundle for r in i["rels"])][:2]
    b_of = {i["_truth"]: i["id"] for i in case.b}
    p1, p2 = b_of[truth[m1]], b_of[truth[m2]]
    dev_a = case.a[0]["id"]; dev_b = b_of[truth[dev_a]]
    queue = [
        (T(experiments=[Experiment(my_id=m1, their_id=p2),      # the look-alike: must be refuted
                        Experiment(my_id=m1, their_id=p1),      # the true partner: confirmed
                        Experiment(my_id=dev_a, their_id=dev_b)],  # a device: not operable
           interrogations=[Interrogation(my_id=m1, attribute="hardware-address")], done=True), 10, 1),
        (T(done=True), 10, 1),
    ]
    stack = TwoAgentInstanceStack(case, model="stub", client=StubClient(queue), max_rounds=2, interrogation=False, closing_check=False)
    assert stack.operations and stack.name == "two-agent-instance+op-noint"
    rec = stack.reconcile("both_cognitive")
    ops = [s for s in rec.transcript if s["step"] == "virtual_provision"]
    assert ops[0]["result"]["answer"]["confirmed"] is False and "different component" in ops[0]["result"]["message"]
    assert ops[1]["result"]["answer"]["confirmed"] is True
    assert ops[2]["result"]["ok"] is False
    assert set(rec.proposed) == {frozenset((m1, p1))} and rec.oracle_calls["provision"] == 2
    assert rec.oracle_calls["interrogate"] == 0          # interrogation was withheld
    row = ir.score_row(case, rec, "stub", None, 0, ir.trap_names(case), ir.FULL_EVIDENCE)
    assert row["precision"] == 1.0 and row["confirmed_provision"] == 1
    print("ok test_virtual_operation_on_ports")


def test_format_and_prompt_advertise_exactly_the_tools_available():
    """With a tool withheld, neither the reply format nor the prompt may offer it."""
    case = load_instance_case(CASES / "instance_ipnet_small")
    full = TwoAgentInstanceStack(case, model="stub")
    assert {"interrogations", "experiments"} <= set(full.turn_model.model_fields)
    noint = TwoAgentInstanceStack(case, model="stub", interrogation=False)
    assert "interrogations" not in noint.turn_model.model_fields
    assert "experiments" in noint.turn_model.model_fields
    p = _system("A", "B", noint.operations, noint.interrogation, noint.services)
    assert "'interrogations'" not in p and "hardware-address" not in p and "serial" not in p
    assert "interrogat" not in p.lower() and "DECISIVE VIRTUAL EXPERIMENT" in p and "test, not a" in p
    assert "interrogate" not in p.split("Rules:")[1]
    noop = TwoAgentInstanceStack(case, model="stub", operations=False)
    assert "experiments" not in noop.turn_model.model_fields          # no services, no operation
    q = _system("A", "B", noop.operations, noop.interrogation, noop.services)
    assert "'experiments'" not in q and "'interrogations'" in q
    hard = TwoAgentInstanceStack(load_instance_case(STUDY_CASES / "instance_hard"), model="stub")
    assert hard.services and not hard.operations and "experiments" in hard.turn_model.model_fields
    # a reply in the reduced format parses and runs
    Tn = noint.turn_model
    queue = [(Tn(answers=[], questions=[], proposals=[], ratifications=[], experiments=[],
                 no_counterpart=[], done=True), 5, 1)] * 2
    client = StubClient(queue)
    rec = TwoAgentInstanceStack(case, model="stub", client=client, max_rounds=1, closing_check=False,
                                interrogation=False).reconcile("both_cognitive")
    assert rec.submitted and rec.oracle_calls == {"interrogate": 0, "provision": 0}
    # the instructions actually SENT to each agent are the ones for the tools it has
    for side, other, call in (("A", "B", client.calls[0]), ("B", "A", client.calls[1])):
        sent = call[0]["content"]
        assert sent == _system(side, other, noint.operations, noint.interrogation, noint.services)
        assert "DECISIVE VIRTUAL EXPERIMENT" in sent and "interrogat" not in sent.lower()
    for kw, want in ((dict(), ("'interrogations'", "DECISIVE VIRTUAL EXPERIMENT")),
                     (dict(operations=False), ("'interrogations'",))):
        c = StubClient([(TwoAgentInstanceStack(case, model="stub", **kw).turn_model(
            answers=[], questions=[], proposals=[], ratifications=[], no_counterpart=[], done=True), 5, 1)] * 2)
        TwoAgentInstanceStack(case, model="stub", client=c, max_rounds=1, closing_check=False, **kw).reconcile("both_cognitive")
        assert all(w in c.calls[0][0]["content"] for w in want)
        assert ("DECISIVE VIRTUAL EXPERIMENT" in c.calls[0][0]["content"]) == ("operations" not in kw)
    print("ok test_format_and_prompt_advertise_exactly_the_tools_available")


if __name__ == "__main__":
    test_format_and_prompt_advertise_exactly_the_tools_available()
    test_negotiation_on_instance_hard()
    test_virtual_operation_on_ports()
    test_inert_delegates_to_single_agent()
    print("all two-agent instance offline checks passed")
