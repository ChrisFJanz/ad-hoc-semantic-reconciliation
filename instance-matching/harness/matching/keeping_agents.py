"""Keeping bindings, with agents: a batch of changes happens, and the agents bring the bindings up to date.

Two agents hold the bindings made at matching time. Then the network and the two systems change: handles are
renamed and re-keyed, a port is decommissioned, addresses change and move, cables are exchanged. Some of
these void bindings and some do not. Each agent sees only its own side. What it knows about a change depends
on the condition:

  log        its system gives it a change log (what was renamed, what was re-keyed, what was done to the
             network), and it can compare its own record before and after
  record     it can only compare its own record before and after
  record_check  as 'record', with two additions. A binding whose handle a record change touches must be
             observed and found to be one component before its agent may declare done. And an observation that
             finds a pair to be one component closes the binding mechanically: the harness sets the binding to
             that pair, whichever side's handles moved, and the pair is settled. A handle that such a repair
             leaves without a partner is paired provisionally with the handle left over on the other side, and
             that binding must be observed in turn. The rule is not limited
             to look-alike handles: two of B's ports can differ in B's own record (one is the source of its
             link and the other the destination) and a re-keying of them still reads there as a cable move.
  one_inert  B is inert: there is one reasoner, A's agent. It has A's change log and A's record, and B's
             published record before and after. Nothing can be read through B's handles, so no observation.

On its turn an agent says, for ITS OWN handles only, which handle now denotes the component that an old
handle denoted, and which components are gone. Each side is the authority on its own handles, so these take
effect at once. With an agent on each side, a bound pair can be put to a live observation: data the network
has recorded is read through both handles and compared. An agent can also say that it cannot tell whether a
binding still holds; that binding is then left open, which is counted apart from a binding that is wrong.

Scoring is against the truth the case carries, per change and for the table as a whole.
"""
from __future__ import annotations

import json
import random
import time
from typing import Literal

from pydantic import BaseModel, Field

from reconcile.instance import InstanceCase

from matching import keeping as D
from matching.anchor import anchor_join, lookalike_classes
from matching.two_agent import _effort_from_usage

KINDS = ["rename", "rekey_distinct", "rekey_lookalike", "decommission", "readdress", "move_address", "cable_swap"]
SIDES = [("b", "a", "b"), ("a", "b", "a"), ("b", "b", "b")]     # per trial: side of the rename, of each re-keying


# --------------------------------------------------------------------------------------- the episode
def _facts(ind: dict) -> dict:
    return {"type": ind["type"], "attrs": ind["attrs"],
            "rels": sorted([r["rel"], r["target"]] for r in ind["rels"])}


def build_episode(case: InstanceCase, trial: int, seed: int = 11) -> dict:
    """One change of each kind, on components that do not touch each other, applied one after another.
    Returns the states before and after, what each side's system logs, and what each change did."""
    rng = random.Random(seed * 100 + trial)
    before = D.initial_state(case)
    st, used, events = before, set(), []
    by_truth_a = {i["_truth"]: i for i in before.a}
    ida = {i["id"]: i for i in before.a}

    def touched(truths):
        out = set(truths)
        for t in truths:                                  # a port's neighbour is touched with it
            for r in by_truth_a[t]["rels"]:
                if r["rel"] in ("lldp-neighbour", "higher-layer-if", "lower-layer-if"):
                    out.add(ida[r["target"]]["_truth"])
        return out

    sides = dict(zip(("rename", "rekey_distinct", "rekey_lookalike"), SIDES[trial % len(SIDES)]))
    for kind in KINDS:
        for inst in D.candidates(case, kind, rng, 10_000):
            if kind in sides:
                if inst[0] != sides[kind]:
                    continue
                truths = [by_truth_a[next(i["_truth"] for i in before.side(inst[0]) if i["id"] == inst[1])]["_truth"]] \
                    if kind == "rename" else list(inst[1:])
                if kind == "rename" and by_truth_a[truths[0]]["type"] != D.PORT:
                    continue
            else:
                truths = list(inst)
            if touched(truths) & used:
                continue
            used |= touched(truths)
            handles = {s: [st.handle_of(s, t) for t in truths] for s in ("a", "b")}
            st = D.apply_to(st, kind, inst)
            ev = {"kind": kind, "side": inst[0] if kind in sides else None, "components": truths, "handles_before": handles}
            if kind == "rename":
                ev["new_handle"] = st.log[-1]["new"]
            events.append(ev)
            break
        else:
            raise RuntimeError("no instance of %s left that touches nothing already changed" % kind)
    return {"before": before, "after": st, "events": events}


