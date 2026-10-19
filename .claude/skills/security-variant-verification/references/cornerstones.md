# The four cornerstones — provenance notes

Every figure below is a **claim** with a data-generating mechanism, per the
skill's own citation discipline. `Status` says whether the citation has been
re-verified against the primary source; re-verify anything marked
`unverified` before quoting it externally.

## Cornerstone 1: Variant hunting (Google Project Zero)

- Source: Project Zero public methodology and blog posts on in-the-wild 0-day
  variant analysis (2022).
- Claim (mechanism: observation of in-the-wild 0-day samples): roughly **50%**
  of in-the-wild 0-days in 2022 H1 were variants of previously patched bugs.
  Status: widely reported via Project Zero's 2022 mid-year reviews — re-check
  the exact half and sample definition before external citation.
- Case claim (mechanism: one campaign report): a hunt seeded from Arm Mali bugs
  (e.g. CVE-2021-39793 / CVE-2022-22706) surfaced **5** additional exploitable
  vulnerabilities in **3 weeks**. Status: unverified — confirm against the
  specific Project Zero issue tracker write-up before citing.
- Operating rule (robust regardless of figures): extract the abstract
  "invariant violated" pattern, never function names or literals; search the
  target for isomorphic sites.

## Cornerstone 2: The Cedar pattern (AWS Cedar)

- Structure (publicly described by the Cedar team): production Rust
  implementation + Lean executable model (~1/10 scale) + large-scale nightly
  differential random testing + release gate. The often-quoted scale is on the
  order of **10^8** randomized differential tests per day. Status: unverified
  scale figure — treat as a design target, not a measured constant.
- Canonical property: `forbid_trumps_permit` — a request matching a forbid
  policy is always denied.
- SymCert (Amazon Science, reported ~2026): 5 SMT-analysis properties given
  sound+complete proofs in Lean at roughly **1 working day/property**, with new
  features costing **4–8 days** via two reusable properties (reducibility,
  interpretability). Status: unverified — confirm paper, authors and numbers
  before external citation.
- Lesson (robust regardless of figures): "prove the whole product" is
  unmaintainable; "small model + binding layer" is maintainable.

## Cornerstone 3: Neuro-symbolic layering (multiple independent experiments)

- MoCQ claim (mechanism: labeled experiment on a **343**-vulnerability set):
  pure LLM → 185 true positives / 182 false positives (false-discovery rate
  **49.6%**); with CodeQL/Joern adjudication on the C/C++ subset → true-positive
  rate 78.3%, false-discovery rate **19.4%**. Status: unverified — locate the
  primary paper before citing these numbers externally.
- Architecture (robust regardless of figures): LLM = candidate generation and
  pattern abstraction (judgment-intensive); deterministic tools = verdicts
  (auditable).

## Cornerstone 4: Differential random testing as the binding layer

- Principle: a formal proof holds of the model, not the implementation. Feed
  the same inputs to both and compare outputs.
- Enforcement: "no findings, no release" gives the test its gate status;
  exit-code semantics are implemented by `scripts/diff_test.py` (0 clean /
  1 findings / 2 infrastructure error).
- Trust chain: model kernel → differential testing → implementation. Each layer
  is the "introduced element" completing the previous one (substance-field
  completion, in TRIZ terms — applied before the fact, not as decoration).
