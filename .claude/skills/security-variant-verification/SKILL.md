---
name: security-variant-verification
description: Use when hunting vulnerability variants from a CVE or patch, binding a formal or simplified model to a production implementation through differential testing, gating a release on model-implementation agreement, or auditing LLM security findings to cut false positives. Triggers: variant hunting, patch-pattern migration, differential/diff testing, Lean small model, Cedar-style property, neuro-symbolic security audit, divergence ledger, release gate.
---

# Security Variant Verification

## Overview

One chain, six links: **extract the violated-invariant pattern (variant hunting)
→ state it as a small-model property → generate candidates (neural layer) →
machine-verdict them (symbolic layer) → bind model to implementation
(differential testing) → gate the release**.

Two rules never bend:

1. The LLM does judgment-intensive work only (candidate generation, pattern
   abstraction). Every verdict runs through deterministic tools.
2. Every number carries its source and its data-generating mechanism. A bare
   claim is never an anchor.

## When to use

- Variant analysis / isomorph mining starting from a CVE, a patch diff, or a
  Project Zero-style report
- Building a "small model + differential test" verification layer for a
  critical component
- Auditing or cleaning LLM security-audit output (false-positive reduction)
- Binding a formal/simplified model to what production actually does

## When not to use

- A brand-new vulnerability class with no patch history to abstract from
- One-off scripts with no specification worth writing down
- Tasks where "run the LLM and trust it" is genuinely acceptable (no gate needed)

## Roles

| Human side | Agent side |
|---|---|
| Provides CVE/patch seeds, target codebase | Extracts the violated-invariant pattern (abstract level) |
| Maintains NVD/CVE/Project Zero-style feeds | Produces candidate variant sites (judgment-intensive) |
| Maintains diff-test infra and the release gate | Writes small-model property specs, runs differential comparison |
| Adjudicates disputed findings | Keeps the ledger (schema below) |

## Workflow

Copy this checklist and track progress:

```
Security Variant Verification:
- [ ] P0. Scope + gap scan (stop rule checked)
- [ ] P1. Pattern extracted (survives a counterexample test)
- [ ] P2. Property written in the small model (budget checked)
- [ ] P3. Candidates generated, then machine-verdict (no neural-only rows)
- [ ] P4. Differential binding run (divergence triaged)
- [ ] P5. Gate decision recorded (block/release) + coverage claim written
```

### P0. Scope and gap scan

Define: seed (CVE/patch), target (repo/component), and the property family to
verify. Declare the engagement type — it decides later phases:

- `variant-hunt`: P3 isomorph mining is required (search the whole target)
- `bind-only`: P3 isomorph mining is N/A; P1 extracts the pattern from the one
  patch/component and P4 binds that component only

Run the gap-scan template in [references/triz-mapping.md](references/triz-mapping.md)
once per engagement. Stop rule: no seed, no target, or no writable property →
stop and say so; do not improvise a "variant hunt" without them.

### P1. Pattern extraction (variant hunting)

1. **Seed**: CVE advisory + vendor patch diff + issue report — cross at least two
   sources; a single source is never trusted alone. No second public source
   (internal/synthetic bug)? Prefix the seed id with `SYNTH-`, mark the
   source-crossing row N/A with a one-line justification — never fabricate a
   second source.
2. **Extract the pattern**: the abstract structure of "which invariant got
   violated". Never function names or literals — the pattern must be stateable
   without the original code.
3. **Transfer**: isomorph search on the target (deterministic queries —
   CodeQL/Joern — first; LLM only for semantic sites a query cannot express).
4. **Acceptance**: every hit carries a one-line "why isomorphic" rationale,
   marked `[explanation]` (neural-layer judgment, never a verdict).
5. The pattern must survive a **counterexample test**: name one nearby shape
   that is NOT an instance of the pattern. No counterexample named → abstraction
   is untested.

Reference figure (claimed; data-generating mechanism: in-the-wild 0-day sample
observation, Project Zero public reports): roughly 50% of in-the-wild 0-days in
2022 H1 were variants of previously patched bugs; a variant hunt seeded from
Arm Mali bugs (e.g. CVE-2021-39793 / CVE-2022-22706) reportedly surfaced 5
additional exploitable bugs in 3 weeks. See
[references/cornerstones.md](references/cornerstones.md) for provenance notes.

### P2. Small-model property (the Cedar pattern)

1. Do **not** rewrite production code. Maintain an executable model at roughly
   1/10 scale (TRIZ "cheap substitute" logic: the model is a mediator, not a
   replacement).
2. State key properties on the model (canonical example: `forbid_trumps_permit`
   — any request matching a forbid policy must be denied).
3. Split properties into small reusable lemmas (target: ~1 working day per
   property once the harness exists).
4. Budget: 4–8 days for a new property family. Over budget → stop and ask
   whether the model boundary was cut wrong before pushing harder.
5. Discipline: a proven property holds **of the model**. Whether it holds of the
   implementation is decided at P4, never assumed.

### P3. Candidate generation, then machine verdict

| Layer | Component | Job | Trust |
|---|---|---|---|
| Neural | LLM | candidate generation, pattern abstraction, false-positive triage | untrusted (must carry `[explanation]`) |
| Symbolic | CodeQL / Joern / Lean kernel / SAT | verdict, count, proof | trusted (auditable) |

- Reference figure (claimed; MoCQ experiment, 343-vulnerability set): pure-LLM
  false-discovery rate 49.6% → 19.4% once deterministic queries adjudicate.
  Practical rule: **no neural-layer-only finding enters the ledger as a verdict.**
- Architectural reason: this is not a performance optimization; it is the move
  from un-auditable to auditable.

### P4. Differential binding + gate