def change_log(ep: dict, s: str) -> list[dict]:
    """What side ``s``'s own system reports to its agent, in that side's handles."""
    out = []
    for ev in ep["events"]:
        k, h = ev["kind"], ev["handles_before"][s]
        if k == "rename" and ev["side"] == s:
            out.append({"event": "this system renamed a handle", "old_handle": h[0], "new_handle": ev["new_handle"]})
        elif k in ("rekey_distinct", "rekey_lookalike") and ev["side"] == s:
            out.append({"event": "this system re-keyed two handles: each now denotes the component the other denoted",
                        "handles": h})
        elif k == "decommission":
            out.append({"event": "a port was removed from the network", "handle": h[0]})
        elif k == "readdress":
            out.append({"event": "the address of a port was changed in the network", "handle": h[0]})
        elif k == "move_address":
            out.append({"event": "two ports exchanged their addresses in the network", "handles": h})
        elif k == "cable_swap":
            out.append({"event": "the cables on two ports were exchanged in the network", "handles": h})
    return out


def touched_handles(ep: dict, s: str) -> set[str]:
    """Handles of side ``s`` that a change in its record touches: the handle's own facts changed, or a relation to
    it appeared or disappeared anywhere in the record."""
    b0 = {i["id"]: i for i in D.published(ep["before"].side(s))}
    b1 = {i["id"]: i for i in D.published(ep["after"].side(s))}
    out = set()
    for h in set(b0) | set(b1):
        r0 = {(r["rel"], r["target"]) for r in b0[h]["rels"]} if h in b0 else set()
        r1 = {(r["rel"], r["target"]) for r in b1[h]["rels"]} if h in b1 else set()
        out |= {t for _, t in r0 ^ r1}
        if h in b0 and h in b1 and _facts(b0[h]) != _facts(b1[h]):
            out.add(h)
    return out & set(b1)


def record_changes(ep: dict, s: str) -> dict:
    """What side ``s`` sees by comparing its own record before and after, with the facts."""
    b0 = {i["id"]: i for i in D.published(ep["before"].side(s))}
    b1 = {i["id"]: i for i in D.published(ep["after"].side(s))}
    return {"handles_gone": [{"handle": h, "facts_before": _facts(b0[h])} for h in sorted(set(b0) - set(b1))],
            "handles_new": [{"handle": h, "facts_now": _facts(b1[h])} for h in sorted(set(b1) - set(b0))],
            "handles_with_changed_facts": [{"handle": h, "before": _facts(b0[h]), "now": _facts(b1[h])}
                                           for h in sorted(set(b0) & set(b1)) if _facts(b0[h]) != _facts(b1[h])]}


# ----------------------------------------------------------------------------------------- the turn
class HandleChange(BaseModel):
    old_handle: str      # one of YOUR handles, as it stands in the bindings
    new_handle: str      # YOUR handle that now denotes the component old_handle denoted
    reason: str


class Observation(BaseModel):
    my_handle: str
    their_handle: str


class Turn(BaseModel):
    say: str = ""                                            # to the other agent: questions, answers, what you found
    my_handle_changes: list[HandleChange] = Field(default_factory=list)
    my_removed: list[str] = Field(default_factory=list)      # your handles whose component is gone from the network
    observations: list[Observation] = Field(default_factory=list)
    cannot_tell: list[str] = Field(default_factory=list)     # your handles whose binding you cannot vouch for
    done: bool = False


class TurnNoObservation(BaseModel):
    say: str = ""
    my_handle_changes: list[HandleChange] = Field(default_factory=list)
    my_removed: list[str] = Field(default_factory=list)
    cannot_tell: list[str] = Field(default_factory=list)
    done: bool = False


class SideChange(BaseModel):
    side: Literal["A", "B"]
    old_handle: str
    new_handle: str
    reason: str


class ReasonerTurn(BaseModel):
    handle_changes: list[SideChange] = Field(default_factory=list)
    removed: list[str] = Field(default_factory=list)         # handles, of either side, whose component is gone
    cannot_tell: list[str] = Field(default_factory=list)     # handles, of either side, whose binding cannot be vouched for
    notes: str = ""


