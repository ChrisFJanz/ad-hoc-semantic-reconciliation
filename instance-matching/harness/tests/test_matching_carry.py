"""Offline checks for generate and carry on matched individuals. Scripted agents produce a
right and a wrong matching; the carry must tell them apart, and the round trip must not."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.instance import load_instance_case                                          # noqa: E402
from matching.carry import carry, correspondences_from_transcript, generate      # noqa: E402
from matching.two_agent import TwoAgentInstanceStack                 # noqa: E402
from test_matching_two_agent_staged import ScriptedAgents                                  # noqa: E402


def test_carry_tells_right_from_wrong_and_round_trip_does_not():
    case = load_instance_case(CASES / "instance_ipnet_small")
    out = {}
    for confirm in (False, True):
        stack = TwoAgentInstanceStack(case, model="stub", client=ScriptedAgents(case, careless=True),
                                      max_rounds=3, confirm=confirm)
        rec = stack.reconcile("both_cognitive")
        corr = correspondences_from_transcript(case, rec.transcript)
        assert corr == set(rec.proposed)                 # the saved transcript yields the run's own result
        tr = generate(case, corr)
        assert len(tr["a_to_b"]) == len(tr["b_to_a"]) == 50
        out[confirm] = carry(case, tr)
    wrong, right = out[False], out[True]
    assert wrong["instructions"] == right["instructions"] == 42          # every port and bundle
    assert wrong["wrong_component"] == 12 and wrong["same_component"] == 30
    assert wrong["round_trip_ok"] == 42                                  # the round trip sees nothing wrong
    assert right["wrong_component"] == 0 and right["same_component"] == 42 and right["round_trip_ok"] == 42
    bad = next(r for r in wrong["rows"] if not r["same_component"])
    assert bad["named_component"] != bad["responded_component"] and bad["carried"]["operation"] == "take-out-of-service"
    print("ok test_carry_tells_right_from_wrong_and_round_trip_does_not")


if __name__ == "__main__":
    test_carry_tells_right_from_wrong_and_round_trip_does_not()


def test_live_experiment_is_non_disruptive_and_decisive():
    """The live experiment compares recorded data through each handle; it never operates the component."""
    from matching.network_check import OperationOracle
    from matching.two_agent import _system
    from matching.two_agent_staged import StagedTwoAgentInstanceStack
    case = load_instance_case(CASES / "instance_ipnet_small")
    b_of = {i["_truth"]: i["id"] for i in case.b}
    members = [i["id"] for i in case.a if any(r["rel"] == "higher-layer-if" for r in i["rels"])]
    m1, m2 = members[0], members[1]
    net = OperationOracle(case, "both_cognitive"); net.live = True
    ok = net.virtual_provision(m1, b_of[case.truth[m1]])
    no = net.virtual_provision(m1, b_of[case.truth[m2]])
    assert ok.answer["confirmed"] and ok.answer["recorded_through_A"] == ok.answer["recorded_through_B"]
    assert not no.answer["confirmed"] and no.answer["recorded_through_A"] != no.answer["recorded_through_B"]
    assert "recorded" in ok.message and net.calls["provision"] == 2
    p = _system("A", "B", operations=True, interrogation=True, services=False, confirm=True, live=True)
    assert "LIVE OBSERVATION" in p and "does nothing to the network" in p and "out of service through" not in p
    assert "puts it to the live observation" in p and "experiment" not in p.lower()
    q = _system("A", "B", operations=True, interrogation=True, services=False, confirm=True)
    assert "VIRTUAL EXPERIMENT" in q and "OBSERVATION" not in q and "puts it to the virtual experiment" in q
    client = ScriptedAgents(case, careless=True)
    stack = StagedTwoAgentInstanceStack(case, model="stub", client=client, max_rounds=3, confirm=True,
                                        experiment="live", batch_size=16)
    assert "+live+confirm" in stack.name
    rec = stack.reconcile("both_cognitive")
    assert set(rec.proposed) == case.correct_pairs
    assert "LIVE OBSERVATION" in client.calls[0][0]
    assert "observations" in stack.turn_model.model_fields and "experiments" not in stack.turn_model.model_fields
    ops = [s for s in rec.transcript if s["step"] == "virtual_provision"]
    assert all("recorded_through_A" in o["result"]["answer"] for o in ops) and len(ops) == 54
    print("ok test_live_experiment_is_non_disruptive_and_decisive")


def test_anchor_first_and_targeted_confirmation():
    """Identity anchors settle what a shared identifier settles, with no conversation. Each side's look-alikes
    are found mechanically. Careless agents that swap look-alikes are caught by testing the look-alikes only."""
    import json
    from matching.anchor import anchor_join, lookalike_classes, withhold, shuffled
    from matching.two_agent_staged import StagedTwoAgentInstanceStack
    from matching.two_agent import _system
    sdir = CASES / "config_ipnet"
    binding = json.loads((sdir / "data_binding.json").read_text())
    rules = [{"a_id": "a.rid", "b_id": "b.rid", "value_rule": "identity"}, {"a_id": "a.ip", "b_id": "b.ip", "value_rule": "identity"},
             {"a_id": "a.speed", "b_id": "b.rate", "value_rule": "scale"}, {"a_id": "a.if", "b_id": "b.tp", "value_rule": "not-a-value"}]
    case = load_instance_case(CASES / "instance_ipnet_small")
    pairs, why = anchor_join(case, rules, binding)
    assert len(pairs) == 38 and all(case.truth[a] == case.truth[b] for a, b in pairs.items())
    la = lookalike_classes(case.a, set(pairs))
    members = {i["id"] for i in case.a if any(r["rel"] == "higher-layer-if" for r in i["rels"])}
    assert {x for g in la for x in g} == members and all(len(g) == 2 for g in la)      # exactly the bundle members
    assert lookalike_classes(shuffled(case, 7).a, set(pairs)) == la                    # order is not evidence
    client = ScriptedAgents(case, careless=True)
    stack = StagedTwoAgentInstanceStack(case, model="stub", client=client, max_rounds=3, confirm="lookalikes",
                                        batch_size=60).use_anchors(pairs)
    assert "+confirm-lookalikes" in stack.name and stack.name.endswith("+anchors")
    rec = stack.reconcile("both_cognitive")
    assert set(rec.proposed) == case.correct_pairs
    ops = [s for s in rec.transcript if s["step"] == "virtual_provision"]
    assert len(ops) == 24 and sum(1 for o in ops if not o["result"]["answer"]["confirmed"]) == 12   # 12 refuted, 12 confirmed
    assert not [s for s in rec.transcript if s["step"] == "stage" and s["kind"] == "devices"]       # no device conversation
    first = json.loads(client.calls[0][1])
    assert {i["id"] for i in first["your_individuals"]} <= members                     # only the open individuals come up
    assert first["your_lookalikes"] and "your_settled_records" in first and "LOOK-ALIKES:" in client.calls[0][0]
    assert "LOOK-ALIKES:" not in _system("A", "B", True, True, False, confirm=True)
    # with addresses withheld, the anchors are the devices alone and topology has work to do
    cw = withhold(case)
    p2, _ = anchor_join(cw, rules, binding)
    assert len(p2) == 8
    client2 = ScriptedAgents(cw)
    rec2 = StagedTwoAgentInstanceStack(cw, model="stub", client=client2, max_rounds=3, confirm="lookalikes",
                                       batch_size=60).use_anchors(p2).reconcile("both_cognitive")
    assert set(rec2.proposed) == cw.correct_pairs
    n_la = len({x for g in lookalike_classes(cw.a, set(p2)) for x in g})
    assert n_la == 16 and len([s for s in rec2.transcript if s["step"] == "virtual_provision"]) <= 2 * n_la
    print("ok test_anchor_first_and_targeted_confirmation")
