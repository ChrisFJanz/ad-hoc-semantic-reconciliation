"""Offline checks for the term translator: a stub client returns the value rules. With the right
unit rule every observation agent B holds agrees with agent A's own record; with a wrong unit rule
every rate observation differs, and nothing else does."""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _paths import CASES, RESULTS, STUDY_CASES, HARNESS      # noqa: E402  (also puts the study harness on the path)

from reconcile.harness import Case                                                     # noqa: E402
from reconcile.instance import load_instance_case                                      # noqa: E402
from matching.carry import generate                                          # noqa: E402
from matching.term_translator import (TermRule, TermRules, carry_observations,        # noqa: E402
                                       generate_term_rules, GENERATE_SYSTEM)
from test_two_agent import _Completion                                                 # noqa: E402


class StubGen:
    def __init__(self, factor):
        self.factor = factor; self.calls = []; self.chat = self; self.completions = self

    def parse(self, model, messages, response_format):
        self.calls.append(messages)
        pairs = json.loads(messages[1]["content"])["settled_correspondences"]
        rules = []
        for p in pairs:
            if p["a_id"] == "a.speed":
                rules.append(TermRule(a_id=p["a_id"], b_id=p["b_id"], value_rule="scale", a_to_b_factor=self.factor,
                                      a_unit="bits/second", b_unit="Kbps", note=""))
            elif p["a_id"] in ("a.ip", "a.rid", "a.mac", "a.ifname"):
                rules.append(TermRule(a_id=p["a_id"], b_id=p["b_id"], value_rule="identity", a_to_b_factor=1.0,
                                      a_unit="", b_unit="", note=""))
            else:
                rules.append(TermRule(a_id=p["a_id"], b_id=p["b_id"], value_rule="not-a-value", a_to_b_factor=1.0,
                                      a_unit="", b_unit="", note=""))
        return _Completion(TermRules(rules=rules), 10, 1)


def test_right_and_wrong_unit_rule():
    sdir = CASES / "config_ipnet"
    schema = Case.load(sdir)
    binding = json.loads((sdir / "data_binding.json").read_text())
    corr = [(c["a"], c["b"]) for c in json.loads((sdir / "gold.json").read_text())["correspondences"]]
    case = load_instance_case(CASES / "instance_ipnet_small")
    tr = generate(case, case.correct_pairs)
    client = StubGen(0.001)
    rules, eff = generate_term_rules(schema.model_a, schema.model_b, corr, "stub", client=client)
    assert eff["rules"] == eff["asked"] == 10 and client.calls[0][0]["content"] == GENERATE_SYSTEM
    assert "_truth" not in client.calls[0][1]["content"]
    good = carry_observations(case, rules, tr, binding)
    n_links = sum(1 for i in case.b if i["type"] == "link")
    assert good["by_term"]["b.rate"]["observations"] == n_links == 21
    assert good["observations"] == good["carried"] == good["agree"] and good["differ"] == 0
    row = next(r for r in good["rows"] if r["observed"]["concept"] == "b.rate")
    assert len(row["carried"]["on"]) == 2 and row["carried"]["unit"] == "bits/second"      # a link, restated on its two ends
    assert row["carried"]["value"] == row["observed"]["value"] * 1000
    rules_bad, _ = generate_term_rules(schema.model_a, schema.model_b, corr, "stub", client=StubGen(1.0))
    bad = carry_observations(case, rules_bad, tr, binding)
    assert bad["by_term"]["b.rate"]["agree"] == 0 and bad["differ"] == n_links
    assert bad["by_term"]["b.ip"]["agree"] == bad["by_term"]["b.ip"]["observations"]
    print("ok test_right_and_wrong_unit_rule", {k: v for k, v in good.items() if k not in ("rows",)})


if __name__ == "__main__":
    test_right_and_wrong_unit_rule()