BASICS = (
    "A BINDING pairs one of agent A's handles with one of agent B's handles and says that the two denote one "
    "component of the network (a router, a port, a bundle). It holds while both handles still denote that same "
    "component. The bindings were made earlier and were all correct then. Since then the network and the two "
    "systems have changed. Your task is to bring the bindings up to date: every binding that no longer holds must "
    "be corrected or removed, and every binding that still holds must be left as it is.\n"
    "Keep two things apart. (1) A handle can come to denote ANOTHER component: a system renames a handle, or "
    "re-keys its handles so that a handle now denotes a component that another handle denoted. That changes "
    "bindings. (2) The facts recorded about a component can change while the handle still denotes the same "
    "component: an address is changed or moved, a cable is moved to another port. That changes no binding. "
    "A change in recorded facts is evidence, and it can be consistent with either. Look-alike handles (listed for "
    "you where given) are handles of yours that no recorded fact tells apart: for those, a record alone can never "
    "say which of the two things happened.\n")


def _system_agent(side: str, other: str, condition: str, observe: bool) -> str:
    s = (f"You are agent {side}. You hold only system {side}'s record. Agent {other} holds only system {other}'s.\n" + BASICS +
         "You are given the current bindings, what changed in YOUR OWN record (handles gone, handles new, handles "
         "whose recorded facts changed, with the facts before and now)")
    s += (", and the change log of your own system, which states what your system and the network operators did. "
          "The log is authoritative for what it states.\n" if condition == "log" else
          ". Your system gives you no change log: you know what your record shows, and not why.\n")
    s += ("You act on YOUR OWN handles only. In my_handle_changes, give old_handle and new_handle when the component "
          "that old_handle denoted is now denoted by new_handle; this rewrites the binding at once, so give it only "
          "when you know it. For an exchange between two handles give both directions in the same turn. In my_removed, "
          "list handles whose component is gone from the network. Use 'say' to tell the other agent what it needs to "
          "know and to ask what you need to know; it sees only its own side.\n")
    if observe:
        s += ("You can put a pair to a LIVE OBSERVATION: data the network has recorded is read through your handle and "
              "through one of the other agent's handles and compared. The same data means one component; different "
              "data means two. It does nothing to the network. The result comes back to both of you. Use it where the "
              "records cannot settle whether a binding holds, and to find where a handle now belongs.\n")
    if condition == "record_check":
        s += ("RULE: a change in your record is evidence and not a verdict. Where it touches one of your bound handles "
              "(the handle's own facts changed, or a relation to it appeared or disappeared), the binding of that handle "
              "must be put to a live observation and found to be one component before you declare done. "
              "When an observation finds a pair of handles to be one component, the binding is set to that pair "
              "automatically, whichever side's handles moved, and it is then settled: you do not rewrite it yourself, and a "
              "rewrite that would change a settled binding is ignored. So where a binding is found to be void, observe the "
              "candidates for its handles until one is found to be one component. A handle that such a repair leaves without a "
              "partner is paired provisionally with the handle left over on the other side, and that binding must be "
              "observed too. Use cannot_tell only for a binding that no observation can settle. "
              "You will be reminded of any that remain.\n")
    s += ("If, after that, you cannot tell whether a binding of one of your handles still holds, list the handle in "
          "cannot_tell: a binding left open is better than a binding that is wrong. Set done to true when you have "
          "nothing more to do or to ask.")
    return s


SYSTEM_REASONER = (
    "You are agent A. System B has no agent: it only publishes its record. You hold system A's record and its "
    "change log, and system B's published record before and now.\n" + BASICS +
    "A's change log states what system A and the network operators did, and is authoritative for what it states. "
    "For system B you know only what its record shows, and not why. Nothing can be read through B's handles, so "
    "no binding can be put to an observation.\n"
    "In handle_changes, give side, old_handle and new_handle when the component that old_handle denoted is now "
    "denoted by new_handle on that side; give it only when the evidence determines it. For an exchange between "
    "two handles give both directions. In removed, list handles of either side whose component is gone. If you "
    "cannot tell whether a binding still holds, list one of its handles in cannot_tell: a binding left open is "
    "better than a binding that is wrong.")


