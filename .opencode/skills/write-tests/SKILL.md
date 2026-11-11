---
name: write-tests
description: Guide for writing tests in this repository. The spec-implementer MUST invoke this skill every time it writes tests. Covers Red/Green TDD, happy-path and edge-case coverage, and behaviour-first testing.
---

# Write Tests

This skill is the mandatory guide for writing tests in the Tessela codebase.
**Invoke it every time you write, extend, or modify tests.** It applies to tests
for any feature, bug fix, or refactor, in every phase of the Red/Green TDD loop.

Tests should be written **before** the code that makes them pass when practical,
and features should be verified against the actual behaviour (see
`SPECS/TECH.md`, the spec, and `README.md`).

---

## 1. Red/Green TDD — the loop

Follow this order strictly. Do not skip ahead.

1. **RED — write a failing test first.** Write a test that expresses the desired
   behaviour. Run it and confirm it **fails for the right reason** (the behaviour
   does not exist yet), not because of a typo, an import error, or a broken
   fixture. The failure should be about the missing/incorrect behaviour.
2. **GREEN — make it pass.** Write the smallest amount of code needed to make the
   test pass. No speculative features, no premature abstraction (YAGNI).
3. **REFACTOR — clean up.** Improve the code you just wrote and its tests while
   keeping the suite green. Run the full checks afterwards.

Rules:

- Never write the implementation before the test for it. If you find yourself
  reaching for production code first, stop and write the test.
- A test whose RED state was never demonstrated is suspect — flag it.
- Run tests using the project's actual commands (consult README/spec), e.g.
  `python -m pytest` if a test suite exists. Do not invent non-existent helper
  scripts like `scripts/test` or `scripts/hooks`.

---

## 2. Cover the happy path

Every feature or fix must have a test proving the **primary, expected success
path** works. The happy-path test is what demonstrates the feature actually does
its job when everything behaves.

- The happy path must assert the **observable outcome**, not just that a function
  was called without error.
- Where the feature has an output contract (a returned value, a persisted
  document, a logged event, a sent message), assert on the real output.

---

## 3. Cover the edge cases

Happy-path coverage alone is not enough. For each piece of behaviour, add tests
for the **edge cases** and **failure modes**. Ask yourself: *what else could
happen, and is it handled correctly?*

Common edge cases to consider (choose the ones that apply to your code):

- **Empty inputs** — empty lists, empty strings, missing optional fields.
- **Boundary values** — minimum/maximum values, off-by-one thresholds, the exact
  value at a limit versus just past it.
- **Malformed / unexpected input** — wrong types, missing required fields,
  extra fields, non-ASCII or special characters (treat external boundaries such
  as raw source files, CSV/TSV rows, SQLite records, OCR output, and AI/model
  responses as untrusted and arbitrary).
- **Errors and fallbacks** — what happens when a dependency fails, a retry is
  exhausted, a query/file read returns nothing, or a fallback is used. Assert
  the degraded/diagnosable behaviour, not just that "no exception propagates"
  (unless that is the contract).
- **Idempotency** — running the same operation twice produces the same result
  where applicable.
- **Isolation / scoping** — where data is per-verse/book/tradition/pipeline
  stage, assert records do not leak or misalign across entities/stages.
- **State transitions** — first vs. later runs, resumed processing, stage
  boundaries, and boundary values.

For each edge case you identify, decide whether it is:
- **Covered** — add a test that asserts the correct behaviour, or
- **Explicitly out of scope** — note it, and why (it cannot occur, or YAGNI).

Do not leave edge cases unexamined.

---

## 4. Test behaviour, not implementation

Prefer tests that assert **what the code does** (its externally observable
behaviour and outcomes) over tests that assert **how it does it** (internal
implementation details). This keeps tests resilient to refactoring and honest
about what actually works.

Prefer asserting:

- The **return value / output** (a structured result, string, list, or model).
- The **side effect that matters** (rows/files/SQLite records written, stage DB
  outputs produced, logs emitted, or external calls handled as specified).
- The **resulting state** (counts, normalized propositions, comparison flags, or
  persisted stage data).
- The **failure behaviour** (an exception raised, a fallback delivered, a
  CRITICAL log fired).

Avoid asserting:

- **Internal call sequences** that are incidental — e.g. that a specific private
  method was called in a specific order, unless that ordering is the contract.
- **Tight coupling to a particular implementation** (a specific internal helper,
  a mock's internal wiring) where a behavioural assertion is possible.

Mocks and test doubles are appropriate for non-deterministic or expensive
external calls (e.g. Gemini API responses) to make behaviour observable and
deterministic. When a real dependency is cheap and deterministic (local SQLite,
fixture files), prefer it so the test exercises real behaviour. Organize tests
clearly if/when a `tests/` suite is introduced, following any conventions in the
spec or README.

---

## 5. Naming and structure

- Name tests to describe the **behaviour** they verify, e.g.
  `test_normalize_verse_returns_expected_atomic_propositions`, not
  `test_function`.
- Group related tests sensibly; a new behaviour gets a new test, not an overloaded
  "kitchen sink" test.
- Keep each test focused on one behaviour. If a test asserts many unrelated
  things, split it.
- Do **not** remove existing tests unless they are replaced by a better, more
  comprehensive test covering the same behaviour plus additional cases. Redundant
  tests are harmless; missing tests are dangerous.

---

## 6. Category lock-in (bug-fixing tests)

When you write tests for a bug fix, in addition to the reported instance, add
tests that lock in the **category** and the **prevention mechanism** (see the
`feature-specification` skill's "Root cause, category & prevention" guidance):

- At least one test per **sibling instance** found in the sweep.
- A test asserting the **prevention mechanism actually fires** (the fail-loud
  log, the rejected input, or the guard/check that blocks the regression).
- An **isolation/alignment** test when the bug involves data leaking or being
  misaligned across verses, books, traditions, or pipeline stages.

This ensures the class of bug cannot silently recur, not just the one instance.
