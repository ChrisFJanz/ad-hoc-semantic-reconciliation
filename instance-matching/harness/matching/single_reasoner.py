"""The instance-matching sequence where one or both sides are INERT: a single reasoner over the records.

The method applies its tools in a fixed order. Which of them a placement can use depends on where the
cognition is:

  step                                           both inert   one inert        both cognitive
  1  identity anchor (join on shared identifiers)    yes         yes              yes
  2  topology (reasoning over the records)           yes         yes              yes
  3  look-alike detection (from each graph)          yes         yes              yes
  4  ask the other side                              no          no               yes
  5  ask a device for an identifier it can report    no          live side only   both sides
  6  check against the network (experiment on the    no          no               yes
     twin, or live observation)
  7  closing check (every individual accounted for)  reasoner    reasoner         yes

The both-cognitive column is ``TwoAgentInstanceStack`` and its staged form. This module is the other two
columns, run on the SAME sequence, so that the placements can be compared within their own toolkits:

  * steps 1 and 3 are computed before the reasoner is called, exactly as for the two agents
    (``instance_anchor.anchor_join`` and ``lookalike_classes``), and handed to it;
  * the reasoner performs step 2 over what the anchors leave open;
  * every topology match is then VERIFIED: a second, independent reading of the records, which is not shown the
    reasoner's stated basis, says for each proposed match whether the records determine it, contradict it or
    leave it open. Only a match the verifier finds determined counts; the others go back to the reasoner. This
    is the single reasoner's equivalent of ratification by the other agent, which the two agents get by
    construction. Without it, one reasoner can state the right basis and still cross two assignments, and
    nothing catches the slip;
  * the protocol's rule is unchanged: a match that involves a look-alike counts only when it has been
    checked against the network. No check exists here, so such a match is REFUSED and recorded; the
    correct behaviour for an inert placement is to leave every look-alike open and say so;
  * with one side inert, the reasoner may ask the LIVE side's devices for an identifier (step 5). Answers are
    joined mechanically, never read off by the model. With only one side able to ask, a device identifier
    has nothing to be joined with, so it cannot settle a match.

DESIGN DECISION, deliberate: the inert side's published record does NOT include the identifiers that only a
device can report (hardware addresses, serial numbers). If it did, they would be identity anchors and step 1
would close the look-alikes with no check, and the case would no longer test what a live side adds. A system
that publishes such identifiers in its static record is covered by the anchor step, not by this placement.

The result is an ``InstanceReconciliation``, so the existing scoring applies. The client is injectable.
"""
from __future__ import annotations

import json
import time

from pydantic import BaseModel

from reconcile.instance import InstanceCase, Oracle
from matching.anchor import lookalike_classes
from reconcile.stacks.agent_instance import InstanceReconciliation
from matching.two_agent import _private_view, _effort_from_usage

FULL = {"name", "key", "attrs", "rels"}


class Match(BaseModel):
    a_id: str
    b_id: str
    basis: str
    confidence: float


class Open(BaseModel):
    id: str
    reason: str


class Ask(BaseModel):
    individual_id: str
    attribute: str


class Verdict(BaseModel):
    a_id: str
    b_id: str
    verdict: str          # determined | contradicted | undetermined
    reason: str


class Verdicts(BaseModel):
    verdicts: list[Verdict]


class ReplyInert(BaseModel):
    matches: list[Match]
    left_open: list[Open]
    no_counterpart: list[str]
    done: bool


class ReplyOneLive(BaseModel):
    matches: list[Match]
    left_open: list[Open]
    no_counterpart: list[str]
    device_questions: list[Ask]
    done: bool


PREAMBLE = (
    "You are a single reasoner. Two systems, A and B, each hold a record of the SAME network, each in its own "
    "model and with its own names for the routers, ports and bundles. Your task is instance matching: to say "
    "which individual of B is the same real component as each individual of A.\n\n"
    "The method works in a fixed sequence, and you carry out the steps open to you.\n"
    "STEP 1, IDENTITY ANCHORS, is already done: a join on identifiers that both records carry. Its results are "
    "under 'settled' (a_id, b_id), with the records of those individuals under 'settled_records_a' and "
    "'settled_records_b'. They are fixed points; do not revisit them.\n"
    "STEP 2, TOPOLOGY, is yours. The individuals still open are under 'open_a' and 'open_b'. For each open "
    "individual of A, find the individual of B that the RECORDS determine: the same owning device, the same "
    "bundle membership, the same neighbour, each taken relative to what is already settled. Give a match only "
    "where the records leave exactly one candidate, and state the basis.\n"
    "STEP 3, LOOK-ALIKES: 'lookalikes_a' and 'lookalikes_b' list groups of individuals that no recorded fact "
    "tells apart. The order in which individuals are listed is not evidence. A match that involves a look-alike "
    "counts only when it has been checked against the network.\n")