# ---------------------------------------------------------------------------------------- the stack
class KeepBindings:
    def __init__(self, case: InstanceCase, model: str, condition: str, term_rules: list[dict], data_binding: dict,
                 client=None, max_rounds: int = 4):
        assert condition in ("log", "record", "record_check", "one_inert")
        self.case, self.model, self.condition, self.max_rounds, self._client = case, model, condition, max_rounds, client
        anchors, _ = anchor_join(case, term_rules, data_binding)
        self._anchors = anchors

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def _lookalikes(self, ep: dict, s: str) -> list[list[str]]:
        now = {i["id"] for i in ep["after"].side(s)}
        anchored = {h for h in (self._anchors if s == "a" else self._anchors.values()) if h in now}
        return lookalike_classes(ep["after"].side(s), anchored)

    def _call(self, system: str, payload: dict, fmt):
        t0 = time.time()
        c = self._get_client().chat.completions.parse(
            model=self.model, messages=[{"role": "system", "content": system},
                                        {"role": "user", "content": json.dumps(payload, indent=1)}],
            response_format=fmt)
        eff = _effort_from_usage(getattr(c, "usage", None))
        eff["latency_s"] = round(time.time() - t0, 2)
        return c.choices[0].message.parsed, eff

    def run(self, trial: int) -> dict:
        ep = build_episode(self.case, trial)
        rows = [[a, b] for a, b in ep["before"].bindings.items()]       # the table the agents keep
        transcript, open_handles = [], set()
        tot = {"total_tokens": 0, "reasoning_tokens": 0, "latency_s": 0.0, "turns": 0, "observations": 0}

        settled = set()                                               # pairs closed by observation: protected (record_check)

        def rewrite(col: int, changes: list[tuple[str, str]]) -> list[str]:
            m, ignored = dict(changes), []
            for r in rows:
                if r[col] in m and (r[0], r[1]) in settled:
                    ignored.append(r[col]); continue
                r[col] = m.get(r[col], r[col])
            return ignored

        def remove(handles) -> list[str]:
            ignored = [h for r in rows if (r[0], r[1]) in settled for h in r if h in handles]
            rows[:] = [r for r in rows if (r[0], r[1]) in settled or (r[0] not in handles and r[1] not in handles)]
            return ignored

        def add(eff):
            for k in ("total_tokens", "reasoning_tokens", "latency_s"):
                tot[k] += eff[k]
            tot["turns"] += 1

        if self.condition == "one_inert":
            payload = {"bindings_A_handle_B_handle": rows, "A_change_log": change_log(ep, "a"),
                       "A_record_changes": record_changes(ep, "a"), "B_record_changes": record_changes(ep, "b"),
                       "A_lookalike_handles": self._lookalikes(ep, "a"), "B_lookalike_handles": self._lookalikes(ep, "b")}
            turn, eff = self._call(SYSTEM_REASONER, payload, ReasonerTurn)
            add(eff)
            for col, side in ((0, "A"), (1, "B")):
                rewrite(col, [(c.old_handle, c.new_handle) for c in turn.handle_changes if c.side == side])
            remove(set(turn.removed))
            open_handles |= set(turn.cannot_tell)
            transcript.append({"from": "A", **turn.model_dump()})
        else:
            fmt = Turn
            done = {"a": False, "b": False}
            checked = set()                                           # pairs (A handle, B handle) observed to be one component
            must = {s: touched_handles(ep, s) if self.condition == "record_check" else set() for s in ("a", "b")}

            now = {x: {i["id"] for i in ep["after"].side(x)} for x in ("a", "b")}

            def close(a: str, b: str) -> list[dict]:
                """Set the binding to the observed pair. A handle that this leaves without a partner on each side is
                paired provisionally with the one left on the other side, and must be observed in turn."""
                left_b = [r[1] for r in rows if r[0] == a and r[1] != b]
                left_a = [r[0] for r in rows if r[1] == b and r[0] != a]
                rows[:] = [r for r in rows if r[0] != a and r[1] != b]
                rows.append([a, b])
                settled.add((a, b))
                open_handles.difference_update({a, b})
                out = [{"settled": [a, b]}]
                live_a = [h for h in left_a if h in now["a"]]               # a handle its own side still records
                live_b = [h for h in left_b if h in now["b"]]
                if len(live_a) == 1 and len(live_b) == 1 and not any(r[0] == live_a[0] or r[1] == live_b[0] for r in rows):
                    rows.append([live_a[0], live_b[0]])
                    must["a"].add(live_a[0]); must["b"].add(live_b[0])
                    out.append({"provisional": [live_a[0], live_b[0]]})
                return out

            def unmet(s, col):
                return sorted(r[col] for r in rows if r[col] in must[s] and (r[0], r[1]) not in checked
                              and not ({r[0], r[1]} & open_handles))
            for rnd in range(self.max_rounds + (2 if self.condition == "record_check" else 0)):   # room for the reminders
                for s, col in (("a", 0), ("b", 1)):
                    S, O = s.upper(), ("B" if s == "a" else "A")
                    payload = {"bindings": [{"my_handle": r[col], "their_handle": r[1 - col]} for r in rows],
                               "my_record_changes": record_changes(ep, s),
                               "my_lookalike_handles": self._lookalikes(ep, s)}
                    if self.condition == "log":
                        payload["my_change_log"] = change_log(ep, s)
                    if unmet(s, col) and rnd > 0:
                        payload["reminder_bindings_still_to_observe_or_leave_open"] = unmet(s, col)
                    payload["transcript_so_far"] = transcript
                    turn, eff = self._call(_system_agent(S, O, self.condition, True), payload, fmt)
                    reminded = payload.get("reminder_bindings_still_to_observe_or_leave_open")
                    add(eff)
                    ignored = rewrite(col, [(c.old_handle, c.new_handle) for c in turn.my_handle_changes])
                    ignored += remove(set(turn.my_removed))
                    open_handles |= set(turn.cannot_tell)
                    results, closed = [], []
                    for o in turn.observations:
                        a, b = (o.my_handle, o.their_handle) if s == "a" else (o.their_handle, o.my_handle)
                        ra, rb = D.recorded(ep["after"], a), D.recorded(ep["after"], b)
                        tot["observations"] += 1
                        if ra is not None and ra == rb:
                            checked.add((a, b))                      # only a pair found to be one component is settled
                            if self.condition == "record_check" and (a, b) not in settled:
                                closed += close(a, b)
                        results.append({"A_handle": a, "B_handle": b,
                                        "result": ("a handle does not resolve" if ra is None or rb is None else
                                                   "same data: one component" if ra == rb else
                                                   "different data: two components")})
                    entry = {"from": S, **turn.model_dump()}
                    if results:
                        entry["observation_results"] = results
                    if reminded:
                        entry["was_reminded_of"] = reminded
                    if closed:
                        entry["closed_by_observation"] = closed
                    if ignored:
                        entry["rewrites_ignored_settled"] = sorted(set(ignored))
                    transcript.append(entry)
                    done[s] = turn.done and not turn.observations and not unmet(s, col)
                if all(done.values()):
                    break
        return {"condition": self.condition, "trial": trial, "events": ep["events"], "final_bindings": rows,
                "left_open": sorted(open_handles), "transcript": transcript, "effort": tot,
                "score": score(ep, rows, open_handles)}


