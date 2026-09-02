# Bringing in the OpenAI agent (macOS)

This connects the language-model reasoning stack. You do it once. None of these
steps ever ask you to paste your key into a chat or commit it to GitHub — keep it
to yourself and to the local `.env` file described below.

## 1. Know what you're signing up for

The OpenAI **API** is separate from the ChatGPT app, and is billed separately. A
ChatGPT subscription does not include API calls. The API is pay-as-you-go: you add
a small amount of credit and each call draws down from it. Our runs are tiny — the
configuration case is a few thousand tokens per call, so a handful of dollars of
credit covers a great deal of experimentation.

## 2. Create an API key

1. Go to **platform.openai.com** and sign in with the account you just made.
2. Open **Settings → Billing** and add a payment method or a small prepaid credit
   (say $5–$10 to start). Without credit, calls fail with an "insufficient quota"
   error.
3. Open the **API keys** page (under your profile / dashboard), click **Create new
   secret key**, name it something like `reconciliation-study`, and copy it. You
   will only see it once. It looks like `sk-...`.

Treat that string like a password. Anyone who has it can spend your credit.

## 3. Put the key where the code can find it

In the repo folder on your Mac, create a file named exactly `.env` (the leading dot
matters) with one line:

```
OPENAI_API_KEY=sk-your-key-here
```

That's it. `.env` is already in `.gitignore`, so it will not be committed or
pushed. The code reads it automatically. If you ever think the key leaked, delete
it on the API keys page and create a new one — that instantly disables the old one.

(If you prefer not to use a file, you can instead run `export OPENAI_API_KEY=sk-...`
in the Terminal window before running, but that only lasts for that one window.)

## 4. Install the library

From the repo folder in Terminal:

```bash
python3 -m venv .venv          # a clean, isolated Python environment
source .venv/bin/activate      # you'll see (.venv) appear in the prompt
pip install openai
```

The walking skeleton itself needs nothing installed; `openai` is only for this
agent stack.

## 5. Run it

```bash
python pipeline/run.py --agent --trials 3
```

This runs four things on the configuration case: the two model-agnostic stacks
(baseline and reference), then the OpenAI agent **without** the reference and
**with** it, three times each because a language model varies from run to run. You
will see precision, resolved fraction, the surviving-false-cognate count, and — for the agent
rows — the tokens and seconds each run took. Everything is also written to
`results/config_tapi_teas.csv`.

## What to look for

The agent rows are the first real measurement of the central claim. Compare the
agent **without** the reference against the agent **with** it, on two axes at once:

- **Quality**: does the reference raise precision/resolved fraction and remove the surviving
  false cognate?
- **Effort**: does the agent spend *fewer tokens* to reach the answer when the
  reference is present? That token difference is cognitive effort, measured — the
  thing Part II said could only be observed with a model in the loop, not counted.

If the reference both improves the answer and lowers the effort, that is
hypothesis H1 — a reference partially substitutes for cognition — showing up in
real data on real standards, for the first time.

## Choosing the model

The default is `gpt-5.6`. To try another model your account lists on the Models
page, set it alongside the key:

```
OPENAI_MODEL=<model-name>
```

Cheaper or smaller models are a fine way to keep costs down while iterating; the
reasoning-heavy models will show a larger effort signal and are worth a few runs
once the pipeline is working.

## If something goes wrong

- `openai is not installed` → you skipped step 4, or the virtualenv isn't active
  (re-run `source .venv/bin/activate`).
- `OPENAI_API_KEY is not set` → the `.env` file isn't in the repo folder, or the
  line is misspelled.
- `insufficient_quota` or a 429 → add credit in Billing (step 2).
- A model-not-found error → set `OPENAI_MODEL` to a model your account can access.

Bring me any error text and I'll sort it out with you.