NOTE = {
    "both_inert": (
        "BOTH RECORDS ARE STATIC. You cannot ask either system anything, cannot ask a device, and cannot check a "
        "match against the network. So leave every look-alike open: list it under 'left_open' with the reason. "
        "A guessed match for a look-alike will be refused.\n"),
    "one_inert": (
        "SYSTEM A IS LIVE AND SYSTEM B IS STATIC. You may ask a device of A to report an identifier it holds, "
        "under 'device_questions' (individual_id, attribute); the answers come back under 'device_answers'. B "
        "cannot be asked, and no check against the network is available. An identifier reported by A's device "
        "settles a match only if B's record carries the same identifier; the join is made for you. Otherwise "
        "leave every look-alike open: list it under 'left_open' with the reason. A guessed match for a "
        "look-alike will be refused.\n"),
}

VERIFY_NOTE = (
    "VERIFICATION: each match you give is read again, independently, against the records. A match that this "
    "second reading does not find determined does not count; it comes back to you under 'verifier_rejections' "
    "with the reason, and you may correct it.\n")

VERIFIER = (
    "You are a verifier. Two systems, A and B, each hold a record of the SAME network, each in its own model and "
    "with its own names. Some correspondences are already settled, under 'settled', with the records of those "
    "individuals under 'settled_records_a' and 'settled_records_b'. The individuals still open are under "
    "'open_a' and 'open_b'. Under 'proposed' is a list of proposed matches between an open individual of A and "
    "an open individual of B.\n"
    "Read each proposed match again from the records alone: the owning device, bundle membership and neighbour "
    "of each side, taken relative to what is settled. Follow each relation to its far end and confirm that the "
    "far ends correspond. Give one verdict per proposed match: 'determined' if the records leave this B "
    "individual as the only candidate for this A individual; 'contradicted' if the records point to a different "
    "candidate or rule this one out (say which); 'undetermined' if the records do not decide. The order in which "
    "individuals or matches are listed is not evidence.")

CLOSER = (
    "ACCOUNT FOR EVERY OPEN INDIVIDUAL: each one in 'open_a' and 'open_b' must appear in a match, under "
    "'left_open', or under 'no_counterpart' (an individual the other system holds nothing for, such as a link "
    "object that only one model has). Set done=true when you have nothing further.")

CLOSING_NOTE = ("CLOSING CHECK: the individuals under 'unaccounted' are open and appear in no match, not under "
                "left_open and not under no_counterpart. Account for each one now.")


