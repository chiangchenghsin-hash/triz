#!/usr/bin/env python3
"""diff_test.py — differential random testing binding layer (Cornerstone 4).

Feeds the same random input to a small reference model and a production
implementation, compares canonicalized outputs.

A mismatch is a DIVERGENCE; a runner exception is a CRASH. Both are findings
(negative results are assets too): they are recorded in the ledger and the
run continues — one bad case never aborts the campaign.

Runner contract (each module must export):
  gen.py    def gen(rng: random.Random) -> input   one test input (any repr-able value)
  model.py  def run(inp) -> output                 small model / specification
  impl.py   def run(inp) -> output                 production implementation
Outputs are compared via JSON canonicalization (dict key order irrelevant;
1 and "1" differ). --gen/--model/--impl accept file paths (recommended, CI
friendly) or module names on sys.path.

Exit codes (release-gate semantics):
  0 = clean run (no DIVERGENCE, no CRASH)           -> release may proceed
  1 = DIVERGENCE or CRASH present (old or new)      -> release MUST be blocked
  2 = infrastructure error (bad path/import/contract) -> fix the harness first;
      never interpret this as a product verdict

Ledger (TSV, append-only, deduplicated by input hash):
  hash  seed  case  status  inp  model_out  impl_out  detail  added_at
Full inputs are archived to <ledger>.inputs.jsonl for reproduction.

Usage:
  python diff_test.py --gen gen.py --model model.py --impl impl.py \
      --n 100000 --seed 42 --ledger divergence.tsv
"""
from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import importlib
import importlib.util
import json
import os
import random
import sys
import threading
from types import ModuleType
from typing import Any, Callable

LEDGER_FIELDS = ["hash", "seed", "case", "status", "inp",
                 "model_out", "impl_out", "detail", "added_at"]

# Gate interprets only 0/1; 2 means the test infrastructure itself is broken
EXIT_CLEAN, EXIT_DIVERGENCE, EXIT_INFRA = 0, 1, 2