def score(ep: dict, rows: list[list[str]], open_handles: set[str]) -> dict:
    """Against the truth: per change, and for the whole table."""
    after = ep["after"]
    truth = after.truth()
    right = D.true_rebinding(after)                               # A handle -> B handle, for every component still there
    held = {}
    dup = set()
    for a, b in rows:
        if a in held:
            dup.add(a)
        held[a] = b
    used_b = [b for _, b in rows]
    dup |= {a for a, b in rows if used_b.count(b) > 1}

    def state_of(t: str) -> str:
        a = after.handle_of("a", t)
        if a is None:                                             # the component is gone: no row should remain
            old = _old_handles(ep, t)
            if not any(r[0] in old or r[1] in old for r in rows):
                return "right"
            return "left_open" if old & open_handles else "wrong"
        if held.get(a) == right[a] and a not in dup:
            return "right"
        if a in open_handles or right[a] in open_handles or held.get(a) in open_handles:
            return "left_open"
        return "wrong"

    per_event = []
    for ev in ep["events"]:
        states = [state_of(t) for t in ev["components"]]
        per_event.append({"kind": ev["kind"], "side": ev["side"],
                          "outcome": "wrong" if "wrong" in states else "left_open" if "left_open" in states else "right"})
    comps = sorted(right)
    n_right = sum(1 for a in comps if held.get(a) == right[a] and a not in dup)
    n_open = sum(1 for a in comps if not (held.get(a) == right[a] and a not in dup)
                 and (a in open_handles or right[a] in open_handles or held.get(a) in open_handles))
    stale_rows = sum(1 for a, b in rows if a not in truth or b not in truth)
    return {"per_event": per_event, "bindings_expected": len(comps), "bindings_right": n_right,
            "bindings_left_open": n_open, "bindings_wrong": len(comps) - n_right - n_open,
            "rows_with_a_dead_handle": stale_rows}


def _old_handles(ep, t: str) -> set[str]:
    """The handles a component had before the changes, on both sides."""
    old = set()
    for ev in ep["events"]:
        if t in ev["components"]:
            i = ev["components"].index(t)
            old |= {ev["handles_before"]["a"][i], ev["handles_before"]["b"][i]}
    return old