class SequencedReasonerStack:
    """Anchors first, then one reasoner over the records, at placement both_inert or one_inert (A live)."""

    def __init__(self, case: InstanceCase, model: str, placement: str, anchors: dict, client=None,
                 max_turns: int = 4, closing_reminders: int = 1, verify: bool = True):
        assert placement in NOTE, placement
        self.case, self.model, self.placement, self.anchors = case, model, placement, dict(anchors)
        self._client, self.max_turns, self.closing_reminders = client, max_turns, closing_reminders
        self.lookalikes = {"A": lookalike_classes(case.a, set(self.anchors)),
                           "B": lookalike_classes(case.b, set(self.anchors.values()))}
        self.verify = verify
        self.max_verify_rounds = 2
        self.name = f"sequenced-reasoner+anchors{'+verify' if verify else ''}+{placement}"
        self.progress = None

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def system(self) -> str:
        return PREAMBLE + NOTE[self.placement] + (VERIFY_NOTE if self.verify else "") + CLOSER

    def reconcile(self, placement: str | None = None) -> InstanceReconciliation:
        case, client = self.case, self._get_client()
        anch_a, anch_b = set(self.anchors), set(self.anchors.values())
        open_a = [i for i in case.a if i["id"] not in anch_a]
        open_b = [i for i in case.b if i["id"] not in anch_b]
        oa, ob = {i["id"] for i in open_a}, {i["id"] for i in open_b}
        la = {x for side in ("A", "B") for g in self.lookalikes[side] for x in g}
        oracle = Oracle(case, "one_inert" if self.placement == "one_inert" else "both_inert", inert_side="b")
        rec = InstanceReconciliation(placement=self.placement, reference_variant="none")
        rec.transcript.append({"step": "prompt", "placement": self.placement, "stack": self.name,
                               "evidence": sorted(FULL), "anchored": len(self.anchors),
                               "open_a": len(open_a), "open_b": len(open_b),
                               "lookalikes_a": sum(len(g) for g in self.lookalikes["A"]),
                               "lookalikes_b": sum(len(g) for g in self.lookalikes["B"])})
        payload = {
            "settled": [{"a_id": a, "b_id": b} for a, b in self.anchors.items()],
            "settled_records_a": _private_view([i for i in case.a if i["id"] in anch_a], FULL),
            "settled_records_b": _private_view([i for i in case.b if i["id"] in anch_b], FULL),
            "open_a": _private_view(open_a, FULL), "open_b": _private_view(open_b, FULL),
            "lookalikes_a": self.lookalikes["A"], "lookalikes_b": self.lookalikes["B"],
        }
        fmt = ReplyOneLive if self.placement == "one_inert" else ReplyInert
        accepted: dict[str, str] = {}          # a_id -> b_id, by topology (or by a joined device identifier)
        conf: dict = {}
        refused, left, none = [], {}, set()
        answers_a: dict[str, dict] = {}
        tot = {"total_tokens": 0, "reasoning_tokens": 0, "latency_s": 0.0}
        turns, reminders, history = 0, 0, []
        n_rejected, verify_rounds = 0, 0
        for _ in range(self.max_turns + self.closing_reminders):
            payload["your_earlier_replies"] = history
            t0 = time.time()
            completion = client.chat.completions.parse(
                model=self.model,
                messages=[{"role": "system", "content": self.system()},
                          {"role": "user", "content": json.dumps(payload, indent=2)}],
                response_format=fmt)
            reply = completion.choices[0].message.parsed
            eff = _effort_from_usage(getattr(completion, "usage", None))
            turns += 1
            tot["total_tokens"] += eff["total_tokens"]; tot["reasoning_tokens"] += eff["reasoning_tokens"]
            tot["latency_s"] += time.time() - t0
            rec.transcript.append({"step": "turn", "from": "reasoner", "turn": reply.model_dump()})
            history.append(reply.model_dump())
            pending = []
            for m in reply.matches:
                if m.a_id not in oa or m.b_id not in ob:
                    continue
                if m.a_id in la or m.b_id in la:          # the protocol's rule: unchecked, so it does not count
                    if (m.a_id, m.b_id) not in [(r["a_id"], r["b_id"]) for r in refused]:
                        refused.append({"a_id": m.a_id, "b_id": m.b_id, "basis": m.basis})
                        rec.transcript.append({"step": "lookalike_match_refused", "a_id": m.a_id, "b_id": m.b_id,
                                               "reason": "involves a look-alike and no check is available"})
                    continue
                if m.a_id in accepted or m.b_id in accepted.values():
                    continue
                pending.append(m)
            rejected_now = []
            if pending and self.verify:        # an independent second reading; it is not shown the stated basis
                vt0 = time.time()
                vc = client.chat.completions.parse(
                    model=self.model,
                    messages=[{"role": "system", "content": VERIFIER},
                              {"role": "user", "content": json.dumps({
                                  **{k: payload[k] for k in ("settled", "settled_records_a", "settled_records_b",
                                                             "open_a", "open_b")},
                                  "proposed": [{"a_id": m.a_id, "b_id": m.b_id} for m in pending]}, indent=2)}],
                    response_format=Verdicts)
                veff = _effort_from_usage(getattr(vc, "usage", None))
                tot["total_tokens"] += veff["total_tokens"]; tot["reasoning_tokens"] += veff["reasoning_tokens"]
                tot["latency_s"] += time.time() - vt0
                verdicts = {(v.a_id, v.b_id): v for v in vc.choices[0].message.parsed.verdicts}
                rec.transcript.append({"step": "verify", "proposed": len(pending),
                                       "verdicts": [v.model_dump() for v in verdicts.values()]})
                kept = []
                for m in pending:
                    v = verdicts.get((m.a_id, m.b_id))
                    if v is not None and v.verdict == "determined":
                        kept.append(m)
                    else:
                        rejected_now.append({"a_id": m.a_id, "b_id": m.b_id,
                                             "verdict": v.verdict if v else "no verdict given",
                                             "reason": v.reason if v else ""})
                pending = kept
                if rejected_now:
                    n_rejected += len(rejected_now)
                    payload.setdefault("verifier_rejections", []).extend(rejected_now)
            for m in pending:
                if m.a_id in accepted or m.b_id in accepted.values():
                    continue
                accepted[m.a_id] = m.b_id
                conf[frozenset((m.a_id, m.b_id))] = float(m.confidence or 0.0)
            for o in reply.left_open:
                if o.id in oa or o.id in ob:
                    left[o.id] = o.reason
            none |= {x for x in reply.no_counterpart if x in oa or x in ob}
            asked = []
            for q in getattr(reply, "device_questions", []):
                r = oracle.interrogate(q.individual_id, q.attribute or None)
                res = {"individual_id": q.individual_id, "ok": r.ok, "answer": r.answer, "message": r.message}
                asked.append(res)
                rec.transcript.append({"step": "interrogate", "by": "reasoner",
                                       "args": {"individual_id": q.individual_id, "attribute": q.attribute},
                                       "result": res})
                if r.ok and r.answer:
                    answers_a.setdefault(q.individual_id, {}).update(r.answer)
            if asked:
                payload.setdefault("device_answers", []).extend(asked)
                # the join on device-reported identifiers is mechanical: a value must be found, once, in the
                # OTHER side's record. The inert side's record carries no such identifiers (see module note).
                joined = self._join_device_answers(answers_a, open_b, set(accepted), set(accepted.values()))
                for a, b in joined.items():
                    accepted[a] = b; conf[frozenset((a, b))] = 1.0
                    rec.transcript.append({"step": "device_identifier_join", "a_id": a, "b_id": b})
            if (asked and not reply.done) or (rejected_now and verify_rounds < self.max_verify_rounds):
                verify_rounds += 1 if rejected_now else 0
                continue
            settled_ids = set(accepted) | set(accepted.values())
            unaccounted = sorted((oa | ob) - settled_ids - set(left) - none - {r["a_id"] for r in refused}
                                 - {r["b_id"] for r in refused})
            if reply.done and (not unaccounted or reminders >= self.closing_reminders):
                if unaccounted:
                    rec.transcript.append({"step": "left_unaccounted", "ids": unaccounted})
                payload.pop("closing_check", None)
                break
            if reply.done:
                reminders += 1
                payload["closing_check"] = {"note": CLOSING_NOTE, "unaccounted": unaccounted}
                rec.transcript.append({"step": "closing_check", "reminder": reminders, "ids": unaccounted})
        pairs = {frozenset(p) for p in self.anchors.items()} | {frozenset(p) for p in accepted.items()}
        matched = set().union(*pairs) if pairs else set()
        rec.submitted = True
        rec.proposed = list(pairs)
        rec.confidence = {p: conf.get(p, 1.0) for p in pairs}
        rec.residual_a = [i["id"] for i in case.a if i["id"] not in matched]
        rec.residual_b = [i["id"] for i in case.b if i["id"] not in matched]
        rec.confirmed_pairs = set()
        rec.oracle_calls = dict(oracle.calls)
        rec.interrogated = set(oracle.interrogated)
        rec.effort = {"total_tokens": tot["total_tokens"], "reasoning_tokens": tot["reasoning_tokens"],
                      "latency_s": round(tot["latency_s"], 2), "model": self.model, "turns": turns}
        rec.transcript.append({"step": "sequence", "placement": self.placement,
                               "by_anchor": len(self.anchors), "by_topology": len(accepted),
                               "verified": self.verify, "verifier_rejections": n_rejected,
                               "lookalike_matches_refused": len(refused),
                               "left_open": len([x for x in left if x in oa]),
                               "left_open_lookalikes": len([x for x in left if x in oa and x in la]),
                               "open_a_lookalikes": len([x for x in oa if x in la]),
                               "device_questions": oracle.calls.get("interrogate", 0)})
        if self.progress:
            self.progress({"stage": 1, "turns": turns, "total_tokens": tot["total_tokens"],
                           "settled": len(pairs), "experiments": 0})
        return rec

    @staticmethod
    def _join_device_answers(answers_a: dict, open_b: list[dict], taken_a: set, taken_b: set) -> dict:
        """A device-reported value of A joins to B's individual whose RECORD carries the same value, once."""
        index: dict = {}
        for i in open_b:
            for v in (i.get("attrs") or {}).values():
                if isinstance(v, (str, int, float)):
                    index.setdefault(str(v), []).append(i["id"])
        out = {}
        for a, facts in answers_a.items():
            if a in taken_a:
                continue
            hits = {b for v in facts.values() for b in index.get(str(v), [])}
            if len(hits) == 1:
                b = next(iter(hits))
                if b not in taken_b and b not in out.values():
                    out[a] = b
        return out
