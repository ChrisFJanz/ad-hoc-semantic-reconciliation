"""Keeping bindings: the events and the mechanisms that need no model call."""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _paths  # noqa: E402,F401
from _paths import CASES, RESULTS  # noqa: E402
from reconcile.instance import load_instance_case  # noqa: E402

from matching import keeping as D  # noqa: E402

CASE = load_instance_case(CASES / "instance_ipnet_small")
RULES = json.loads((RESULTS / "model-step" / "term_rules.json").read_text())["rules"]
BIND = json.loads((CASES / "config_ipnet" / "data_binding.json").read_text())


def _first(kind):
    return D.candidates(CASE, kind, random.Random(1), 1)[0]


def test_matched_network_has_no_void_binding_and_no_alarm():
    st = D.initial_state(CASE)
    assert not D.void_bindings(st)
    for f in (D.on_use(st), D.identifiers(st, CASE, RULES, BIND), D.relations(st), D.observation(st)):
        assert not f.flagged


def test_rename_voids_one_binding_and_every_mechanism_notices():
    st = D.apply(CASE, "rename", _first("rename"))
    assert len(D.void_bindings(st)) == 1
    assert D.on_use(st).flagged == D.void_bindings(st)


def test_rekey_of_lookalikes_is_silent_to_identifiers_and_found_by_observation():
    st = D.apply(CASE, "rekey_lookalike", _first("rekey_lookalike"))
    void = D.void_bindings(st)
    assert len(void) == 2
    assert not D.on_use(st).flagged
    assert not D.identifiers(st, CASE, RULES, BIND).flagged
    obs = D.observation(st)
    assert obs.flagged == void
    assert all(D.true_rebinding(st)[a] == b for a, b in obs.repairs.items()) and set(obs.repairs) == void


def test_relations_narrow_and_observation_settles():
    st = D.apply(CASE, "rekey_lookalike", _first("rekey_lookalike"))
    rel = D.relations(st)
    assert D.void_bindings(st) < rel.flagged                 # found, with the far ends implicated too
    narrowed = D.observation(st, only=rel.flagged)
    assert narrowed.flagged == D.void_bindings(st)
    assert narrowed.cost["observations"] == len(rel.flagged) < len(st.bindings)


def test_a_rekey_and_a_cable_swap_look_the_same_in_the_sides_own_record():
    """The side where two look-alike handles were re-keyed sees, in its own record, exactly what it
    would see had the two cables been exchanged. One voids two bindings and the other voids none."""
    s, t1, t2 = "a", *_first("cable_swap")
    rekey = D.apply(CASE, "rekey_lookalike", (s, t1, t2))
    swap = D.apply(CASE, "cable_swap", (t1, t2))
    assert D.published(rekey.a) == D.published(swap.a)
    assert len(D.void_bindings(rekey)) == 2 and not D.void_bindings(swap)


def test_identifiers_on_a_stale_record_propose_wrong_repairs():
    inst = _first("move_address")
    fresh = D.apply(CASE, "move_address", inst)
    stale = D.apply(CASE, "move_address", inst, stale="b")
    assert not D.identifiers(fresh, CASE, RULES, BIND).flagged
    f = D.identifiers(stale, CASE, RULES, BIND)
    assert len(f.flagged) == 2 and not D.void_bindings(stale)
    assert all(D.true_rebinding(stale)[a] != b for a, b in f.repairs.items())
    assert not D.observation(stale).flagged


def test_changes_that_void_nothing_raise_no_alarm_on_fresh_records():
    for kind in ("readdress", "move_address", "cable_swap"):
        st = D.apply(CASE, kind, _first(kind))
        assert not D.void_bindings(st)
        for f in (D.on_use(st), D.identifiers(st, CASE, RULES, BIND), D.relations(st), D.observation(st)):
            assert not f.flagged, kind
