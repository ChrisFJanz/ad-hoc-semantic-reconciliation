# Working notes for the verification report (threads to carry into the write-up)

Data complete (results/verify_verify_hard.csv). The study measures the *verifier's* own
quality and reach by mode across the cognition spectrum, over the seeded verify_hard set
(8 correct, 2 meaning-visible-wrong: svc-100, R1; 4 byte-clean-wrong: crossed symmetric +
crossed keyless mappings).

## Headline findings (all confirmed except the capability one, which is an honest miss)

1. **Byte round-trip is beaten (the paper's claim, quantified).** catch 0.00, false-pass 1.00
   at every placement — it passes ALL six wrong pairs, including the four byte-clean crossed
   mappings that round-trip perfectly. Lead the report with this.

2. **The modes are complementary; only together do they catch everything.** invariant
   round-trip catches meaning-visible (mv 1.00) but is blind to byte-clean (bc 0.00); virtual
   operation catches byte-clean (bc 1.00 at both_cognitive) + svc-100 by provision, but not R1
   (no probe). byte catches nothing. invariant + virtual at both_cognitive catch all 6. This is
   the argument that verification is intrinsic and multi-modal, not a round-trip check. Build the
   figure as a mode x category catch matrix.

3. **Verification reach collapses across the spectrum.** virtual operation reach 0.79 → 0.21 →
   0.00; byte-clean catch 1.00 → 0.00 → 0.00 (both_cognitive → one_inert → both_inert), because
   an inert side cannot be interrogated. The verification-side echo of the instance study's
   resolvability shortfall — the errors that most need catching become uncatchable exactly where
   cognition is weakest. Tie explicitly to the instance report and to REPORT_1of4_configuration.md's residual-as-
   shortfall.

4. **The invariant verifier never wrongly fails a correct pair (fail_correct 0).** Its false-pass
   (~0.67) is entirely byte-clean blindness, not miscalibration — an important distinction for
   how to read its precision (0.67).

## Honest miss vs pre-registration (report plainly, à la the definition+example correction)

- Prediction 4 (weak models miss meaning-visible violations) DID NOT HOLD. sol, mini, nano all
  catch the meaning-visible errors identically (mv 1.00) and all miss byte-clean (bc 0.00). No
  capability gradient in the invariant mode here. Likely because the seeded meaning-visible
  traps are *visibly* stark (ODU1 vs ODU0 capacity; degree-3 vs degree-1 topology), so even
  nano's reasoning suffices. State it straight: on this set, invariant verification is robust
  across the ladder; a subtler invariant violation would be needed to separate the models, and
  that is a natural follow-up (and a caution: do not over-generalize "verification is
  capability-robust" from stark traps).

## Framing to reuse

- Verification is the *object* here, not the means: the verifier has its own precision, catch
  rate, and reach. Keep "catch what is wrong / pass what is correct / refer what you cannot
  decide" as the three outcomes, mirroring reconciliation's propose/confirm/refer.
- The byte-clean-but-wrong pair is latent in instance_hard (the crossed symmetric mapping): a
  wrong correspondence with identical static records, caught only by interrogation. Reuse the
  instance study's own case as the source of the paper's headline demonstration — a nice economy.
- Reach, not just accuracy, is the spectrum variable: which mode you can still *run* changes as
  cognition recedes, even when the mode that would catch an error exists in principle.
