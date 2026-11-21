# Instance matching: which router are we talking about?

*A case study that applies the reconciliation method to one question: how two agents, each with its own model
and its own names for one network, come to refer to the same components.*

Two software agents each hold their own model of one network and their own names for its routers, ports and
bundles. No identifiers were agreed between them in advance, and no external service binds one agent's names to
the other's. In every recorded run the two agents matched every individual correctly: all 658 in a 96-router
network.

**With the method as tightened in this work, that takes two conversations, about 140 checks against the network
and about five minutes. The method as it stood at the start took twelve conversations, about 580 checks and
22 minutes for the same result.**

This folder holds everything for this case and only this case. It was prompted by an experiment proposed on the
IETF NMOP mailing list, and it is a study of its own, separate from the four-scenario study in `../study`.

## Start here

| If you have | Do this |
|---|---|
| Five minutes | Read the summary of `note.pdf` |
| Twenty-five minutes | Watch `Translation_or_Binding_Part3.mp4`; it stands on its own |
| A browser | Open `demonstrator.html` and step through a recorded run |
| Python | Run the tests and rebuild the tables (below); no API key is needed |
| Python and an OpenAI API key | Rerun any recorded configuration (below) |

## What is in the folder

| Path | What it is |
|---|---|
| `note.pdf` | "Which router are we talking about? Instance matching as a binding": the case, what was shown, the refinements to the method, and what they teach |
| `Translation_or_Binding_Part3.mp4`, `Translation_or_Binding_Part3_transcript.txt` | The narrated video and its transcript |
| `demonstrator.html` | A step-through of a recorded run: the network, each agent's graph and the conversation. It opens in any browser and needs no server and no key |
| `more-demonstrators/` | The same step-through for three other recorded runs: the small network with live observation, the 22-router network with addresses withheld, and the 96-router network |
| `cases/` | The three networks (8, 22 and 96 routers) and the same-name variant, each as two independently populated graphs with the ground truth used for scoring; and `config_ipnet`, the two models with their correspondences |
| `harness/` | The code for this case, with its tests |
| `results/` | Every recorded run: a summary per configuration and the full transcript of each run |

### The code, in the order the method applies it

| File in `harness/matching/` | Step |
|---|---|
| `anchor.py` | Identity anchor: individuals are matched by comparing the identifiers that the model step found to correspond. Also look-alike detection, and the variants (addresses withheld, listing order shuffled) |
| `two_agent.py` | The conversation between two agents and its protocol: propose and ratify, checks for look-alikes, the closing check |
| `two_agent_staged.py` | Conversations of bounded size for a large network |
| `single_reasoner.py` | The same sequence with one or both sides inert: one reasoner over the records, with a verification pass |
| `network_check.py` | The stand-in that answers a check: an experiment on a digital twin, or a live observation |
| `carry.py`, `term_translator.py` | The translators for individuals and for values, and the carry check |

`run_matching.py` runs one configuration; `record_runs.py` is the queue of recorded configurations; `tables.py`
rebuilds the note's tables from `results/`; `build_demonstrator.py` builds a demonstrator page from any recorded
run; `build_case.py` generates a network of any size.

The code is built on the study harness in `../study` and uses it in place: the case format, the scoring and
the base stacks. Nothing in `../study` was changed.

## What you can do

**Read a conversation.** Each `results/<network>/<configuration>/runN.json` is the full record of one run: every
turn each agent took, every question, proposal and ratification, and every check with its outcome.

**Check the figures, with no key.** From this folder:

    python harness/tables.py                     # rebuilds Tables 1 and 3 of the note from results/
    python -m pytest -q harness/tests            # 17 tests: the whole protocol, run with scripted agents

The tests include agents that guess a look-alike wrongly, forget an individual, or cross two matches, and show
the protocol catching each. The identity anchor and the look-alike detection are deterministic, so the 38,
122 and 542 individuals settled by identifier reproduce exactly.

**Rerun the agents, with a key.** Set up the environment as in `../study/README.md` and the key as in `../study/notes/SETUP_OPENAI.md`, then:

    python harness/record_runs.py --list                         # the recorded configurations
    python harness/record_runs.py --only small                   # every small-network configuration
    python harness/record_runs.py --set inert                    # the inert placements
    python harness/record_runs.py --set two-agents --only large  # the 96-router network

Runs are resumable. With gpt-5.6-sol a run costs 0.1 to 0.2 million tokens on the small network, 0.2 to 0.6
million on the medium one, and 1.1 to 2.8 million on the large one, where a run with addresses withheld takes
about 22 minutes. Start small.

**Try your own network.** `python harness/build_case.py --size small` regenerates a case; other sizes and seeds
give new networks in the same format.

## Recorded configurations

| Configuration | What it is |
|---|---|
| `experiment` | Two agents; the check is an experiment on a digital twin |
| `observation` | Two agents; the check is a live observation, which reads recorded data and does nothing to the network |
| `withheld-experiment` | Two agents; every IP address withheld from both, so only the routers match by identifier |
| `both-inert`, `one-inert` | One reasoner over two static records, or with one live side |
| `withheld-both-inert`, `withheld-one-inert` | The same, with addresses withheld |

Each was run three times. `results/earlier-protocol/` holds, with full transcripts, the two earlier
configurations that the note cites for comparison: the 96-router network with every match conversed and checked,
and the 22-router network with no check required. `results/model-step/` holds the conversation in which the two
agents reconciled their models, the experiments they ran, and the resulting translation rules for values.

## What this is not

- **The networks are synthetic,** and so is the recorded data compared in a live observation.
- **The digital twin is a stand-in.** `network_check.py` answers a check from the ground truth that the case
  carries. It shows what the method does when a twin or the live network can answer; it is not itself a twin.
- **The agents are a language model.** A rerun will not reproduce a transcript word for word. The recorded
  results are three runs per configuration with one model, so they show that the method works and what it
  costs here; they do not measure a failure rate.
- **Making bindings, not keeping them.** How a binding already made is found to have gone out of date was not
  examined.
