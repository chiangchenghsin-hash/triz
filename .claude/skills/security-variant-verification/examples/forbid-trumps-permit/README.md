# Worked example: forbid_trumps_permit

A toy differential test of the Cedar property `forbid_trumps_permit`
(cornerstones 2 + 4, minimal closed loop). No Lean required: `model.py` is the
executable statement of the property, `impl.py` is a "production"
implementation with a classic seeded bug (permit checked before forbid).
Five minutes to watch the release gate block.

## Run it (from this directory)

```bash
# 1) Differential testing catches the bug -> exit 1 -> release gate blocks
python ../../scripts/diff_test.py --gen gen.py --model model.py --impl impl.py \
    --n 2000 --seed 42 --ledger divergence.tsv

# 2) Fix impl.py: swap the two for-loops (scan forbid before permit), rerun
#    -> exit 0 -> gate passes
python ../../scripts/diff_test.py --gen gen.py --model model.py --impl impl.py \
    --n 2000 --seed 42 --ledger divergence.tsv

# 3) Rerun once more with the same seed: the ledger does not grow
#    (rows dedupe by input hash)
```

## Expected behavior

| Step | Exit code | Ledger |
|---|---|---|
| 1 | 1 | new `DIVERGENCE` rows + full inputs archived to `divergence.inputs.jsonl` |
| 2 (after fix) | 0 | no new rows |
| 3 | 0 | row count unchanged |

## Reading a ledger row

`hash` is the dedup key and lookup handle; `inp` is the canonicalized input
JSON; `model_out`/`impl_out` are the two sides' outputs. Full inputs live in
`divergence.inputs.jsonl` keyed by `hash`/`case` — feed one back to either side
to debug a single divergence offline.

## Where this sits in the methodology

- Where the property comes from: cornerstone 1 abstracts "which invariant got
   violated" from patches/incidents — here: "a request matching both permit and
  forbid must be denied"
- Who decides: the neural layer may propose the property, but every verdict is
  the differential comparison plus the gate exit code
- Negative results are assets: the clean counts from steps 2–3 are part of the
  run's coverage claim (format in SKILL.md)