1. Feed the same randomized/mutated inputs to both the model and the real
   implementation — run `scripts/diff_test.py` (see Tooling below).
2. Output mismatch → DIVERGENCE; runner crash → CRASH. Both are findings and
   enter the ledger (negative results are assets).
3. **No findings, no block. Any finding, no release.** The gate is enforced by
   exit code, not by report language.
4. Trust-chain terminus: the model's kernel + the gate's enforcement power.
   Differential testing is the binding element between model and implementation,
   not the final authority.

### P5. Record the gate decision

The P4 run produces the coverage claim; P5 writes it into the record together
with block/release and every DIVERGENCE triage verdict. A release cut against a
blocked gate is a process violation, not a judgment call.

## Ledger and discipline

**Two ledgers, never merged** (different jobs, different schemas):

1. **`divergence.tsv`** — machine-written by `diff_test.py` during P4. Fixed
   schema; don't hand-edit.

   | field | meaning |
   |---|---|
   | `hash` | stable input-hash; dedup key across runs |
   | `seed` / `case` | RNG seed and case index; exact reproduction handle |
   | `status` | `DIVERGENCE` \| `CRASH` |
   | `inp`, `model_out`, `impl_out` | canonicalized values (full input in `.inputs.jsonl`) |
   | `detail`, `added_at` | triage note; UTC timestamp |

2. **`findings.tsv`** — manual rows from P1/P3 (pattern-hunt results and their
   symbolic verdicts). Schema: `hash, seed_cve, pattern_id, target_loc,
   layer(neural/symbolic), verdict, confidence, divergence_log, notes, added_at`.
   `divergence_log` links into ledger 1 (e.g. `divergence.tsv#<hash>`).
   Example row:

   ```
   5a77a5565e770e33  SYNTH-CVE-2026-FILEAUTHZ  ordered-deny-before-allow  file_access.py:check_access  symbolic  POSITIVE  probable  divergence.tsv#5a77a5565e770e33  isomorphic: allow short-circuits matching deny  2026-10-19T08:40:00Z
   ```

- **Claim labelling** (three-way split): `fact` (patch diff) / `effect-chain`
  (exploitability reasoning) / `motive` (attribution guess). Never mix them in
  one row.
- **Confidence**, operationally:
  - `confirmed` — symbolic verdict reproduced by a second independent method,
    or proven property + clean differential run
  - `probable` — one deterministic tool confirms; mechanism plausible; not
    independently reproduced
  - `possible` — neural layer only, or plausible mechanism, untested
- **NEG:** prefix — negative findings and clean-coverage statements are recorded,
  not discarded. A blank ledger after a run is itself a reportable result.
- **Coverage claim** format: `coverage: <generator domain> @ <n> cases, seed <s>;
  properties: <list>; excluded: <list>`.
- **Self-reported numbers** (vendor advisories, papers) = claim + data-generating
  mechanism label. Single claims never anchor a conclusion.

## Tooling

**`scripts/diff_test.py`** — differential random testing, model vs implementation:

```bash
python scripts/diff_test.py --gen gen.py --model model.py --impl impl.py \
    --n 100000 --seed 42 --ledger divergence.tsv
```

- Runner contract: `gen(rng) -> inp`, `run(inp) -> output` (model and impl).
  File paths or module names accepted; paths recommended.
- Exit codes: `0` clean (release may proceed) · `1` any DIVERGENCE/CRASH,
  old or new (release MUST block) · `2` infrastructure error (fix the harness;
  never read it as a product verdict).
- Reruns deduplicate by input hash; full inputs archive to
  `<ledger>.inputs.jsonl` for single-case reproduction.
- Per-case `--timeout`, `--fail-fast` (debug only), `--quiet`.

**`examples/forbid-trumps-permit/`** — worked example (seeded bug → gate blocks →
fix → gate passes). Run it before first real use; it is 5 minutes and it
exercises the whole chain. Contract tests: `scripts/test_diff_test.py`.

**Where runners live in a real target**: copy the example's three-file shape
into the target repo under `tests/diff/` (next to its test suite), one
`gen/model/impl` triple per property family. The example is the template; the
harness is invoked from anywhere by path.

## Red flags — stop and re-read the discipline

| Excuse | Reality |
|---|---|
| "The LLM finding looks solid, let me log it as confirmed" | Neural-only findings are `possible` at best. Verdicts come from the symbolic layer. |
| "The pattern is obvious, skip the counterexample test" | An abstraction with no counterexample is untested; a wrong abstraction poisons every transfer. |
| "The model proves it, ship it" | The proof holds of the model. P4 decides the implementation. |
| "The gate is advisory, this one is urgent" | A gate that can be waived under urgency is not a gate. |
| "The diff run found nothing, so we are safe" | Nothing found = coverage claim for this generator and n. Write it down, including exclusions. |
| "This number is from a paper, treat it as fact" | It is a claim. Record mechanism and source; never anchor on a single claim. |

## Known limits

- Pattern abstraction depends on human judgment; a wrong abstraction breaks all
  transfers → every pattern carries a counterexample test (P1.5).
- Differential testing covers only the generator's reachable input space;
  property proofs cover only the properties written down. Both have blind spots
  → each run writes a coverage claim.
- Model and implementation drift apart across versions → run the differential
  suite on a fixed cadence (e.g. nightly) so drift surfaces the day it appears.

## When stuck

A design gap or a design contradiction blocking any phase (hard gate vs
flexible workflow, ledger completeness vs token budget, wrong model boundary):
see [references/triz-mapping.md](references/triz-mapping.md) — **REQUIRED at
design gaps: use the `triz` skill** via its contradiction-card handoff, then
verify the redesign with this skill's own binding discipline.