def load_module(ref: str) -> ModuleType:
    """Load a runner by file path or module name. Paths take priority."""
    looks_like_path = (ref.endswith(".py") or os.sep in ref or (os.altsep and os.altsep in ref)
                       or os.path.exists(ref))
    if looks_like_path:
        path = os.path.abspath(ref)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"runner file not found: {ref}")
        spec = importlib.util.spec_from_file_location(_stem(path), path)
        if spec is None or spec.loader is None:
            raise ImportError(f"cannot load runner: {ref}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    # Module name: cwd is a valid package root (legacy usage; prefer file paths)
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    return importlib.import_module(ref)


def _stem(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def require(mod: ModuleType, fn: str, ref: str) -> Callable:
    """Contract check: a missing export is an infrastructure error with an
    actionable message, not a mystery traceback."""
    target = getattr(mod, fn, None)
    if not callable(target):
        raise AttributeError(f"{ref} has no callable {fn}(); runner contract unmet")
    return target


def canonical(value: Any) -> str:
    """Stable serialization: both comparison and hashing go through here."""
    return json.dumps(value, sort_keys=True, default=repr, ensure_ascii=False)


def case_hash(inp: Any) -> str:
    return hashlib.sha256(canonical(inp).encode("utf-8")).hexdigest()[:16]


def call_with_timeout(fn: Callable, inp: Any, timeout: float | None) -> Any:
    """Call with an optional per-case timeout. A timeout raises TimeoutError.
    Threads cannot be force-killed; back a hung runner with a CI-level timeout."""
    if timeout is None:
        return fn(inp)
    box: dict[str, Any] = {}

    def target() -> None:
        try:
            box["out"] = fn(inp)
        except BaseException as exc:  # noqa: BLE001 — re-raised on this thread
            box["exc"] = exc

    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise TimeoutError(f"runner exceeded {timeout}s")
    if "exc" in box:
        raise box["exc"]
    return box["out"]


def read_known_hashes(ledger_path: str) -> set[str]:
    """Read hashes already in the ledger so reruns do not duplicate rows."""
    known: set[str] = set()
    if not os.path.exists(ledger_path):
        return known
    with open(ledger_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if reader.fieldnames and "hash" in reader.fieldnames:
            for row in reader:
                if row.get("hash"):
                    known.add(row["hash"])
    return known


def write_finding(writer, inputs_f, known: set[str], *, h: str, seed: int,
                  case: int, status: str, inp: Any, model_out: str,
                  impl_out: str, detail: str) -> bool:
    """Append one ledger row + archive the full input.
    Returns True when this hash was not in the ledger before."""
    is_new = h not in known
    if is_new:
        writer.writerow([h, seed, case, status, canonical(inp)[:500],
                         model_out[:500], impl_out[:500], detail[:500],
                         datetime.datetime.now(datetime.timezone.utc)
                         .isoformat(timespec="seconds")])
        inputs_f.write(json.dumps({"hash": h, "seed": seed, "case": case,
                                   "inp": inp}, default=repr, ensure_ascii=False)
                       + "\n")
        known.add(h)
    return is_new


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Differential random testing, model vs impl; "
                    "exit 0=clean 1=findings 2=infra error")
    ap.add_argument("--gen", required=True,
                    help="input generator: file path or module name exporting gen(rng)")
    ap.add_argument("--model", required=True,
                    help="small-model runner exporting run(inp)")
    ap.add_argument("--impl", required=True,
                    help="production-impl runner exporting run(inp)")
    ap.add_argument("--n", type=int, default=1000, help="number of cases (default 1000)")
    ap.add_argument("--seed", type=int, default=42,
                    help="RNG seed (default 42; reproduction depends on it)")
    ap.add_argument("--ledger", default="divergence.tsv", help="ledger path (TSV, append)")
    ap.add_argument("--timeout", type=float, default=None,
                    help="per-case timeout in seconds (default unlimited)")
    ap.add_argument("--fail-fast", action="store_true",
                    help="stop at first finding (debug only; keep off for nightly runs)")
    ap.add_argument("--quiet", action="store_true", help="suppress progress output")
    a = ap.parse_args()

    try:
        gen_mod = load_module(a.gen)
        model_mod = load_module(a.model)
        impl_mod = load_module(a.impl)
        gen_fn = require(gen_mod, "gen", a.gen)
        model_fn = require(model_mod, "run", a.model)
        impl_fn = require(impl_mod, "run", a.impl)
    except Exception as exc:  # noqa: BLE001 — load/contract failure = infra error
        print(f"[infra] {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_INFRA

    if a.n < 1:
        print("[infra] --n must be >= 1", file=sys.stderr)
        return EXIT_INFRA

    known = read_known_hashes(a.ledger)
    inputs_path = a.ledger.rsplit(".", 1)[0] + ".inputs.jsonl"
    ledger_exists = os.path.exists(a.ledger) and os.path.getsize(a.ledger) > 0

    total = divergent = crashy = new_findings = 0
    progress_step = max(a.n // 10, 1)

    with open(a.ledger, "a", newline="", encoding="utf-8") as lf, \
            open(inputs_path, "a", encoding="utf-8") as inputs_f:
        writer = csv.writer(lf, delimiter="\t")
        if not ledger_exists:
            writer.writerow(LEDGER_FIELDS)
        for case in range(a.n):
            # Per-case RNG: any single case is reproducible from (seed, case)
            inp = gen_fn(random.Random(a.seed * 1_000_003 + case))
            total += 1
            m_out: Any = None
            i_out: Any = None
            try:
                m_out = call_with_timeout(model_fn, inp, a.timeout)
                i_out = call_with_timeout(impl_fn, inp, a.timeout)
            except Exception as exc:  # noqa: BLE001 — a crash is a finding
                crashy += 1
                detail = f"CRASH {type(exc).__name__}: {exc}"
                is_new = write_finding(
                    writer, inputs_f, known, h=case_hash(inp), seed=a.seed,
                    case=case, status="CRASH", inp=inp,
                    model_out=repr(m_out)[:500],
                    impl_out=repr(i_out)[:500],
                    detail=detail)
                new_findings += is_new
                if a.fail_fast:
                    break
                continue
            if canonical(m_out) != canonical(i_out):
                divergent += 1
                is_new = write_finding(
                    writer, inputs_f, known, h=case_hash(inp), seed=a.seed,
                    case=case, status="DIVERGENCE", inp=inp,
                    model_out=repr(m_out), impl_out=repr(i_out),
                    detail="model != impl")
                new_findings += is_new
                if a.fail_fast:
                    break
            if not a.quiet and (case + 1) % progress_step == 0:
                # ASCII-only console output: safe on Windows GBK terminals and CI logs
                print(f"-- progress {case + 1}/{a.n} "
                      f"(divergent={divergent}, crash={crashy})")

    findings = divergent + crashy
    rate = findings / total if total else 0.0
    print(f"-- {total} cases | findings={findings} "
          f"(divergence={divergent}, crash={crashy}, new={new_findings}) "
          f"| rate={rate:.2%} -> {a.ledger}")
    if findings:
        print(f"-- GATE: BLOCK (exit 1). Reproduce with --seed {a.seed}; "
              f"full inputs in {inputs_path}")
    return EXIT_DIVERGENCE if findings else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
