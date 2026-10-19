#!/usr/bin/env python3
"""test_diff_test.py — diff_test.py harness contract tests (stdlib unittest).

Run:  python test_diff_test.py
These tests pin the release-gating semantics of the harness:
  exit 0 = clean run, exit 1 = divergence (block release), exit 2 = infra error.
Also pins: true dedup across runs, crash-is-a-finding, file-path module loading.
"""
import os, subprocess, sys, tempfile, textwrap, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
DIFF_TEST = os.path.join(HERE, "diff_test.py")

GEN = textwrap.dedent('''
    def gen(rng):
        return {"n": rng.randint(0, 4)}
''')
MODEL = textwrap.dedent('''
    def run(inp):
        return "even" if inp["n"] % 2 == 0 else "odd"
''')
IMPL_OK = textwrap.dedent('''
    def run(inp):
        return "even" if inp["n"] % 2 == 0 else "odd"
''')
IMPL_BUGGY = textwrap.dedent('''
    def run(inp):
        return "odd"  # always diverges on even inputs
''')
IMPL_CRASHY = textwrap.dedent('''
    def run(inp):
        if inp["n"] == 3:
            raise RuntimeError("production crash")
        return "even" if inp["n"] % 2 == 0 else "odd"
''')


class DiffTestHarness(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.ledger = os.path.join(self.dir, "ledger.tsv")
        self._write("gen.py", GEN)
        self._write("model.py", MODEL)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name, body):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        return path

    def _run(self, impl_body, *extra, n=200, seed=42, ledger=None):
        self._write("impl.py", impl_body)
        cmd = [sys.executable, DIFF_TEST,
               "--gen", os.path.join(self.dir, "gen.py"),
               "--model", os.path.join(self.dir, "model.py"),
               "--impl", os.path.join(self.dir, "impl.py"),
               "--n", str(n), "--seed", str(seed),
               "--ledger", ledger or self.ledger, *extra]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=self.dir)

    def _ledger_rows(self):
        if not os.path.exists(self.ledger):
            return []
        with open(self.ledger, encoding="utf-8") as f:
            lines = f.read().splitlines()
        return lines[1:] if lines else []

    def test_clean_run_exits_zero(self):
        r = self._run(IMPL_OK)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self._ledger_rows(), [])

    def test_divergence_exits_one_and_is_recorded(self):
        r = self._run(IMPL_BUGGY)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        rows = self._ledger_rows()
        self.assertTrue(rows, "divergence must be recorded in ledger")
        self.assertTrue(all("\tDIVERGENCE\t" in row for row in rows))

    def test_rerun_same_seed_dedups(self):
        self._run(IMPL_BUGGY)
        first = self._ledger_rows()
        r2 = self._run(IMPL_BUGGY)
        self.assertEqual(r2.returncode, 1)  # still gating: known divergence present
        self.assertEqual(self._ledger_rows(), first,
                         "re-run must not append duplicate ledger rows")

    def test_crash_is_a_finding_and_run_continues(self):
        r = self._run(IMPL_CRASHY)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        rows = self._ledger_rows()
        self.assertTrue(any("\tCRASH\t" in row for row in rows),
                        "runner crash must be recorded as a finding")

    def test_infra_error_exits_two(self):
        self._write("impl.py", IMPL_OK)
        cmd = [sys.executable, DIFF_TEST,
               "--gen", os.path.join(self.dir, "gen.py"),
               "--model", os.path.join(self.dir, "model.py"),
               "--impl", os.path.join(self.dir, "missing.py"),
               "--n", "5", "--ledger", self.ledger]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=self.dir)
        self.assertEqual(r.returncode, 2,
                         "harness/infra failure must be exit 2, not 1")

    def test_module_name_import_still_works(self):
        self._write("impl.py", IMPL_OK)
        cmd = [sys.executable, DIFF_TEST,
               "--gen", "gen", "--model", "model", "--impl", "impl",
               "--n", "20", "--seed", "1", "--ledger", self.ledger]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=self.dir)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_inputs_archived_for_reproduction(self):
        self._run(IMPL_BUGGY, n=50)
        archive = os.path.join(self.dir, "inputs.jsonl")
        # harness records divergent inputs next to the ledger
        candidate = self.ledger.replace(".tsv", ".inputs.jsonl")
        self.assertTrue(os.path.exists(archive) or os.path.exists(candidate),
                        "divergent inputs must be archived for reproduction")


if __name__ == "__main__":
    unittest.main(verbosity=2)
