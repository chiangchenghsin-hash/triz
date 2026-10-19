# Design-gap handoff: SVV → `triz` skill

This file is a **handoff protocol**, not a principle-label table. SVV invokes the
`triz` skill when a design gap or contradiction blocks the workflow; it does not
decorate findings with TRIZ numbers after the fact (post-hoc mapping rates are
prior-determined and prove nothing — see SKILL.md discipline).

Kept here because they are SVV-unique: the **delta table** (what the security
domain adds to TRIZ's uncalibrated tools) and the **gap-scan template**.

## Trigger conditions (when to hand off)

Hand a problem to the `triz` skill when **any** of these holds:

1. **P0 gap scan** finds a hole the workflow cannot close (missing isolation
   band, missing regression cadence, missing visualization — anything the scan
   template flags as `GAP`)
2. **Design contradiction**: two constraints are both hard and appear to
   conflict (e.g. "hard release gate" vs "flexible working loop"; "complete
   ledger" vs "token budget")
3. **Budget overrun** at P2: the stop rule fired ("is the model boundary cut
   wrong?") — that is a design question, not an implementation task

**REQUIRED at design gaps:** Use the `triz` skill. Pass the filled contradiction
card (below) as the problem statement — the card fields cover the clarification
the `triz` skill would otherwise ask for, so hand it over up front and the
interactive interview can be skipped or kept minimal. Do not copy Five-Bridges
content into this skill; the method lives there, the handoff lives here.

## Contradiction card (handoff template)

```
CARD
  id:            <SVV-GAP-nn>
  from:          which workflow phase raised it (P0–P5)
  constraint A:  <hard requirement>   e.g. gate must block on any finding
  constraint B:  <hard requirement>   e.g. agent must iterate without CI red tape
  conflict:      one sentence: where they collide in practice
  context:       artifacts involved (ledger schema, gate script, budget)
  ask:           what a resolution must satisfy (acceptance criteria)
  verify-by:     how SVV will machine-verify the chosen resolution
```

## Worked handoff (example card)

```
CARD
  id:            SVV-GAP-01
  from:          P4 / tooling design
  constraint A:  any DIVERGENCE must block release (exit-code enforcement)
  constraint B:  the agent must iterate on fixtures/impl without permanent red CI
  conflict:      one shared exit code cannot be both a hard block and a soft loop signal
  context:       scripts/diff_test.py gate semantics
  ask:           keep the gate un-waivable for product verdicts while keeping
                 infra noise out of the gate channel
  verify-by:     contract tests pin the exit-code table (0 clean / 1 findings /
                 2 infra); differential reruns stay green after a real fix
```

Resolutions of this shape are exactly what the `triz` skill is for (candidate
generation). SVV then **binds** the chosen resolution: the differential tests and
the gate are the machine verdict on whether the redesign actually holds.

### Honesty note on the reverse direction

"Differential testing" of a *documentation or design* change is not
`diff_test.py`. It is the RED-GREEN discipline: baseline behavior before the
change vs application behavior after (run the scenario against the artifact).
The binding layer applies literally only when there is an executable model and
an implementation to feed the same inputs.

## Delta table: TRIZ original vs security instance

| | TRIZ original | Security instance adds |
|---|---|---|
| Pattern library | 76 standard solutions (never calibrated) | CVE history gives ground truth — transfer validity is measurable |
| Ideality | qualitative slogan | 1/10-scale models, ~1 day/property — cost is quantifiable |
| Substance-field completion | manual analysis | differential testing is machine-run and gate-enforced |

## Gap-scan template (run at P0, and after each release)

Scan the *current design* against these four recurring hole classes. Copy this
block per engagement; fill every row (`OK` / `GAP` / `N/A` + one line of evidence):

```
GAP SCAN  (date: ____  engagement: ____) 
  Isolation band:   seed corpus vs verdict layer — can a poisoned seed forge a
                    verdict?                                    [OK|GAP|N/A]
  Cadence:          is there a regression beat outside the release gate
                    (e.g. nightly diff run)?                    [OK|GAP|N/A]
  Visualization:    can the divergence ledger be read as a picture
                    (trend of findings over time), not just rows? [OK|GAP|N/A]
  Boundary:         is the small-model boundary written down, with an owner
                    who can move it?                            [OK|GAP|N/A]
```

Any `GAP` with a pair of colliding constraints → contradiction card → hand off
to the `triz` skill. Any `GAP` without a contradiction is ordinary backlog:
fix it in the next engineering pass.
